import os
import streamlit as st
from load_documents import load_documents, add_documents_to_index, retrieve_relevant_documents
from gemini import generate_response
from utils import load_env

# Load environment variables
load_env()

# Set page configuration for dark theme
st.set_page_config(
    page_title="RAG Based with Document Upload",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS for dark theme
st.markdown(
    """
    <style>
    body { background-color: #1e1e1e; color: #ffffff; }
    .stApp { background-color: #1e1e1e; }
    .stTextInput input { background-color: #3e3e3e; color: #ffffff; }
    .stButton button { background-color: #4e4e4e; color: #ffffff; }
    .chat-bubble-user {
        background-color: #2e4a7a;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
    }
    .chat-bubble-bot {
        background-color: #2e2e2e;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App
def main():
    st.title("RAG Document Q&A ChatBot")

    # Sidebar for file uploads
    st.sidebar.header("Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Upload .txt, .pdf, .docx, or .xlsx files", 
        type=["txt", "pdf", "docx", "xlsx"], 
        accept_multiple_files=True
    )

    # Track already-indexed files to prevent duplicate indexing on Streamlit reruns
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()

    if uploaded_files:
        os.makedirs("temp", exist_ok=True)
        new_files = 0
        for uploaded_file in uploaded_files:
            if uploaded_file.name in st.session_state.processed_files:
                continue
            file_path = f"temp/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            load_documents(file_path)
            st.session_state.processed_files.add(uploaded_file.name)
            new_files += 1
        if new_files > 0:
            add_documents_to_index()
            st.sidebar.success(f"{new_files} new file(s) processed and added to the index!")
        else:
            st.sidebar.info("All uploaded files are already indexed.")

    # Show indexed files list in sidebar
    if st.session_state.get("processed_files"):
        st.sidebar.markdown("**Indexed files:**")
        for fname in sorted(st.session_state.processed_files):
            st.sidebar.markdown(f"- {fname}")

    # Initialize chat history
    if "history" not in st.session_state:
        st.session_state.history = []

    # Chat interface
    st.header("Chat")

    # Display full conversation history
    for entry in st.session_state.history:
        if "user" in entry:
            st.markdown(
                f'<div class="chat-bubble-user">🧑 <strong>You:</strong> {entry["user"]}</div>',
                unsafe_allow_html=True,
            )
        elif "bot" in entry:
            st.markdown(
                f'<div class="chat-bubble-bot">🤖 <strong>Chatbot:</strong> {entry["bot"]}</div>',
                unsafe_allow_html=True,
            )

    user_query = st.text_input("Enter your query:", key="user_query")
    col1, col2 = st.columns([1, 6])
    with col1:
        send = st.button("Send")
    with col2:
        if st.button("Clear Chat"):
            st.session_state.history = []
            st.rerun()

    if send:
        if not st.session_state.processed_files:
            st.warning("Please upload at least one document before querying.")
        elif user_query.strip():
            retrieved_docs = retrieve_relevant_documents(user_query)
            st.session_state.history.append({"user": user_query})
            bot_response = generate_response(user_query, retrieved_docs, st.session_state.history)
            st.session_state.history.append({"bot": bot_response})
            st.rerun()

if __name__ == "__main__":
    # Ensure the temp directory exists
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Run Streamlit app
    main()
