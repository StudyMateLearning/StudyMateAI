
import streamlit as st
from google import genai
import time
import re
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚"
)

st.title("📚 StudyMate AI")
st.subheader("Your free personal learning assistant")

st.write("Learn difficult topics in simple English or Urdu.")

subject = st.selectbox(
    "Choose your subject",
    [
        "Mathematics",
        "Computer Science",
        "English",
        "Physics",
        "Chemistry",
        "Biology",
        "Other"
    ]
)

language = st.selectbox(
    "Choose your language",
    ["Simple English", "Urdu"]
)

student_class = st.selectbox(
    "Choose your class",
    ["9th Class", "10th Class", "11th Class", "12th Class"]
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
            Class: {student_class}
            Language: {language}
            Task: {task}
            Student question: {question}

            Explain everything clearly using simple words.
Give practical examples.

IMPORTANT FORMATTING RULES:
- Put every Python code example in a separate fenced code block.
- Use triple backticks with python after the opening backticks.
- Preserve correct Python indentation.
- Never put code and explanations on the same line.
- Show program output in a separate code block.
- Make sure every code example is valid and executable.
- Never include plain English statements as Python code.
- Explain code line by line after each code block.

Show mathematics step by step.

            If generating a quiz, provide five questions
            and an answer key separately.

            Encourage the student to understand.

            Match the difficulty and depth of your explanation
            to the selected class and its school level.

            For Pakistani students, use familiar examples.
            For Urdu, explain naturally in Urdu script.
            Keep technical terms in English when helpful.

            Do not assume the student already understands
            advanced concepts. Explain step by step.
            """

            
            response = None

            with st.spinner("StudyMate AI is thinking..."):
                for attempt in range(4):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )
                        break

                    except Exception as error:
                        if "503" in str(error) or "UNAVAILABLE" in str(error):
                            if attempt == 3:
                                st.warning(
                                    "StudyMate AI is temporarily busy. "
                                    "Please try again in a few minutes."
                                )
                            else:
                                time.sleep(10 * (attempt + 1))
                        else:
                            raise error

            if response is not None:
                answer = response.text

                parts = re.split(
                    r"```(\w*)\n(.*?)```",
                    answer,
                    flags=re.DOTALL
                )

                for i in range(0, len(parts), 3):
                    st.markdown(parts[i])

                    if i + 2 < len(parts):
                        code_language = parts[i + 1] or "python"
                        code = parts[i + 2].strip()
                        st.code(code, language=code_language)    
        except Exception as error:
            st.error(f"Something went wrong: {error}")
