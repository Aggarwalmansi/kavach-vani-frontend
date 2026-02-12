import streamlit as st
import requests

# ------------------ Config ------------------
# BACKEND_URL = "http://127.0.0.1:8000/analyze"  # Local backend
# When deployed, change to:
BACKEND_URL = "https://kavach-vani-backend.onrender.com/analyze"

# ------------------ Page config ------------------
st.set_page_config(
    page_title="Kavach-Vani",
    layout="wide"
)

st.title("Kavach-Vani")
st.caption("Explainable Legal AI for Indian Judgments")

st.divider()

# ------------------ Case Context ------------------
st.subheader("Case Context")

case_mode = st.radio(
    "Choose analysis scope",
    ["General analysis (across cases)", "Analyze a specific case"],
    horizontal=True
)

case_file = None
if case_mode == "Analyze a specific case":
    case_file = st.selectbox(
        "Select a case from the knowledge base",
        [
            "2020_1_90_93_EN.pdf",
            "2020_3_514_524_EN.pdf",
            "2020_6_289_302_EN.pdf"
        ]
    )

st.divider()

# ------------------ User Query ------------------
st.subheader("Ask your question")

user_query = st.text_input(
    "Enter your legal question",
    placeholder="Why was the employee dismissed?",
    label_visibility="collapsed"
)

analyze = st.button("Analyze")

# ------------------ Backend Call ------------------
if analyze:
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        payload = {
            "user_query": user_query,
            "case_file": case_file
        }

        with st.spinner("Analyzing with legal context..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

            except requests.exceptions.RequestException as e:
                st.error(f"Backend error: {e}")
                st.stop()

        # ------------------ Output ------------------
        st.subheader("Interpreted Intent")
        st.write(data.get("interpreted_intent", "—"))

        st.subheader("Answer")
        st.write(data.get("answer", "No answer returned."))

        st.subheader("Evidence")
        evidence = data.get("evidence", [])
        if evidence:
            # Deduplicate evidence by file
            seen = set()
            for ev in evidence:
                if ev["file"] not in seen:
                    seen.add(ev["file"])
                    st.write(
                        f"- **{ev['file']}** ({ev['year']}, {ev['source']})"
                    )
        else:
            st.write("No evidence returned.")
