import streamlit as st
from groq import Groq
import re

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Electrical Safety AI Agent",
    page_icon="⚡",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

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
    text-align: center;
}

.dashboard-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f5f7fa;
    border: 1px solid #dddddd;
    text-align: center;
    min-height: 120px;
}

.dashboard-title {
    font-size: 16px;
    color: #666666;
}

.dashboard-value {
    font-size: 24px;
    font-weight: bold;
    margin-top: 10px;
}

.risk-low {
    padding: 20px;
    border-radius: 12px;
    background-color: #d4edda;
    border: 2px solid #28a745;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}

.risk-medium {
    padding: 20px;
    border-radius: 12px;
    background-color: #fff3cd;
    border: 2px solid #ffc107;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}

.risk-high {
    padding: 20px;
    border-radius: 12px;
    background-color: #f8d7da;
    border: 2px solid #dc3545;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
}

.risk-emergency {
    padding: 20px;
    border-radius: 12px;
    background-color: #f5c6cb;
    border: 3px solid #b30000;
    text-align: center;
    font-size: 26px;
    font-weight: bold;
}

.recommendation-box {
    padding: 20px;
    border-radius: 12px;
    background-color: #eef6ff;
    border: 1px solid #b8daff;
    margin-top: 20px;
}

.workflow-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #f8f9fa;
    border: 1px solid #dddddd;
    min-height: 180px;
}

.workflow-number {
    font-size: 28px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("💬 Analysis History")

    if st.session_state.history:

        for i, item in enumerate(
            reversed(st.session_state.history),
            1
        ):

            st.markdown(
                f"**{i}. {item['category']}**"
            )

            st.caption(
                item["problem"]
            )

            st.caption(
                f"Risk: {item['risk']}"
            )

            st.divider()

    else:

        st.info(
            "No analysis history yet."
        )

    if st.button(
        "🧹 Clear History",
        use_container_width=True
    ):

        st.session_state.history = []

        st.rerun()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

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

# --------------------------------------------------
# SAFETY NOTICE
# --------------------------------------------------

st.markdown("""
<div class="warning-box">
<b>⚠️ Safety Notice</b><br>
This AI assistant provides general safety information only.
It does not replace a qualified electrician or emergency service.
Never touch exposed or live electrical components.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# GROQ
# --------------------------------------------------

api_key = st.secrets["GROQ_API_KEY"]

client = Groq(
    api_key=api_key
)

# --------------------------------------------------
# KNOWLEDGE BASE
# --------------------------------------------------

@st.cache_data
def load_knowledge_base():

    with open(
        "knowledge_base/safety_knowledge.txt",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


knowledge_base = load_knowledge_base()

# --------------------------------------------------
# RAG RETRIEVAL
# --------------------------------------------------

def retrieve_relevant_information(
    user_question,
    knowledge
):

    sections = re.split(
        r"\n(?=\d+\.)",
        knowledge
    )

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

    scored_sections.sort(
        key=lambda x: x[0],
        reverse=True
    )

    relevant_sections = [
        section
        for score, section in scored_sections[:3]
        if score > 0
    ]

    if not relevant_sections:

        relevant_sections = [
            knowledge[:5000]
        ]

    return "\n\n".join(
        relevant_sections
    )

# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

system_prompt = """
You are an Electrical Safety AI Agent.

Use the retrieved Electrical Safety Knowledge Base to provide
safe, beginner-friendly guidance.

For every problem:

1. Understand the electrical situation.
2. Consider the selected problem category.
3. Identify possible hazards.
4. Determine ONE risk level:
   Low, Medium, High, or Emergency.
5. Explain why the situation is dangerous.
6. Provide safe precautions.
7. Explain when a qualified electrician is needed.

Emergency situations include:

- Electric shock
- Active electrical fire
- Smoke from electrical equipment
- Exposed live electrical parts
- Major sparking or arcing
- Severe burning smell with overheating

IMPORTANT SAFETY RULES:

- Never tell users to touch live wires.
- Never tell users to open energized equipment.
- Never tell users to bypass breakers, fuses, RCDs, or protection devices.
- Never encourage dangerous electrical experiments.
- Never provide step-by-step instructions for working on energized equipment.
- Do not pretend to physically inspect equipment.
- If uncertain, prioritize safety and professional assistance.

For emergency situations, tell the user to move away from the danger
and seek appropriate emergency/professional help.

IMPORTANT OUTPUT RULE:

Always write the risk level exactly in this format:

Risk Level: Low

OR

Risk Level: Medium

OR

Risk Level: High

OR

Risk Level: Emergency

Then provide:

⚠️ Possible Hazard:
...

📖 Why It Is Dangerous:
...

🛡️ Safety Precautions:
...

👷 Professional Help:
...

🚨 Emergency Warning:
...

📚 Knowledge Source:
Electrical Safety Knowledge Base
"""

# --------------------------------------------------
# CATEGORY
# --------------------------------------------------

st.subheader("📂 Select Problem Category")

category = st.selectbox(
    "What type of electrical problem are you experiencing?",
    [
        "🔌 Socket / Wiring",
        "⚡ Electric Shock",
        "🔥 Fire / Smoke",
        "🔧 Electrical Appliance",
        "🔴 Circuit Breaker",
        "💡 Other"
    ]
)

# --------------------------------------------------
# EXAMPLES
# --------------------------------------------------

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

# --------------------------------------------------
# USER PROBLEM
# --------------------------------------------------

st.subheader("🔍 Describe Your Electrical Problem")

user_problem = st.text_area(
    "Enter your problem below:",
    placeholder=(
        "Example: My electrical socket is making a buzzing "
        "sound and becoming hot."
    ),
    height=150
)

# --------------------------------------------------
# ANALYZE
# --------------------------------------------------

if st.button(
    "🔍 Analyze Safety Risk",
    type="primary"
):

    if not user_problem.strip():

        st.warning(
            "Please describe an electrical problem first."
        )

    else:

        with st.spinner(
            "⚡ Retrieving safety information and analyzing risk..."
        ):

            try:

                # ------------------------------------------
                # RETRIEVE KNOWLEDGE
                # ------------------------------------------

                relevant_information = (
                    retrieve_relevant_information(
                        user_problem,
                        knowledge_base
                    )
                )

                # ------------------------------------------
                # USER MESSAGE
                # ------------------------------------------

                user_message = f"""
PROBLEM CATEGORY:

{category}

USER'S ELECTRICAL PROBLEM:

{user_problem}

RETRIEVED SAFETY KNOWLEDGE:

{relevant_information}

Analyze the problem using the selected category
and retrieved safety knowledge.
"""

                # ------------------------------------------
                # AI RESPONSE
                # ------------------------------------------

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

                answer = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                # ------------------------------------------
                # RISK DETECTION
                # ------------------------------------------

                risk_match = re.search(
                    r"Risk Level:\s*(Low|Medium|High|Emergency)",
                    answer,
                    re.IGNORECASE
                )

                if risk_match:

                    risk_level = (
                        risk_match
                        .group(1)
                        .capitalize()
                    )

                else:

                    risk_level = "Unknown"

                # ------------------------------------------
                # SAVE HISTORY
                # ------------------------------------------

                st.session_state.history.append(
                    {
                        "category": category,
                        "problem": user_problem,
                        "risk": risk_level
                    }
                )

                # ------------------------------------------
                # SAFETY DASHBOARD
                # ------------------------------------------

                st.subheader(
                    "📊 Safety Summary Dashboard"
                )

                dashboard_col1, dashboard_col2, dashboard_col3 = st.columns(3)

                with dashboard_col1:

                    st.markdown(
                        f"""
                        <div class="dashboard-card">
                        <div class="dashboard-title">
                        🚦 Risk Level
                        </div>
                        <div class="dashboard-value">
                        {risk_level}
                        </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with dashboard_col2:

                    st.markdown(
                        f"""
                        <div class="dashboard-card">
                        <div class="dashboard-title">
                        📂 Category
                        </div>
                        <div class="dashboard-value">
                        {category}
                        </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with dashboard_col3:

                    st.markdown(
                        """
                        <div class="dashboard-card">
                        <div class="dashboard-title">
                        📚 Knowledge
                        </div>
                        <div class="dashboard-value">
                        RAG Used
                        </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # ------------------------------------------
                # RISK DISPLAY
                # ------------------------------------------

                st.subheader(
                    "🚦 Detailed Risk Level"
                )

                if risk_level == "Low":

                    st.markdown(
                        """
                        <div class="risk-low">
                        🟢 LOW RISK
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                elif risk_level == "Medium":

                    st.markdown(
                        """
                        <div class="risk-medium">
                        🟡 MEDIUM RISK
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                elif risk_level == "High":

                    st.markdown(
                        """
                        <div class="risk-high">
                        🔴 HIGH RISK
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                elif risk_level == "Emergency":

                    st.markdown(
                        """
                        <div class="risk-emergency">
                        🚨 EMERGENCY
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.warning(
                        "Risk level could not be determined."
                    )

                # ------------------------------------------
                # SAFETY RECOMMENDATION
                # ------------------------------------------

                st.markdown("""
                <div class="recommendation-box">
                <b>🛡️ Safety Recommendation</b><br>
                Follow the safety precautions provided by the AI.
                Do not touch exposed or energized electrical parts.
                If the situation involves shock, fire, smoke,
                major sparking, or exposed live parts, move away
                from the danger and seek appropriate professional
                or emergency assistance.
                </div>
                """, unsafe_allow_html=True)

                # ------------------------------------------
                # AI ANALYSIS
                # ------------------------------------------

                st.subheader(
                    "🧠 AI Safety Analysis"
                )

                st.markdown(answer)

                # ------------------------------------------
                # KNOWLEDGE
                # ------------------------------------------

                with st.expander(
                    "📚 View Retrieved Safety Information"
                ):

                    st.write(
                        relevant_information
                    )

            except Exception as e:

                st.error(
                    "An error occurred while analyzing the problem."
                )

                st.write(str(e))

# --------------------------------------------------
# HOW IT WORKS
# --------------------------------------------------

st.divider()

st.subheader("⚙️ How It Works")

flow_col1, flow_col2, flow_col3 = st.columns(3)

with flow_col1:

    st.markdown("""
    <div class="workflow-box">

    <div class="workflow-number">
    1️⃣
    </div>

    <h3>User Input</h3>

    The user describes an electrical problem
    and selects a problem category.

    </div>
    """, unsafe_allow_html=True)

with flow_col2:

    st.markdown("""
    <div class="workflow-box">

    <div class="workflow-number">
    2️⃣
    </div>

    <h3>RAG Knowledge</h3>

    The system retrieves relevant information
    from the Electrical Safety Knowledge Base.

    </div>
    """, unsafe_allow_html=True)

with flow_col3:

    st.markdown("""
    <div class="workflow-box">

    <div class="workflow-number">
    3️⃣
    </div>

    <h3>AI Analysis</h3>

    The AI Agent analyzes the situation
    and identifies possible safety risks.

    </div>
    """, unsafe_allow_html=True)

flow_col4, flow_col5, flow_col6 = st.columns(3)

with flow_col4:

    st.markdown("""
    <div class="workflow-box">

    <div class="workflow-number">
    4️⃣
    </div>

    <h3>Risk Detection</h3>

    The system classifies the situation as
    Low, Medium, High, or Emergency.

    </div>
    """, unsafe_allow_html=True)

with flow_col5:

    st.markdown("""
    <div class="workflow-box">

    <div class="workflow-number">
    5️⃣
    </div>

    <h3>Safety Guidance</h3>

    The AI provides precautions and explains
    when professional help is required.

    </div>
    """, unsafe_allow_html=True)

with flow_col6:

    st.markdown("""
    <div class="workflow-box">

    <div class="workflow-number">
    6️⃣
    </div>

    <h3>Safety Decision</h3>

    The user receives clear safety-focused
    guidance based on the identified risk.

    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "⚡ Electrical Safety AI Agent | Hackathon Project | "
    "RAG-based safety guidance"
)
