# ---------------- Import core libraries ----------------
import streamlit as st                        # Streamlit for web UI
from datetime import datetime                 # For timestamps on uploads
import os                                     # For environment variables
from dotenv import load_dotenv                # Load .env for API keys
from pypdf import PdfReader                   # PDF text extraction
from langchain.chains import LLMChain         # LangChain workflow
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini LLM
from pydantic import SecretStr                # Secure API key handling
from langchain.prompts import PromptTemplate  # LLM prompt templates
import speech_recognition as sr               # Voice recognition
import re                                     # Regex for skill extraction
import streamlit_ace                           # Online code editor

# ---------------- Import custom pages ----------------
from app.login import login
from app.profile import profile
from app.uploads import uploads
from app.settings import settings

# ---------------- App configuration ----------------
st.set_page_config(page_title="ResumeBot - AI Interview Coach", page_icon="🤖")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY environment variable is not set.")

# ---------------- Initialize Gemini LLM ----------------
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=SecretStr(api_key))

# ---------------- Default session state ----------------
default_session = {
    "logged_in": False,
    "username": "",
    "email": "",
    "phone": "",
    "account_type": "User",
    "password": "",
    "profile_image": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    "upload_history": [],
    "questions": None,
    "voice_answer": ""
}
for k, v in default_session.items():
    st.session_state.setdefault(k, v)

# ---------------- Login check ----------------
if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- Sidebar with profile ----------------
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center;">
        <img src="{st.session_state.profile_image}" width="100">
        <h4 style="margin-top: 10px; text-decoration: underline;">{st.session_state.username}</h4>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("## 🤖 ResumeBot Navigation")
sections = [
    ("🏠 Dashboard", "Dashboard"),
    ("🧑‍💼 Profile", "Profile"),
    ("📁 Recent Uploads", "Uploads"),
    ("⚙️ Settings", "Settings"),
]
if "page_id" not in st.session_state:
    st.session_state["page_id"] = "Dashboard"

for name, pid in sections:
    if st.sidebar.button(name, key=pid, use_container_width=True):
        st.session_state["page_id"] = pid

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

page = st.session_state["page_id"]

# ---------------- Dashboard ----------------
def show_interview_dashboard():
    st.title("🤖 ResumeBot - AI Interview Coach")
    st.write("Upload your resume and practice interview questions with text, voice, or coding!")

    # ---------------- Resume Upload ----------------
    uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type="pdf")
    if uploaded_file:
        pdf_reader = PdfReader(uploaded_file)
        resume_text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        # Track upload history
        st.session_state.upload_history.append({
            "filename": uploaded_file.name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # ---------------- AI Interview Questions ----------------
        if st.session_state.questions is None:
            prompt = PromptTemplate(
                input_variables=["resume_text"],
                template="Based on the following resume, generate 10 relevant interview questions:\n{resume_text}"
            )
            chain = LLMChain(llm=llm, prompt=prompt)
            st.session_state.questions = chain.run(resume_text=resume_text)

        st.subheader("🎯 Interview Questions:")
        questions = [q for q in st.session_state.questions.split("\n") if q.strip()]
        st.write(questions)

        selected_question = st.selectbox("👉 Select a question to answer:", questions)
        user_answer = st.text_area("✍️ Type your Answer:")

        # ---------------- Voice Answer ----------------
        st.markdown("### 🎙️ OR Record your Voice Answer")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🎤 Record"):
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    st.info("Listening...")
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        text = recognizer.recognize_google(audio)
                        st.success(f"You said: {text}")
                        st.session_state.voice_answer = text
                    except:
                        st.error("Voice not recognized.")
        with col2:
            st.write(st.session_state.get("voice_answer", ""))

        final_answer = st.session_state.get("voice_answer") or user_answer

        # ---------------- Feedback ----------------
        if st.button("🚀 Get Feedback"):
            if final_answer:
                feedback_prompt = PromptTemplate(
                    input_variables=["question", "answer"],
                    template="""
                    Question: {question}
                    Candidate's Answer: {answer}
                    Provide professional feedback on relevance, clarity, and improvement.
                    """
                )
                feedback_chain = LLMChain(llm=llm, prompt=feedback_prompt)
                feedback = feedback_chain.run(question=selected_question, answer=final_answer)
                st.markdown("### 📋 Feedback:")
                st.markdown(f"<div class='feedback-box'>{feedback}</div>", unsafe_allow_html=True)
            else:
                st.warning("Provide an answer by text or voice.")

       # ---------------- Programming Questions & Online Compiler ----------------
        st.subheader("💻 Programming Questions Section")

        # Step 1: Extract skills using Gemini LLM
        skill_extraction_prompt = PromptTemplate(
            input_variables=["resume_text"],
            template="""
            Analyze the following resume text and extract technical skills in these categories:
            - Programming Languages (Python, C, C++, Java, etc.)
            - Web Development (HTML, CSS, JavaScript, Django, Flask, etc.)
            - Databases (MySQL, SQL, PostgreSQL, etc.)
            - Data Science, Machine Learning, or AI tools.

            Return them as a comma-separated list only.
            Resume Text:
            {resume_text}
            """
        )
        extract_chain = LLMChain(llm=llm, prompt=skill_extraction_prompt)
        extracted_skills = extract_chain.run(resume_text=resume_text).strip()

        if extracted_skills:
            st.info(f"🧠 Detected Skills: {extracted_skills}")

            # Step 2: Generate skill-based coding & SQL questions
            question_prompt = PromptTemplate(
                input_variables=["skills"],
                template="""
                Generate 10 short, practical, and resume-based coding or SQL interview questions 
                based on these skills: {skills}.

                Include:
                - Basic logic programs (even/odd, factorial, palindrome)
                - String or array handling
                - File handling or exception handling (for Python/Java)
                - SQL tasks (CREATE TABLE, INSERT, SELECT queries)
                - Web-related small tasks (HTML/CSS/JS) if relevant

                Each question should be skill-relevant and returned on a new line.
                """
            )
            q_chain = LLMChain(llm=llm, prompt=question_prompt)
            coding_questions = q_chain.run(skills=extracted_skills)
            question_list = [q.strip() for q in coding_questions.split("\n") if q.strip()]

            # Step 3: Dropdown for question selection
            selected_question = st.selectbox("🎯 Select a Question to Solve:", question_list)

            # Step 4: Language selection
            selected_lang = st.selectbox(
                "Choose Language:",
                ["Python", "C", "C++", "Java", "SQL", "HTML", "JavaScript"]
            )

            # Step 5: White-themed ACE code editor
            st.markdown("**✍️ Write Your Code Below:**")
            code_input = streamlit_ace.st_ace(
                placeholder=f"Write your {selected_lang} code here...",
                language="python" if selected_lang.lower() == "python" else "sql",
                theme="xcode",       # ✅ White background editor
                key="code_editor",
                height=300,
                font_size=15,
                tab_size=4,
                wrap=True,
                auto_update=True,
            )

            # Step 6: Input editor for test data
            st.markdown("**📥 Provide Input (if your code uses input()):**")
            input_data = streamlit_ace.st_ace(
                placeholder="Type program inputs here (one per line)...",
                language="plain_text",
                theme="xcode",
                key="input_editor",
                height=120,
                font_size=14,
                tab_size=4,
                wrap=True,
            )

            # Step 7: Run / Feedback buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                run_clicked = st.button("▶️ Run Code")
            with col2:
                feedback_clicked = st.button("💡 Get AI Feedback")

            # Step 8: Run code for Python only
            if run_clicked:
                if selected_lang == "Python":
                    try:
                        import io, sys
                        sys.stdin = io.StringIO(input_data)  # Feed input() values
                        exec_globals = {}
                        exec(code_input, exec_globals)
                        st.success("✅ Code executed successfully!")
                    except Exception as e:
                        st.error(f"❌ Error during execution: {e}")
                elif selected_lang == "SQL":
                    st.info("ℹ️ SQL execution requires a connected database (not included in this demo).")
                else:
                    st.warning("⚙️ Code execution currently supports only Python.")

            # Step 9: AI feedback for code
            if feedback_clicked:
                if code_input.strip():
                    feedback_prompt = PromptTemplate(
                        input_variables=["question", "code", "skills"],
                        template="""
                        Evaluate the candidate's code based on the given question and skills.
                        Provide detailed feedback covering:
                        - Logic correctness
                        - Code efficiency
                        - Readability and maintainability
                        - Suggestions for improvement

                        Skills: {skills}
                        Question: {question}
                        Candidate Code:
                        {code}
                        """
                    )
                    feedback_chain = LLMChain(llm=llm, prompt=feedback_prompt)
                    feedback = feedback_chain.run(
                        question=selected_question,
                        code=code_input,
                        skills=extracted_skills
                    )
                    st.markdown("### 📋 AI Feedback on Your Code:")
                    st.markdown(f"<div class='feedback-box'>{feedback}</div>", unsafe_allow_html=True)
                else:
                    st.warning("✍️ Please enter your code before requesting feedback.")
        else:
            st.warning("⚠️ No technical skills detected in the uploaded resume.")


# ---------------- Page Routing ----------------
if page == "Dashboard":
    show_interview_dashboard()
elif page == "Profile":
    profile()
elif page == "Uploads":
    uploads()
elif page == "Settings":
    settings()

# ---------------- Footer ----------------
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    text-align: center;
    color: #888;
    font-size: 0.9em;
    padding: 8px;
    background-color: #f9f9f9;
    border-top: 1px solid #ddd;
}
</style>
<div class='footer'>Developed with ❤️ by Sarathkumar R | © 2025</div>
""", unsafe_allow_html=True)
