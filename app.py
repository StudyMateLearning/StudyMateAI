
import streamlit as st
from google import genai
from supabase import create_client
import time
import re

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)

# ---------------- SUPABASE CONNECTION ----------------

if "supabase_client" not in st.session_state:
    try:
        st.session_state.supabase_client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
    except Exception as error:
        st.error("Supabase connection setup failed.")
        st.code(str(error))
        st.stop()

supabase = st.session_state.supabase_client

if "student" not in st.session_state:
    st.session_state.student = None

if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = None


# ---------------- HELPER FUNCTIONS ----------------

def show_auth_error(error):
    st.error(f"Something went wrong: {error}")


def save_message(conversation_id, role, content):
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content
    }).execute()


def show_answer(answer):
    parts = re.split(
        r"```(\w*)\n(.*?)```",
        answer,
        flags=re.DOTALL
    )

    for i in range(0, len(parts), 3):
        text_part = parts[i].strip()

        if text_part:
            st.markdown(text_part)

        if i + 2 < len(parts):
            code_language = parts[i + 1] or "python"
            code = parts[i + 2].strip()

            if code:
                st.code(code, language=code_language)


# ---------------- LOGIN AND REGISTRATION ----------------

if st.session_state.student is None:

    st.title("📚 StudyMate AI")
    st.subheader("Your free personal learning assistant")
    st.write("Learn difficult topics in simple English or Urdu.")

    login_tab, signup_tab = st.tabs([
        "Login",
        "Create an account"
    ])

    with login_tab:
        st.subheader("Welcome back!")

        login_email = st.text_input(
            "Email address",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            if not login_email or not login_password:
                st.warning("Please enter your email and password.")

            else:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": login_email,
                        "password": login_password
                    })

                    st.session_state.student = {
                        "id": str(response.user.id),
                        "email": response.user.email
                    }

                    st.session_state.active_conversation = None

                    st.success("Login successful!")
                    st.rerun()

                except Exception as error:
                    show_auth_error(error)

    with signup_tab:
        st.subheader("Create your free student account")

        full_name = st.text_input(
            "Your full name",
            key="signup_name"
        )

        signup_email = st.text_input(
            "Email address",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Create a password",
            type="password",
            key="signup_password"
        )

        if st.button("Create account", use_container_width=True):

            if not full_name.strip() or not signup_email.strip() or not signup_password:
                st.warning("Please complete all fields.")

            elif len(signup_password) < 6:
                st.warning("Your password must contain at least 6 characters.")

            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": signup_email.strip(),
                        "password": signup_password,
                        "options": {
                            "data": {
                                "full_name": full_name.strip()
                            }
                        }
                    })

                    if response.session is not None:
                        st.session_state.student = {
                            "id": str(response.user.id),
                            "email": response.user.email
                        }
                        st.success("Account created successfully!")
                        st.rerun()

                    else:
                        st.success(
                            "Account created! Please check your email "
                            "and click the confirmation link before logging in."
                        )

                except Exception as error:
                    show_auth_error(error)

    st.stop()


# ---------------- STUDENT DASHBOARD ----------------

student = st.session_state.student
user_id = student["id"]

st.title("📚 StudyMate AI")
st.subheader("Your free personal learning assistant")
st.write("Learn difficult topics in simple English or Urdu.")

st.sidebar.title("👨‍🎓 Student Account")
st.sidebar.write(f"Email: {student['email']}")

if st.sidebar.button("Logout"):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.student = None
    st.session_state.active_conversation = None
    st.rerun()


# ---------------- PREVIOUS CONVERSATIONS ----------------

st.sidebar.divider()
st.sidebar.subheader("📖 Your Chat History")

if st.sidebar.button("➕ Start a new conversation"):
    st.session_state.active_conversation = None
    st.rerun()

try:
    conversations = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
        .data
    )

    conversation_titles = {
        c["id"]: c["title"] for c in conversations
    }

    options = [None] + [c["id"] for c in conversations]

    current_id = st.session_state.active_conversation

    if current_id not in options:
        current_id = None

    selected_conversation = st.sidebar.selectbox(
        "Open an old conversation",
        options,
        index=options.index(current_id),
        format_func=lambda x: (
            "New conversation" if x is None
            else conversation_titles.get(x, "Previous conversation")
        )
    )

    st.session_state.active_conversation = selected_conversation

except Exception as error:
    st.sidebar.error(f"Could not load chat history: {error}")


# ---------------- SHOW SELECTED CHAT ----------------

if st.session_state.active_conversation:

    try:
        old_messages = (
            supabase.table("messages")
            .select("*")
            .eq(
                "conversation_id",
                st.session_state.active_conversation
            )
            .order("created_at")
            .execute()
            .data
        )

        for message in old_messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    show_answer(message["content"])
                else:
                    st.markdown(message["content"])

    except Exception as error:
        st.error(f"Could not load messages: {error}")


# ---------------- STUDY SETTINGS ----------------

st.divider()
st.subheader("📚 Start learning")

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
    [
        "Explain a topic",
        "Solve a question",
        "Generate a quiz"
    ]
)

question = st.text_area(
    "Enter your question or topic",
    placeholder="Example: Explain Python loops..."
)

# ---------------- GEMINI AI AND AUTOMATIC SAVING ----------------

if st.button("Ask StudyMate AI", type="primary"):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        try:
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            conversation_id = st.session_state.active_conversation

            # Create a new conversation when needed
            if conversation_id is None:

                new_conversation = (
                    supabase.table("conversations")
                    .insert({
                        "user_id": user_id,
                        "title": question.strip()[:60],
                        "subject": subject
                    })
                    .execute()
                    .data[0]
                )

                conversation_id = new_conversation["id"]
                st.session_state.active_conversation = conversation_id

            # Save student's question
            save_message(
                conversation_id,
                "user",
                question.strip()
            )

            prompt = f"""
You are StudyMate AI, a friendly tutor for Pakistani students.

Subject: {subject}
Class: {student_class}
Language: {language}
Task: {task}
Student question: {question}

Explain everything clearly using simple words.
Give practical examples.

IMPORTANT FORMATTING RULES:

- Write mathematical equations using LaTeX notation.
- Use $ ... $ for short mathematical expressions.
- Use $$ ... $$ for important equations on separate lines.
- Never write fractions as compressed text.
- Use properly formatted LaTeX fractions for division steps.
- Solve mathematical problems one step at a time.
- Explain every mathematical operation in simple words.
- Clearly highlight the final answer.
- Check all calculations before presenting the answer.
- Put every Python code example in a separate fenced code block.
- Use triple backticks with python after the opening backticks.
- Preserve correct Python indentation.
- Never put code and explanations on the same line.
- Show program output in a separate code block.
- Make sure every code example is valid and executable.
- Explain code line by line after each code block.
- Show mathematics step by step.

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
- When changing tense, preserve the original meaning and time expressions whenever grammatically possible.
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

            if response is not None and response.text:

                answer = response.text

                # Save AI answer
                save_message(
                    conversation_id,
                    "assistant",
                    answer
                )

                # Update conversation time
                supabase.table("conversations").update({
                    "updated_at": "now()"
                }).eq("id", conversation_id).execute()

                st.subheader("StudyMate AI's Answer")
                show_answer(answer)

                st.success("Your question and answer have been saved!")

                st.rerun()

        except Exception as error:
            st.error(f"Something went wrong: {error}")



# ---------------- SAVED NOTES ----------------

st.divider()
st.subheader("📝 My Saved Notes")

if "show_note_form" not in st.session_state:
    st.session_state.show_note_form = False

if st.button("➕ Add a note" if not st.session_state.show_note_form else "Cancel"):
    st.session_state.show_note_form = not st.session_state.show_note_form
    st.rerun()

if st.session_state.show_note_form:
    with st.form("save_note_form"):
        note_title = st.text_input("Note title")
        note_content = st.text_area("Write your notes here")

        submitted = st.form_submit_button("Save note")

        if submitted:
            if note_title.strip() and note_content.strip():
                try:
                    supabase.table("saved_notes").insert({
                        "user_id": user_id,
                        "title": note_title.strip(),
                        "content": note_content.strip()
                    }).execute()

                    st.session_state.show_note_form = False
                    st.success("Your note has been saved!")
                    st.rerun()

                except Exception as error:
                    st.error(f"Could not save note: {error}")
            else:
                st.warning("Please enter both a title and note content.")

try:
    notes = (
        supabase.table("saved_notes")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
        .data
    )

    if notes:
        for note in notes:
            with st.expander(note["title"]):
                st.write(note["content"])
    else:
        st.info("You haven't saved any notes yet.")

except Exception as error:
    st.error(f"Could not load notes: {error}")
