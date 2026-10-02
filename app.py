import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Electrical Safety AI Agent",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Electrical Safety AI Agent")
st.write(
    "Describe your electrical problem and the AI agent will provide "
    "safety-focused guidance."
)

# Get API key from Streamlit Secrets
api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

system_prompt = """
You are an Electrical Safety AI Agent designed to help users understand
common electrical safety risks.

Your responsibilities are:

1. Understand the user's electrical problem or situation.
2. Identify possible electrical hazards.
3. Explain the risk in simple and beginner-friendly language.
4. Provide safe, practical precautions.
5. Tell the user when they should contact a qualified electrician.
6. Clearly identify emergency situations such as electric shock, fire,
   smoke, exposed live wires, sparks, or severe overheating.
7. Never instruct the user to perform dangerous electrical work.
8. Never encourage the user to touch live wires, open energized equipment,
   bypass protection devices, or perform unsafe experiments.
9. If the situation is dangerous or uncertain, prioritize safety.
10. Do not pretend to physically inspect or diagnose electrical equipment.

For every response, use this structure:

⚠️ Possible Hazard:
Explain the likely electrical hazard.

🔴 Risk Level:
Low / Medium / High / Emergency

📖 Why It Is Dangerous:
Explain the risk in simple language.

🛡️ Safety Precautions:
Give safe precautions the user can follow without performing dangerous
electrical work.

👷 Professional Help:
Explain whether a qualified electrician should inspect the situation.

🚨 Emergency Warning:
If there is immediate danger such as fire, electric shock, smoke,
or exposed live electrical parts, clearly tell the user to move away
and seek appropriate emergency/professional help.

Always prioritize human safety over providing technical instructions.
"""

user_problem = st.text_area(
    "Describe your electrical problem:",
    placeholder="Example: My socket is making a buzzing sound and becoming hot.",
    height=150
)

if st.button("🔍 Analyze Safety Risk", type="primary"):

    if not user_problem.strip():
        st.warning("Please describe an electrical problem first.")

    else:
        with st.spinner("Analyzing electrical safety risk..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_problem
                    }
                ],
                temperature=0.2
            )

            answer = response.choices[0].message.content

        st.subheader("🛡️ Safety Analysis")
        st.markdown(answer)
