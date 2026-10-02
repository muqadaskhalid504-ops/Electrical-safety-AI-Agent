 import streamlit as st
from groq import Groq
import re

# =========================
# PAGE CONFIGURATION
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
    font-weight: 700;
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
    padding: 12px;
    border-radius: 8px;
    background-color: #f5f5f5;
    margin-bottom: 10px;
}

.dashboard-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f8f9fa;
    text-align: center;
    border: 1px solid #ddd;
}

.dashboard-title {
    font-size: 15px;
    color: #666;
}

.dashboard-value {
    font-size: 22px;
    font-weight: bold;
    margin-top: 5px;
}

.risk-low {
    padding: 18px;
    border-radius: 12px;
    background-color: #d4edda;
    border-left: 6px solid #28a745;
    margin: 15px 0;
}

.risk-medium {
    padding: 18px;
    border-radius: 12px;
    background-color: #fff3cd;
    border-left: 6px solid #ffc107;
    margin: 15px 0;
}

.risk-high {
    padding: 18px;
    border-radius: 12px;
    background-color: #f8d7da;
    border-left: 6px solid #dc3545;
    margin: 15px 0;
}

.risk-emergency {
    padding: 18px;
    border-radius: 12px;
    background-color: #f5c6cb;
    border-left: 6px solid #b21f2d;
    margin: 15px 0;
}

.recommendation-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #e8f4fd;
    border-left: 5px solid #2196f3;
    margin: 15px 0;
}

.workflow-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    text-align: center;
    min-height: 130px;
}

.workflow-number {
    font-size: 28px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("⚡ Electrical Safety AI")

st.sidebar.markdown("### 💬 Analysis History")

if st.session_state.history:

    for i, item in enumerate(
        reversed(st.session_state.history),
        start=1
    ):
        st.sidebar.markdown(
            f"**{i}. {item['category']}**  \n"
            f"Risk: **{item['risk']}**"
        )

else:
    st.sidebar.info("No analysis history yet.")

if st.session_state.history:

    if st.sidebar.button("🧹 Clear History"):
        st.session_state.history = []
        st.session_state.last_analysis = None
        st.rerun()

# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-title">⚡ Electrical Safety AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered electrical hazard detection and safety guidance'
    '</div>',
    unsafe_allow_html=True
)

# =========================
# SAFETY NOTICE
# =========================

st.markdown("""
<div class="warning-box">

⚠️ <b>Safety Notice:</b><br>
This AI agent provides educational safety guidance.
Never touch live electrical wires, open energized equipment,
bypass circuit protection, or attempt dangerous electrical repairs.

For serious electrical hazards, contact a qualified electrician
or appropriate emergency services.

</div>
""", unsafe_allow_html=True)

# =========================
# GROQ API
# =========================

try:

    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )

except Exception:

    st.error(
        "GROQ_API_KEY is missing. Please add it in Streamlit Secrets."
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
# SIMPLE RAG RETRIEVAL
# =========================

def retrieve_knowledge(user_question):

    if not knowledge:

        return "No knowledge base available."

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

        section_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                section.lower()
            )
        )

        score = len(
            question_words.intersection(section_words)
        )

        scored_sections.append(
            (score, section)
        )

    scored_sections.sort(
        key=lambda x: x[0],
        reverse=True
    )

    top_sections = [
        section
        for score, section in scored_sections[:3]
        if score > 0
    ]

    if top_sections:

        return "\n\n".join(top_sections)

    return knowledge[:5000]

# =========================
# AI SAFETY SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are an Electrical Safety AI Agent.

Your primary purpose is to identify electrical hazards
and provide safe educational guidance.

Follow this decision process:

1. Understand the user's electrical problem.
2. Identify possible hazards.
3. Consider:
   - Electric shock
   - Short circuit
   - Overheating
   - Electrical fire
   - Sparks or arcing
   - Damaged insulation
   - Overloading
   - Loose connections
   - Exposed live parts

4. Select exactly ONE risk level:
   Low
   Medium
   High
   Emergency

Risk guidance:

Low:
Minor issue with no immediate dangerous signs.

Medium:
Potential hazard that requires attention.

High:
Serious electrical hazard where professional help is recommended.

Emergency:
Electric shock, active fire, smoke, major sparking/arcing,
exposed live electrical parts, or severe burning/overheating signs.

IMPORTANT:
The risk level MUST appear exactly in this format:

🔴 Risk Level: Low

OR

🔴 Risk Level: Medium

OR

🔴 Risk Level: High

OR

🔴 Risk Level: Emergency

Always respond using this format:

⚠️ Possible Hazard
🔴 Risk Level: [one risk level]
📖 Why It Is Dangerous
🛡️ Safety Precautions
👷 Professional Help
🚨 Emergency Warning

IMPORTANT SAFETY RULES:

- Never tell the user to touch live wires.
- Never tell the user to open energized equipment.
- Never tell the user to bypass a circuit breaker or fuse.
- Never provide dangerous step-by-step electrical repair instructions.
- Recommend moving away from dangerous equipment when necessary.
- Recommend qualified electrical professionals for serious hazards.
- For fire, smoke, electric shock, major sparks, or exposed live parts,
  prioritize immediate safety and emergency assistance.
- Do not claim certainty when the available information is incomplete.
"""

# =========================
# CATEGORY SELECTION
# =========================

st.subheader("📂 Select Problem Category")

category = st.selectbox(
    "Choose the category that best matches your problem:",
    [
        "🔌 Socket / Wiring",
        "⚡ Electric Shock",
        "🔥 Fire / Smoke",
        "🔧 Electrical Appliance",
        "🔴 Circuit Breaker",
        "💡 Other"
    ]
)

# =========================
# EXAMPLES
# =========================

st.subheader("💡 Example Problems")

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
    <div class="example-box">
    🔌 <b>Socket:</b><br>
    My electrical socket is slightly warm but there is no smoke
    or burning smell.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="example-box">
    🔴 <b>Circuit Breaker:</b><br>
    My circuit breaker keeps tripping repeatedly.
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown("""
    <div class="example-box">
    🔥 <b>Fire / Smoke:</b><br>
    There are sparks and smoke coming from my electrical switch.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="example-box">
    ⚡ <b>Electric Shock:</b><br>
    I received an electric shock from an electrical appliance.
    </div>
    """, unsafe_allow_html=True)

# =========================
# USER INPUT
# =========================

st.subheader("📝 Describe Your Electrical Problem")

user_problem = st.text_area(
    "Enter the problem in simple words:",
    height=130,
    placeholder="Example: My socket is making a buzzing sound and becomes warm."
)

# =========================
# ANALYZE BUTTON
# =========================

if st.button(
    "🔍 Analyze Safety Risk",
    use_container_width=True
):

    if not user_problem.strip():

        st.warning(
            "Please describe your electrical problem first."
        )

    else:

        retrieved_knowledge = retrieve_knowledge(
            user_problem
        )

        user_prompt = f"""
Problem Category:
{category}

User's Electrical Problem:
{user_problem}

Relevant Safety Knowledge:
{retrieved_knowledge}

Analyze this problem using the safety rules.

Give a clear and conservative safety assessment.

IMPORTANT:
Choose exactly ONE risk level from:

Low
Medium
High
Emergency

Write it exactly as:

🔴 Risk Level: Low

or

🔴 Risk Level: Medium

or

🔴 Risk Level: High

or

🔴 Risk Level: Emergency
"""

        # =========================
        # AI ANALYSIS
        # =========================

        try:

            with st.spinner(
                "🤖 AI Safety Agent is analyzing..."
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
            # FIXED RISK DETECTION
            # =========================

            # Normalize the AI response
            clean_answer = answer.replace(
                "**", ""
            ).replace(
                "__", ""
            )

            # First try: exact "Risk Level"
            risk_match = re.search(
                r"Risk\s*Level\s*[:\-]?\s*"
                r"(?:🔴\s*)?"
                r"(Low|Medium|High|Emergency)",
                clean_answer,
                re.IGNORECASE
            )

            if risk_match:

                risk = risk_match.group(1).capitalize()

            else:

                # Second try: Risk Level may be on a
                # separate line or have extra symbols
                risk_match = re.search(
                    r"Risk\s*Level.*?"
                    r"(Low|Medium|High|Emergency)",
                    clean_answer,
                    re.IGNORECASE | re.DOTALL
                )

                if risk_match:

                    risk = risk_match.group(1).capitalize()

                else:

                    # Third backup: search for common
                    # risk phrases in the complete answer
                    answer_lower = clean_answer.lower()

                    if re.search(
                        r"\bemergency\b",
                        answer_lower
                    ):

                        risk = "Emergency"

                    elif re.search(
                        r"\bhigh\s*risk\b",
                        answer_lower
                    ):

                        risk = "High"

                    elif re.search(
                        r"\bmedium\s*risk\b",
                        answer_lower
                    ):

                        risk = "Medium"

                    elif re.search(
                        r"\blow\s*risk\b",
                        answer_lower
                    ):

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

            st.subheader(
                "📊 Safety Summary Dashboard"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.markdown(
                    f"""
                    <div class="dashboard-card">

                    <div class="dashboard-title">
                    🚦 Risk Level
                    </div>

                    <div class="dashboard-value">
                    {risk}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:

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

            with col3:

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

            # =========================
            # RISK CARD
            # =========================

            if risk.lower() == "low":

                st.markdown(
                    """
                    <div class="risk-low">

                    🟢 <b>LOW RISK</b><br>

                    The situation does not appear to show an immediate
                    serious electrical danger based on the information provided.

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif risk.lower() == "medium":

                st.markdown(
                    """
                    <div class="risk-medium">

                    🟡 <b>MEDIUM RISK</b><br>

                    The situation may become dangerous and should receive
                    attention from a qualified person.

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif risk.lower() == "high":

                st.markdown(
                    """
                    <div class="risk-high">

                    🔴 <b>HIGH RISK</b><br>

                    A serious electrical hazard may be present.
                    Avoid unsafe interaction and seek qualified professional help.

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif risk.lower() == "emergency":

                st.markdown(
                    """
                    <div class="risk-emergency">

                    🚨 <b>EMERGENCY</b><br>

                    A potentially life-threatening electrical hazard may be present.
                    Move to a safe location and contact appropriate emergency
                    services or qualified professionals.

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.warning(
                    "⚠️ The AI response did not provide a clear risk level."
                )

            # =========================
            # RECOMMENDATION
            # =========================

            st.markdown(
                """
                <div class="recommendation-box">

                🛡️ <b>Safety Recommendation</b><br>

                Follow the safety precautions provided below.
                Do not attempt electrical repairs beyond your level
                of training or qualification.

                </div>
                """,
                unsafe_allow_html=True
            )

            # =========================
            # AI SAFETY ANALYSIS
            # =========================

            st.subheader(
                "🤖 AI Safety Analysis"
            )

            st.markdown(answer)

            # =========================
            # DOWNLOAD REPORT
            # =========================

            st.subheader(
                "📥 Download Safety Report"
            )

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
            # RETRIEVED RAG KNOWLEDGE
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

st.subheader(
    "⚙️ How It Works"
)

workflow_col1, workflow_col2, workflow_col3 = st.columns(3)

with workflow_col1:

    st.markdown(
        """
        <div class="workflow-box">

        <div class="workflow-number">1️⃣</div>

        <b>User Input</b>

        <p>
        User describes an electrical problem.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

with workflow_col2:

    st.markdown(
        """
        <div class="workflow-box">

        <div class="workflow-number">2️⃣</div>

        <b>RAG Knowledge</b>

        <p>
        Relevant electrical safety information
        is retrieved from the knowledge base.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

with workflow_col3:

    st.markdown(
        """
        <div class="workflow-box">

        <div class="workflow-number">3️⃣</div>

        <b>AI Analysis</b>

        <p>
        The AI agent analyzes the problem
        using the retrieved safety knowledge.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

workflow_col4, workflow_col5, workflow_col6 = st.columns(3)

with workflow_col4:

    st.markdown(
        """
        <div class="workflow-box">

        <div class="workflow-number">4️⃣</div>

        <b>Risk Detection</b>

        <p>
        The agent identifies Low, Medium,
        High, or Emergency risk.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

with workflow_col5:

    st.markdown(
        """
        <div class="workflow-box">

        <div class="workflow-number">5️⃣</div>

        <b>Safety Guidance</b>

        <p>
        The agent provides safe precautions
        and professional-help guidance.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

with workflow_col6:

    st.markdown(
        """
        <div class="workflow-box">

        <div class="workflow-number">6️⃣</div>

        <b>Safety Decision</b>

        <p>
        The user receives a clear safety-focused
        recommendation.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# KNOWLEDGE SOURCES
# =========================

st.divider()

st.subheader(
    "📚 Safety Knowledge Sources"
)

st.markdown("""
This AI Safety Agent uses a retrieval-based knowledge base
to support its electrical safety analysis.

### Knowledge Sources

- **OSHA** — Electrical Safety guidance
- **HSE** — Electrical Safety guidance
- **General electrical safety and hazard-prevention practices**

### RAG Process

**User Problem → Retrieve Relevant Safety Knowledge → AI Analysis → Risk Level → Safety Guidance**
""")

st.info(
    "⚠️ This application provides educational safety guidance. "
    "For electrical emergencies such as electric shock, fire, smoke, "
    "major sparking, or exposed live parts, move to a safe location "
    "and contact appropriate emergency services or qualified professionals."
)

# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "⚡ Electrical Safety AI Agent | Hackathon Project | "
    "RAG-based safety guidance"
)
