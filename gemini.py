from google import genai
from google.genai import types, errors
from utils import load_env
import os
import time
import streamlit as st

# Load environment variables
load_env()

# Initialize the new Google GenAI client with automatic retry on 429/5xx
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        api_version="v1alpha",     # preview models require v1alpha
        retry_options=types.HttpRetryOptions(
            attempts=4,
            initial_delay=10000,   # 10s initial delay (respects the ~10s retry hint)
            max_delay=60000,       # 60s max delay
            exp_base=2.0,
            jitter=True,
            http_status_codes=[429, 500, 502, 503],
        ),
    ),
)

# Generation configuration using the new types API
generation_config = types.GenerateContentConfig(
    temperature=0.3,
    top_p=0.95,
    top_k=40,
    max_output_tokens=8192,
    system_instruction=(
        "You are a precise document Q&A assistant. Answer questions strictly based on the "
        "provided context. If the context does not contain enough information to fully answer "
        "the query, clearly state what is and isn't covered — do not infer, speculate, or "
        "add information beyond what is explicitly present in the context."
    ),
)

# Create a persistent chat session
chat_session = client.chats.create(
    model="gemini-3.1-flash-lite-preview",
    config=generation_config,
)

# Function to generate a response using Google Gemini API
def generate_response(query, retrieved_docs, chat_history):
    context = "\n".join(retrieved_docs)
    prompt = f"""Context:
{context}

History:
{chat_history}

Query:
{query}"""
    try:
        response = chat_session.send_message(prompt)
        return response.text.strip()
    except errors.APIError as e:
        if e.code == 429:
            st.error("Rate limit reached. The app will retry automatically — please wait a moment and try again.")
        else:
            st.error(f"API error ({e.code}): {e.message}")
        return "Sorry, I couldn't generate a response."
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return "Sorry, I couldn't generate a response."
