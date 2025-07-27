# utils/auth.py

import streamlit as st

# Dummy user database
USERS = {
    "admin": "admin123",
    "doctor": "docpass"
}

def login():
    """Simple login system via sidebar."""
    with st.sidebar:
        st.subheader("🔐 Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if USERS.get(username) == password:
                st.session_state["authenticated"] = True
                st.success(f"✅ Welcome, {username}!")
            else:
                st.error("❌ Invalid credentials")

    return st.session_state.get("authenticated", False)
