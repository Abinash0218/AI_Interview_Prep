import streamlit as st
from frontend.utils.api_client import APIClient

api = APIClient()


def render_profile():
    token = st.session_state.access_token

    st.markdown("## 👤 Profile")

    profile = api.get_profile(token)
    if "error" in profile:
        st.error(profile["error"])
        return

    with st.form("profile_form"):
        full_name = st.text_input("Full Name", value=profile.get("full_name", ""))
        email = st.text_input("Email", value=profile.get("email", ""), disabled=True)

        if st.form_submit_button("Save Profile", use_container_width=True, type="primary"):
            result = api.update_profile(token, {"full_name": full_name})
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.user["full_name"] = full_name
                st.success("Profile updated!")
                st.rerun()

    if st.button("← Back to Chat", use_container_width=True):
        st.session_state.show_profile = False
        st.rerun()
