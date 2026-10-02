import streamlit as st
from groq import Groq
import re

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Electrical Safety AI Agent",
    page_icon="⚡",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================

if "history" not in st.session_state:
    st.session_state.history = []

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}

.warning-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #fff3cd;
    border-left: 6px solid #ffc107;
    margin-bottom: 20px;
}

.example-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #f1f8ff;
    border-left: 6px solid #2196f3;
    margin-top: 10px;
    margin-bottom: 20px;
}

.dashboard {
    padding: 20px;
    border-radius: 12px;
    background-color: #f7f7f7;
    margin-top: 20px;
    margin-bottom: 20px;
}

.risk-card {
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin: 15px 0;
}

.recommendation {
    padding: 18px;
    border-radius: 10px;
    background-color: #e8f5e9;
    border-left: 6px solid #4caf50;
    margin-top: 15px;
}

.workflow-step {
    padding: 15px;
    border-radius: 10px;
    background-color: #f5f5f5;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.header("💬 Analysis History")

    if st.session_state.history:

        for i, item in enumerate(
            reversed(st.session_state.history),
            start=1
        ):
            st.markdown(
                f"""
                **{i}. {item['category']}**

                Risk: **{item['risk']}**

                {item['problem'][:80]}...
                """
            )

    else:
        st.info("No analysis yet.")

    st.divider()

    if st.button(
        "🧹 Clear History",
        use_container_width=True
    ):
        st.session_state.history = []
        st.rerun()

# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-title">⚡ Electrical Safety AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered electrical hazard analysis and safety guidance</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="warning-box">
    ⚠️ <b>Safety Notice:</b>
    This application provides educational safety guidance.
    It does not replace a qualified electrician, electrical engineer,
    professional inspection, or emergency services.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# GROQ CLIENT
# =========================

try:

    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )

except Exception as e:

    st.error(
        "Groq API key is missing or incorrectly configured."
    )

    st.stop()

# =========================
# LOAD KNOWLEDGE BASE
# =========================

@st.cache_data
def load_knowledge():

    try:

        with open(
            "knowledge_base/safety_knowledge.txt",
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception:

        return ""


knowledge = load_knowledge()

# =========================
# RAG RETRIEVAL
# =========================

def retrieve_knowledge(
    user_question,
    knowledge_text,
    top_k=3
):

    if not knowledge_text:
        return "No safety knowledge was retrieved."

    sections = re.split(
        r"\n(?=\d+\.)",
        knowledge_text
    )

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            user_question.lower()
        )
    )

    scored_sections = []

    for section in sections:

        section_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                section.lower()
            )
        )

        score = len(
            question_words.intersection(
                section_words
            )
        )

        scored_sections.append(
            (score, section)
        )

    scored_sections.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = [
        section
        for score, section in scored_sections[:top_k]
        if score > 0
    ]

    if not selected:

        return knowledge_text[:5000]

    return "\n\n".join(selected)

# =========================
# SAFETY SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are an Electrical Safety AI Agent.

Your job is to analyze electrical problems and provide
safe, conservative and educational safety guidance.

IMPORTANT SAFETY RULES:

1. Never tell the user to touch live electrical wires.
2. Never tell the user to open energized equipment.
3. Never tell the user to bypass a circuit breaker or fuse.
4. Never provide dangerous electrical repair instructions.
5. Encourage professional help when the situation is dangerous.
6. For electric shock, active fire, smoke, major sparking,
   exposed live parts, or severe overheating, treat the
   situation as HIGH or EMERGENCY depending on severity.
7. Always prioritize human safety.

Your response MUST use this structure:

⚠️ Possible Hazard:
[hazard]

🔴 Risk Level: [Low / Medium / High / Emergency]

📖 Why It Is Dangerous:
[explanation]

🛡️ Safety Precautions:
[safety precautions]

👷 Professional Help:
[when professional help is needed]

🚨 Emergency Warning:
[emergency guidance if applicable]

Do not encourage dangerous DIY electrical work.
"""

# =========================
# USER INPUT
# =========================

st.subheader("🔍 Analyze an Electrical Problem")

category = st.selectbox(
    "📂 Select Problem Category",
    [
        "🔌 Socket / Wiring",
        "⚡ Electric Shock",
        "🔥 Fire / Smoke",
        "🔧 Electrical Appliance",
        "🔴 Circuit Breaker",
        "💡 Other"
    ]
)

st.markdown(
    """
    <div class="example-box">
    <b>💡 Example:</b>
    Describe the electrical problem in simple words.
    </div>
    """,
    unsafe_allow_html=True
)

user_problem = st.text_area(
    "Describe your electrical problem:",
    placeholder=(
        "Example: My electrical socket is getting warm "
        "and I can smell something burning."
    ),
    height=150
)

# =========================
# ANALYZE BUTTON
# =========================

analyze_button = st.button(
    "🔍 Analyze Safety Risk",
    type="primary",
    use_container_width=True
)

# =========================
# AI ANALYSIS
# =========================

if analyze_button:

    if not user_problem.strip():

        st.warning(
            "Please describe your electrical problem first."
        )

        st.stop()

    # Retrieve RAG knowledge
    retrieved_knowledge = retrieve_knowledge(
        user_problem,
        knowledge
    )

    # AI prompt
    user_prompt = f"""
Problem Category:
{category}

User's Electrical Problem:
{user_problem}

Relevant Electrical Safety Knowledge:
{retrieved_knowledge}

Analyze this situation according to the safety rules.

IMPORTANT:
Clearly write the risk level in exactly this format:

🔴 Risk Level: Low

or

🔴 Risk Level: Medium

or

🔴 Risk Level: High

or

🔴 Risk Level: Emergency

Choose only ONE risk level.
"""

    try:

        with st.spinner(
            "⚡ AI is analyzing the electrical safety risk..."
        ):

            response = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],

                temperature=0.2
            )

        answer = response.choices[0].message.content

        # =========================
        # RISK LEVEL DETECTION
        # =========================

        risk_match = re.search(
            r"Risk\s*Level\s*[:\-]?\s*(?:🔴\s*)?"
            r"(Low|Medium|High|Emergency)",
            answer,
            re.IGNORECASE
        )

        if risk_match:

            risk = risk_match.group(1).capitalize()

        else:

            # Backup detection
            answer_lower = answer.lower()

            if "emergency" in answer_lower:

                risk = "Emergency"

            elif "high risk" in answer_lower:

                risk = "High"

            elif "medium risk" in answer_lower:

                risk = "Medium"

            elif "low risk" in answer_lower:

                risk = "Low"

            else:

                risk = "Unknown"

        # =========================
        # SAVE HISTORY
        # =========================

        st.session_state.history.append(
            {
                "category": category,
                "problem": user_problem,
                "risk": risk
            }
        )

        # =========================
        # SAVE LAST ANALYSIS
        # =========================

        st.session_state.last_analysis = {
            "category": category,
            "problem": user_problem,
            "risk": risk,
            "answer": answer
        }

        # =========================
        # SAFETY SUMMARY
        # =========================

        st.markdown(
            "## 📊 Safety Summary Dashboard"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🚦 Risk Level",
                risk
            )

        with col2:

            st.metric(
                "📂 Category",
                category
            )

        with col3:

            st.metric(
                "📚 Knowledge",
                "RAG Used"
            )

        # =========================
        # RISK CARD
        # =========================

        if risk == "Low":

            risk_color = "#d4edda"
            risk_message = "🟢 Low Risk"

        elif risk == "Medium":

            risk_color = "#fff3cd"
            risk_message = "🟡 Medium Risk"

        elif risk == "High":

            risk_color = "#f8d7da"
            risk_message = "🔴 High Risk"

        elif risk == "Emergency":

            risk_color = "#ffcccc"
            risk_message = "🚨 EMERGENCY"

        else:

            risk_color = "#eeeeee"
            risk_message = "⚪ Risk Level Unknown"

        st.markdown(
            f"""
            <div class="risk-card"
            style="background-color:{risk_color};">
            {risk_message}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =========================
        # RECOMMENDATION
        # =========================

        if risk in ["High", "Emergency"]:

            recommendation = """
            🚨 **Immediate Safety Attention Required**

            Move away from the electrical hazard and avoid
            touching electrical equipment or exposed wires.

            Contact a qualified electrician or appropriate
            emergency services when necessary.
            """

        elif risk == "Medium":

            recommendation = """
            ⚠️ **Caution Required**

            Avoid using the affected electrical equipment
            until it can be safely inspected by a qualified
            professional.
            """

        elif risk == "Low":

            recommendation = """
            ✅ **General Safety Guidance**

            Continue to follow basic electrical safety
            practices and monitor the situation.
            """

        else:

            recommendation = """
            ⚠️ **Safety Caution**

            The system could not determine a clear risk level.
            Follow basic electrical safety precautions and
            consult a qualified professional.
            """

        st.markdown(
            f"""
            <div class="recommendation">
            {recommendation}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =========================
        # AI RESPONSE
        # =========================

        st.markdown("## 🤖 AI Safety Analysis")

        st.markdown(answer)

        # =========================
        # DOWNLOAD REPORT
        # =========================

        report = f"""
ELECTRICAL SAFETY AI AGENT
Safety Analysis Report
========================================

Problem Category:
{category}

User's Electrical Problem:
{user_problem}

Risk Level:
{risk}

========================================
AI SAFETY ANALYSIS
========================================

{answer}

========================================
Safety Notice:
This report provides educational safety guidance.
It does not replace professional electrical inspection,
diagnosis, or emergency services.

For electric shock, fire, smoke, major sparking,
or exposed live parts, move to a safe location
and contact appropriate emergency services or
a qualified electrical professional.

========================================
Generated by Electrical Safety AI Agent
========================================
"""

        st.download_button(
            label="📄 Download Safety Report",
            data=report,
            file_name="electrical_safety_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        # =========================
        # RAG KNOWLEDGE
        # =========================

        with st.expander(
            "📚 View Retrieved RAG Knowledge"
        ):

            st.write(
                retrieved_knowledge
            )

    except Exception as e:

        st.error(
            f"AI analysis failed: {str(e)}"
        )

# =========================
# HOW IT WORKS
# =========================

st.divider()

st.subheader("⚙️ How It Works")

steps = [
    ("1️⃣", "User Input",
     "User describes an electrical problem."),

    ("2️⃣", "RAG Knowledge",
     "Relevant electrical safety information is retrieved."),

    ("3️⃣", "AI Analysis",
     "The AI agent analyzes the problem."),

    ("4️⃣", "Risk Detection",
     "The system identifies the safety risk level."),

    ("5️⃣", "Safety Guidance",
     "The AI provides safety precautions."),

    ("6️⃣", "Safety Decision",
     "The user is guided toward safe action or professional help.")
]

for icon, title, description in steps:

    st.markdown(
        f"""
        <div class="workflow-step">
        <b>{icon} {title}</b><br>
        {description}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# SOURCES
# =========================

st.divider()

st.subheader("📚 Sources & References")

st.markdown("""
- OSHA — Electrical Safety Guidance
- HSE — Electrical Safety Guidance
- General electrical safety and hazard-prevention practices
""")

st.markdown(
    """
    **RAG Process:**

    User Problem → Retrieve Relevant Safety Knowledge
    → AI Analysis → Risk Level → Safety Guidance
    """
)

# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "⚡ Electrical Safety AI Agent | Hackathon Project | "
    "RAG-based safety guidance"
)
