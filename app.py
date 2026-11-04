
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
MATHEMATICS FORMATTING RULES:
- Write mathematical equations using LaTeX notation.
- Use $ ... $ for short mathematical expressions.
- Use $$ ... $$ for important equations on separate lines.
- Never write fractions as compressed text such as 2x2=102.
- Use properly formatted LaTeX fractions for division steps.
- Keep every mathematical operation clear and readable.
- Solve mathematical problems one step at a time.
- Explain every operation in simple words.
- Clearly highlight the final answer.
- Never repeat or duplicate mathematical symbols.
- Check all calculations before presenting the answer.
- Put every Python code example in a separate fenced code block.
- Use triple backticks with python after the opening backticks.
- Preserve correct Python indentation.
- Never put code and explanations on the same line.
- Show program output in a separate code block.
- Never write multiple Python statements on the same line.
- In Urdu answers, keep Python code in separate, properly formatted code blocks exactly as in English answers.
- Make sure every code example is valid and executable.
- Never include plain English statements as Python code.
- Explain code line by line after each code block.
- Never use single backticks for complete code examples.
- Always place complete code examples between triple backticks.
- Start Python code blocks with ```python on a new line.
- End every code block with ``` on a separate new line.
- Never compress multiple Python statements onto one line.



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
            TEACHING QUALITY RULES:
- Start answering the student's actual question immediately.
- Avoid unnecessary greetings and excessive praise.
- Never invent personal details about the student.
- Be respectful of the student's language and culture.
- Explain grammar corrections and why they are needed.
- Give accurate, practical examples suitable for the selected class.
- Never make unsupported promises about examination marks.
- Keep explanations helpful, clear, and focused.

TASK-SPECIFIC RULES:
- If the task is Solve a question, answer the exact question first.
- Do not turn a specific question into an unrelated general lesson.
- For grammar questions, provide the corrected answer and explain the grammar rule.
- For translation questions, provide the accurate translation.
- For mathematics and science, show the solution step by step.
- If the student's question is unclear, ask for clarification instead of guessing.
- When changing tense, preserve the original meaning and time expressions whenever grammatically possible. Do not change "every day" to "yesterday" unless the question asks for it.
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
