
import streamlit as st
from google import genai

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚"
)

st.title("📚 StudyMate AI")
st.subheader("Your free personal learning assistant")

st.write("Learn difficult topics in simple English or Urdu.")

subject = st.selectbox(
    "Choose your subject",
    ["Mathematics", "Computer Science", "English",
     "Physics", "Chemistry", "Biology", "Other"]
)

language = st.selectbox(
    "Choose your language",
    ["Simple English", "Urdu"]
)

task = st.selectbox(
    "What do you need help with?",
    ["Explain a topic", "Solve a question", "Generate a quiz"]
)

question = st.text_area(
    "Enter your question or topic",
    placeholder="Example: Explain Python loops..."
)

if st.button("Ask StudyMate AI"):
    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        try:
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            prompt = f"""
            You are StudyMate AI, a friendly tutor
            for Pakistani students.

            Subject: {subject}
            Language: {language}
            Task: {task}
            Student question: {question}

            Explain everything clearly using simple words.
            Give practical examples.
            Show mathematics step by step.
            If generating a quiz, provide five questions
            and an answer key separately.
            Encourage the student to understand.
            """

            with st.spinner("StudyMate AI is thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.markdown("### Your Answer")
            st.write(response.text)

        except Exception as error:
            st.error(f"Something went wrong: {error}")
