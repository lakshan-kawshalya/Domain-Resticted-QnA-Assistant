"""
DOMAIN-RESTRICTED Q&A ASSISTANT
================================

YOUR TASK:
----------
Implement the functions marked with "STUDENT CODE HERE" below.
Each function has a docstring that explains exactly what it should do.
Read the docstrings carefully - they are your guide!

DEVELOPMENT STRATEGY:
---------------------
Build one tab at a time in this order:
1. Setup tab (render_setup_tab + load_knowledge_base)
2. Chat tab (render_chat_tab + build_prompt + get_ai_response)
3. Quick Questions tab (render_quick_questions_tab)

Run "streamlit run app.py" after EVERY change!

WHAT'S ALREADY PROVIDED:
------------------------
- All imports
- All constants (domains, questions, options)
- All function signatures with type hints
- initialize_session_state() (complete)
- main() (complete)
- is_setup_complete() (complete)
- render_setup_status() (complete)

WHAT YOU IMPLEMENT:
-------------------
- load_knowledge_base()
- build_prompt()
- get_ai_response()
- render_setup_tab()
- render_chat_tab()
- render_quick_questions_tab()
"""

import pandas as pd
import streamlit as st
from openai import OpenAI
from streamlit.runtime.uploaded_file_manager import UploadedFile

# ==============================================================================
# CONFIGURATION AND CONSTANTS
# ==============================================================================

# Available domains for the assistant
AVAILABLE_DOMAINS: list[str] = ["Fitness", "Travel", "Biology", "Personal Finance"]

# Prompt template questions for each domain (dict of lists)
PREBUILT_QUESTIONS: dict[str, list[str]] = {
    "Fitness": [
        "Create a beginner workout plan",
        "What should I eat before training?",
        "How do I stay consistent with fitness?",
        "How much protein do I need daily?",
    ],
    "Travel": [
        "Plan a 1-day city itinerary",
        "What are the best budget travel tips?",
        "How do I stay safe while traveling solo?",
        "What should I pack for international travel?",
    ],
    "Biology": [
        "Explain how photosynthesis works",
        "What is the difference between mitosis and meiosis?",
        "How does the immune system fight infections?",
        "What are the main functions of DNA?",
    ],
    "Personal Finance": [
        "How do I create a monthly budget?",
        "What should I know about investing?",
        "How do I build an emergency fund?",
        "Explain compound interest",
    ],
}

# Prompt style options
TONE_OPTIONS: list[str] = ["Friendly", "Professional", "Casual"]
LENGTH_OPTIONS: list[str] = ["Brief", "Moderate", "Detailed"]
AUDIENCE_OPTIONS: list[str] = ["Beginner", "Intermediate", "Advanced"]

# Required columns in the uploaded CSV
REQUIRED_CSV_COLUMNS: list[str] = ["topic", "information"]


# ==============================================================================
# HELPER FUNCTIONS (PROVIDED - DO NOT MODIFY)
# ==============================================================================


def is_setup_complete() -> bool:
    """
    Check if both domain and knowledge base are configured.

    Returns:
        True if setup is complete, False otherwise.
    """
    return (
        st.session_state.selected_domain is not None
        and st.session_state.knowledge_base is not None
    )


def render_setup_status() -> None:
    """
    Show a compact status bar indicating what setup steps are done.
    If setup is incomplete, shows a helpful message pointing to the Setup tab.
    """
    domain_done: bool = st.session_state.selected_domain is not None
    kb_done: bool = st.session_state.knowledge_base is not None

    if domain_done and kb_done:
        st.success(
            f"Ready — Domain: **{st.session_state.selected_domain}** | "
            f"Knowledge Base: **{st.session_state.uploaded_filename}**"
        )
    else:
        missing: list[str] = []
        if not domain_done:
            missing.append("select a domain")
        if not kb_done:
            missing.append("upload a knowledge base")
        st.warning(f"Go to the **Setup** tab to {' and '.join(missing)}.")


# ==============================================================================
# FUNCTIONS TO IMPLEMENT
# ==============================================================================


def load_knowledge_base(uploaded_file: UploadedFile) -> str:
    """
    Load the knowledge base from uploaded CSV file.

    Steps:
    1. Reset the file position to the beginning with seek(0)
    2. Use pd.read_csv() to read the CSV file into a DataFrame
    3. Validate that required columns ('topic' and 'information') exist
    4. Check that the DataFrame is not empty
    5. Iterate through rows and build a formatted text string
    6. Return the formatted string

    Error handling:
    - If columns are missing, return a string starting with "Error:"
    - If the DataFrame is empty, return a string starting with "Error:"
    - Wrap everything in try/except to catch pandas exceptions

    Args:
        uploaded_file: A Streamlit UploadedFile object containing CSV data.

    Returns:
        A formatted string with all knowledge base content, or an error
        message starting with "Error:" if loading fails.
    """
    # STUDENT CODE HERE
    try:
        uploaded_file.seek(0)

        kb_content: str = ""
        df: pd.DataFrame = pd.read_csv(uploaded_file)

        for col in REQUIRED_CSV_COLUMNS:
            if col not in df.columns:
                return f"Error: Missing column '{col}' !"
        if df.empty:
            return "Error: No data rows !"

        for _, row in df.iterrows():
            topic: str = str(row["topic"]).strip()
            info: str = str(row["information"]).strip()

            kb_content += f"Topic: {topic}\nInformation: {info}\n\n"

        return kb_content

    except pd.errors.EmptyDataError:
        return "Error: The CSV file is empty."
    except pd.errors.ParserError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def build_prompt(
    domain: str,
    knowledge_base: str,
    tone: str,
    length: str,
    audience: str,
    user_question: str,
) -> str:
    """
    Build the complete prompt with all 5 required sections.

    The prompt must include these 5 sections:
    1. Role - Define the assistant's role and specialty domain
    2. Domain Constraint - Limit responses to the selected domain only
    3. Knowledge Base - Include the full CSV content as context
    4. Style Variables - Apply tone, length, and audience settings
    5. User Question - The actual question to answer

    Use a multi-line f-string to construct the prompt with all parameters.

    Args:
        domain: The selected specialty domain (e.g. "Fitness").
        knowledge_base: The full knowledge base text from the CSV.
        tone: The desired response tone (e.g. "Friendly").
        length: The desired response length (e.g. "Moderate").
        audience: The target audience level (e.g. "Beginner").
        user_question: The user's question to answer.

    Returns:
        A complete prompt string ready to send to an AI API.
    """
    # STUDENT CODE HERE
    return f"""
prompt : str = You are a {domain} expert .

RULES :
Only answer questions about {domain}. If asked about other topics ,
politely decline .

KNOWLEDGE BASE :
{knowledge_base}

STYLE :
- Tone : {tone}
- Length : {length}
- Audience : {audience}

QUESTION :
{user_question}

Answer based ONLY on the knowledge base above .
"""


def get_ai_response(prompt: str) -> str:
    """
    Send the prompt to OpenAI and return the AI's response.

    Steps:
    1. Get the API key from st.session_state.get("openai_api_key")
    2. If no API key, return an error message string
    3. Create an OpenAI client: OpenAI(api_key=api_key)
    4. Call client.chat.completions.create() with:
       - model="gpt-4o-mini"
       - messages=[{"role": "user", "content": prompt}]
       - max_tokens=1024
    5. Return response.choices[0].message.content
    6. Wrap everything in try/except to handle API errors

    Args:
        prompt: The complete prompt string to send to OpenAI.

    Returns:
        The AI's response text, or an error message if the call fails.
    """
    # STUDENT CODE HERE
    api_key: str = st.session_state.get("openai_api_key")

    try:
        client: OpenAI = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )

        return response

    except Exception as e:
        return f"Error: {str(e)}"


# ==============================================================================
# TAB RENDERING FUNCTIONS TO IMPLEMENT
# ==============================================================================


def render_setup_tab() -> None:
    """
    Render the Setup tab for domain selection and knowledge base upload.

    This tab should:
    1. Display header: "Setup"
    2. Domain selection:
       - st.radio() with AVAILABLE_DOMAINS
       - Store directly in st.session_state.selected_domain (no button needed!)
       - Hint: just compare the radio value to session state and update if different
    3. A st.markdown("---") divider
    4. Knowledge base upload:
       - st.file_uploader() restricted to CSV files
       - Call load_knowledge_base() on uploaded file
       - If result starts with "Error:", show st.error()
       - Otherwise store in session state immediately (no button needed!)
       - Show a st.success() with the filename
       - Show the knowledge base text in an st.expander as a preview

    Remember:
    - Give every widget a unique key= parameter
    - Store domain in st.session_state.selected_domain
    - Store knowledge base text in st.session_state.knowledge_base
    - Store filename in st.session_state.uploaded_filename
    """
    # STUDENT CODE HERE
    st.header("Setup")
    domain: str = st.radio("Domains: ", AVAILABLE_DOMAINS, key="domain_radio")

    if domain != st.session_state.selected_domain:
        st.session_state.selected_domain = domain

    st.markdown("---")

    uploadedFile = st.file_uploader(
        "Upload Knowledge Base...", type=["csv"], key="kb_uploader"
    )

    if uploadedFile is not None:
        st.success(f"File uploaded successfully: {uploadedFile.name}")

        st.session_state.uploaded_filename = uploadedFile.name

        result = load_knowledge_base(uploadedFile)

        if result.startswith("Error:"):
            st.error(result)
        else:
            st.session_state.knowledge_base = result
            st.info("Knowledge Base loaded into memory.")
            with st.expander("View Formatted Content"):
                st.text(result)

    else:
        st.info("No file uploaded yet.")


def render_chat_tab() -> None:
    """
    Render the Chat tab interface.

    This tab should:
    1. Call render_setup_status() to show current config
    2. Check is_setup_complete() — if False, return early
    3. Text input for the user's question (key="chat_question")
       - Add a placeholder like "Ask anything about {domain}..."
    4. Style options inside an st.expander("Response style options"):
       - 3 columns with selectboxes for Tone, Length, Audience
    5. "Get Answer" button (type="primary") that:
       - Validates the question is not empty
       - Calls build_prompt() with all parameters
       - Calls get_ai_response() with the prompt
       - Stores question and answer in session state
    6. Display the last Q&A from session state (if it exists)

    Remember:
    - Give every widget a unique key= parameter
    - Use return after failed validation (NOT st.stop())
    - Only store the LAST question and answer (no history)
    """
    # STUDENT CODE HERE
    render_setup_status()

    if not is_setup_complete():
        return

    chat_question: str = st.text_input(
        f"Ask anything about {st.session_state.selected_domain}...", key="chat_question"
    )

    with st.expander("Response style options"):
        col1, col2, col3 = st.columns(3)
        with col1:
            tone: str = st.selectbox("Select Tone", TONE_OPTIONS, key="tone_selector")
        with col2:
            length: str = st.selectbox(
                "Select Length", LENGTH_OPTIONS, key="length_selector"
            )
        with col3:
            audience: str = st.selectbox(
                "Select Audience", AUDIENCE_OPTIONS, key="audience_selector"
            )

    with st.spinner("Crafting the answer..."):
        if st.button("Get Answer", type="primary", key="answer_btn"):
            if chat_question.strip() == "":
                st.info("Please ask a question first.")
                return

            domain = st.session_state.selected_domain
            kb = st.session_state.knowledge_base

            prompt: str = build_prompt(
                domain, kb, tone, length, audience, chat_question
            )

            response: list[str] = get_ai_response(prompt)

            st.session_state.answer = response

            st.write(st.session_state.answer.choices[0].message.content)


def render_quick_questions_tab() -> None:
    """
    Render the Quick Questions tab with domain-specific template questions.

    This tab should:
    1. Call render_setup_status() to show current config
    2. Check is_setup_complete() — if False, return early
    3. Show a caption telling the user to click a question, then go to Chat
    4. Get questions for selected domain from PREBUILT_QUESTIONS
       (use .get() with default empty list)
    5. Define a callback function that sets st.session_state.chat_question
    6. Display each question as a clickable st.button() using on_click=callback

    Why a callback? The Chat tab's text_input (key="chat_question") renders
    before this tab. Streamlit won't let you modify a widget's key after
    it's rendered. But on_click callbacks run BEFORE the next rerun, so
    the key is set before the widget exists.

    Example pattern:
        def select_question(q: str) -> None:
            st.session_state.chat_question = q

        st.button("My Question", on_click=select_question, args=("My Question",))

    Remember:
    - Give every button a unique key= that includes the domain name
    - Use a loop to generate buttons dynamically
    """
    # STUDENT CODE HERE
    pass


# ==============================================================================
# STREAMLIT APP - MAIN INTERFACE (PROVIDED - DO NOT MODIFY)
# ==============================================================================


def initialize_session_state() -> None:
    """
    Initialize all session state variables with default values.

    Session state persists data across Streamlit reruns, allowing the app
    to remember user selections and previous Q&A results.
    """
    defaults: dict[str, str | None] = {
        "selected_domain": None,
        "knowledge_base": None,
        "uploaded_filename": None,
        "last_question": None,
        "last_answer": None,
        "openai_api_key": None,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def main() -> None:
    """
    Main application entry point.

    Sets up the page, initializes session state, and renders three tabs:
    Setup (first), Chat, and Quick Questions.
    """
    st.title("Domain Q&A Assistant")
    st.caption(
        "A specialist assistant that only answers questions within its selected domain"
    )

    initialize_session_state()

    # Sidebar: API key input
    with st.sidebar:
        st.header("Settings")
        st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_api_key",
            help="Enter your OpenAI API key to get real AI responses",
        )

    # Setup tab is first so users complete it before chatting
    tab_setup, tab_chat, tab_quick = st.tabs(["Setup", "Chat", "Quick Questions"])

    with tab_setup:
        render_setup_tab()

    with tab_chat:
        render_chat_tab()

    with tab_quick:
        render_quick_questions_tab()


# ==============================================================================
# RUN THE APPLICATION
# ==============================================================================

if __name__ == "__main__":
    main()
