import os
import streamlit as st

KEY_NAME = "GOOGLE_API_KEY"


def get_api_key():
    """Returns the API key from environment or Streamlit secrets."""
    env_key = os.environ.get(KEY_NAME)
    if env_key:
        return env_key.strip()

    if hasattr(st, "secrets"):
        secret_key = st.secrets.get(KEY_NAME, "")
        if secret_key:
            return secret_key.strip()

    return ""


def set_session_api_key(api_key: str):
    """Store the API key only for the current session."""
    st.session_state[KEY_NAME] = api_key.strip()


def get_session_api_key():
    return st.session_state.get(KEY_NAME, "")
