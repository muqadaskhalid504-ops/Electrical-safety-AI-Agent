 ```python
import streamlit as st
from groq import Groq
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Electrical Safety AI Agent",
    page_icon="⚡",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666666;
    margin-bottom: 25px;
}

.warning-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #fff3cd;
    border: 1px solid #ffecb5;
    margin-bottom: 25px;
}

.example-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f5f7fa;
    border: 1px solid #dddddd;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    '<div class="main-title">⚡ Electrical Safety AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered assistant for identifying electrical safety risks'
    '</div>',
    unsafe_allow_html=True
)

# ---------------- SAFETY NOTICE ----------------
st.markdown("""
<div class="warning-box">
<b>⚠️ Safety Notice</b><br>
This AI assistant provides general safety information only.
It does not replace a qualified electrician or emergency service.
Never touch exposed or live electrical components.
</div>
""", unsafe_allow_html=True)

# ---------------- API ----------------
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# ---------------- LOAD KNOWLEDGE BASE ----------------
@st.cache_data
def load_knowledge_base():

    with open(
        "knowledge_base/safety_knowledge.txt",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


knowledge_base = load_knowledge_base()


# ---------------- SIMPLE RAG RETRIEVAL ----------------
def retrieve_relevant_information(user_question, knowledge):

    # Convert text into sections
    sections = re.split(r"\n(?=\d+\.)", knowledge)

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            user_question.lower()
        )
    )

    scored_sections = []

    for section in sections:

        section_lower = section.lower()

        score = 0

        for word in question_words:

            if word in section_lower:
                score += 1

        scored_sections.append(
            (score, section)
        )

    # Sort by relevance
    scored_sections.sort(
        key=lambda x: x[0],
        reverse=True
    )

    # Select top relevant sections
    relevant_sections = [
        section
        for score, section in scored_sections[:3]
        if score > 0
    ]

    # If no exact match, provide general safety knowledge
    if not relevant_sections:
        relevant_sections = [
            knowledge[:5000]
        ]

    return "\n\n".join(relevant_sections)


# ---------------- AI SYSTEM PROMPT ----------------
system_prompt = """
You are an Electrical Safety AI Agent.

Your purpose is to help users understand possible electrical safety
hazards using the provided safety knowledge.

IMPORTANT:

The information retrieved from the knowledge base is the primary
reference for safety guidance.

Do not invent safety facts when relevant information is available
in the knowledge base.

Follow this decision process:

STEP 1 — Understand the situation
Identify what electrical equipment, condition, or problem the user
is describing.

STEP 2 — Identify hazards
Identify possible hazards such as:
- Electric shock
- Short circuit
- Overheating
- Fire
- Arc/sparking
- Damaged insulation
- Overloading
- Loose connection
- Exposed live parts

STEP 3 — Determine risk level
Choose exactly ONE:
- Low
- Medium
- High
- Emergency

Use Emergency when there is an immediate threat such as:
- Electric shock
- Active fire
- Smoke from electrical equipment
- Exposed live electrical parts
- Major sparking or arcing
- Severe burning smell with overheating

STEP 4 — Recommend safe action
Give only actions that do not require the user to work on live
electrical equipment.

STEP 5 — Professional help
Clearly state when a qualified electrician should inspect the problem.

IMPORTANT SAFETY RULES:

- Never tell the user to touch live wires.
- Never tell the user to open energized equipment.
- Never tell the user to bypass a fuse, breaker, RCD, or other
  protection device.
- Never encourage dangerous electrical experiments.
- Never provide instructions for working on energized equipment.
- Do not pretend to physically inspect equipment.
- If uncertain, prioritize safety and recommend professional help.

If the user asks how to repair, modify, open, rewire, or troubleshoot
live electrical equipment, do not provide step-by-step instructions
for performing the dangerous work.

Instead, explain the hazard and recommend a qualified electrician.

For emergency situations, clearly tell the user to move away from
the danger and seek appropriate emergency/professional help.

Use this response format:

⚠️ Possible Hazard:
...

🔴 Risk Level:
Low / Medium / High / Emergency

📖 Why It Is Dangerous:
...

🛡️ Safety Precautions:
...

👷 Professional Help:
...

🚨 Emergency Warning:
...

At the end, add:

📚 Knowledge Source:
Electrical Safety Knowledge Base
"""


# ---------------- EXAMPLES ----------------
st.subheader("💡 Example Problems")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="example-box">
    🔥 Burning smell from socket
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="example-box">
    ⚡ Electric shock from appliance
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="example-box">
    🔌 Circuit breaker keeps tripping
    </div>
    """, unsafe_allow_html=True)


# ---------------- USER INPUT ----------------
st.subheader("🔍 Describe Your Electrical Problem")

user_problem = st.text_area(
    "Enter your problem below:",
    placeholder=(
        "Example: My electrical socket is making a buzzing "
        "sound and becoming hot."
    ),
    height=150
)


# ---------------- ANALYZE BUTTON ----------------
if st.button("🔍 Analyze Safety Risk", type="primary"):

    if not user_problem.strip():

        st.warning(
            "Please describe an electrical problem first."
        )

    else:

        with st.spinner(
            "⚡ Retrieving safety information and analyzing risk..."
        ):

            try:

                # Retrieve relevant knowledge
                relevant_information = retrieve_relevant_information(
                    user_problem,
                    knowledge_base
                )

                # Send retrieved knowledge + user problem to AI
                user_message = f"""
USER'S ELECTRICAL PROBLEM:

{user_problem}

RETRIEVED SAFETY KNOWLEDGE:

{relevant_information}

Use the retrieved safety knowledge to analyze the user's problem.
"""

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    temperature=0.2
                )

                answer = response.choices[0].message.content

                st.success(
                    "Safety analysis completed using the knowledge base."
                )

                st.subheader("🛡️ Safety Analysis")

                st.markdown(answer)

                # Show retrieved information
                with st.expander(
                    "📚 View Retrieved Safety Information"
                ):

                    st.write(relevant_information)

            except Exception as e:

                st.error(
                    "An error occurred while analyzing the problem."
                )

                st.write(str(e))


# ---------------- FOOTER ----------------
st.divider()

st.caption(
    "⚡ Electrical Safety AI Agent | Hackathon Project | "
    "RAG-based safety guidance"
)
```
