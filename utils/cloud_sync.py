# utils/cloud_sync.py

from datetime import datetime
import streamlit as st

def simulate_sync():
    """Simulates a simple cloud sync indicator in the sidebar."""
    st.sidebar.markdown("☁️ **Cloud Sync**")

    # Check for last sync time
    last_sync = st.session_state.get("last_sync", None)

    # Button to manually trigger sync
    if st.sidebar.button("🔄 Sync Now"):
        st.session_state["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.sidebar.success("✅ Synced with cloud")

    # Show last sync timestamp
    if last_sync:
        st.sidebar.markdown(f"🕒 Last Sync: `{last_sync}`")
