import os
import streamlit as st
from dotenv import load_dotenv

def load_env():
    # Locally: reads from .env file
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    # Streamlit Cloud: secrets are stored in st.secrets, not .env
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
        except Exception:
            pass

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Set it in your .env file (local) or Streamlit secrets (deployed)."
        )
