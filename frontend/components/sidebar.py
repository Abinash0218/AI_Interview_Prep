import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.utils.session import logout_user, set_category_chat, clear_category_chat, get_category_chat

api = APIClient()


def load_chat_history(token: str, search: str = ""):
    result = api.get_chat_history(token, search if search else None)
    if "error" not in result:
        st.session_state.chat_history = result.get("chats", {})


def render_sidebar():
    token = st.session_state.access_token
    user = st.session_state.user

    with st.sidebar:
        st.markdown("### Menu")

        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            cat = st.session_state.get("last_active_category", "technical_interview")
            clear_category_chat(cat)
            st.session_state.show_profile = False
            st.rerun()

        search = st.text_input(
            "🔍 Search Chats",
            value=st.session_state.get("search_query", ""),
            key="sidebar_search",
        )
        if search != st.session_state.get("search_query", ""):
            st.session_state.search_query = search
            load_chat_history(token, search)

        load_chat_history(token, st.session_state.get("search_query", ""))

        st.markdown("---")
        st.markdown("**Chat History**")

        history = st.session_state.get("chat_history", {})
        if not history:
            st.caption("No chats yet. Start a new conversation!")
        else:
            for category_label, chats in history.items():
                st.markdown(f'<p class="sidebar-section">{category_label}</p>', unsafe_allow_html=True)
                for chat in chats:
                    col1, col2 = st.columns([4, 1])
                    chat_cat = chat.get("category", "")
                    is_active = (
                        chat_cat
                        and get_category_chat(chat_cat).get("chat_id") == chat["id"]
                    )
                    with col1:
                        label = f"{'📌 ' if is_active else ''}{chat['title'][:35]}"
                        if st.button(label, key=f"chat_{chat['id']}", use_container_width=True):
                            open_chat(token, chat["id"])
                    with col2:
                        if st.button("🗑", key=f"del_{chat['id']}", help="Delete"):
                            api.delete_chat(token, chat["id"])
                            for cat_key in st.session_state.get("category_chats", {}):
                                if st.session_state.category_chats[cat_key].get("chat_id") == chat["id"]:
                                    clear_category_chat(cat_key)
                                    break
                            load_chat_history(token)
                            st.rerun()

        st.markdown("---")

        if st.button("👤 Profile", use_container_width=True):
            st.session_state.show_profile = True
            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            api.logout(token)
            logout_user()
            st.rerun()

        if user:
            st.caption(f"Logged in as {user.get('full_name', 'User')}")


def open_chat(token: str, chat_id: int):
    result = api.get_chat(token, chat_id)
    if "error" not in result:
        category = result["category"]
        set_category_chat(category, chat_id, result.get("messages", []))
        st.session_state.show_profile = False
        st.rerun()
