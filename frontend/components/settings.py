import streamlit as st
from frontend.utils.api_client import APIClient

api = APIClient()


def render_settings():
    token = st.session_state.access_token

    st.markdown("## ⚙️ Settings")

    profile = api.get_profile(token)
    settings_data = profile.get("settings", {}) if "error" not in profile else {}

    theme = st.selectbox(
        "Theme",
        ["light", "dark"],
        index=0 if settings_data.get("preferred_theme", st.session_state.theme) == "light" else 1,
    )

    model = st.selectbox(
        "AI Model",
        ["gemini", "groq"],
        index=0 if settings_data.get("preferred_model", "gemini") == "gemini" else 1,
        help="Gemini is primary. Groq is used as fallback if configured.",
    )

    if st.button("Save Settings", type="primary"):
        result = api.update_settings(token, {
            "preferred_theme": theme,
            "preferred_model": model,
        })
        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state.theme = theme
            st.success("Settings saved!")
            st.rerun()

    st.divider()
    st.markdown("### About")
    st.info(
        "AI Interview Preparation Assistant v1.0\n\n"
        "- Technical Interview: Concepts & mock interviews (no code)\n"
        "- Coding Assessment: Full DSA solutions with code\n"
        "- HR Interview: Behavioral & STAR method practice\n"
        "- Non-Technical: Aptitude, Communication, GD"
    )

    if st.button("← Back to Chat"):
        st.session_state.show_settings = False
        st.rerun()
