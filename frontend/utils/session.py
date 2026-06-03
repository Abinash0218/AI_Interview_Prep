import streamlit as st

CATEGORIES = [
    "technical_interview",
    "coding_assessment",
    "hr_interview",
    "non_technical_skills",
]


def init_session_state():
    defaults = {
        "authenticated": False,
        "access_token": None,
        "user": None,
        "current_chat_id": None,
        "current_category": "technical_interview",
        "last_active_category": "technical_interview",
        "messages": [],
        "theme": "light",
        "chat_history": {},
        "show_profile": False,
        "auth_page": "login",
        "search_query": "",
        "category_chats": {cat: {"chat_id": None, "messages": []} for cat in CATEGORIES},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    _sync_category_chats_from_legacy()


def _sync_category_chats_from_legacy():
    """Keep per-tab storage in sync with legacy keys when loading old chats."""
    if st.session_state.get("current_category") and st.session_state.get("messages") is not None:
        cat = st.session_state.current_category
        if cat in st.session_state.category_chats:
            st.session_state.category_chats[cat] = {
                "chat_id": st.session_state.get("current_chat_id"),
                "messages": st.session_state.get("messages", []),
            }


def get_category_chat(category: str) -> dict:
    init_session_state()
    if category not in st.session_state.category_chats:
        st.session_state.category_chats[category] = {"chat_id": None, "messages": []}
    return st.session_state.category_chats[category]


def set_category_chat(category: str, chat_id, messages: list):
    init_session_state()
    st.session_state.category_chats[category] = {
        "chat_id": chat_id,
        "messages": messages or [],
    }
    st.session_state.current_category = category
    st.session_state.last_active_category = category
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = messages or []


def clear_category_chat(category: str):
    set_category_chat(category, None, [])


def login_user(token: str, user: dict, theme: str = "light"):
    st.session_state.authenticated = True
    st.session_state.access_token = token
    st.session_state.user = user
    st.session_state.theme = theme


def logout_user():
    keys_to_clear = [
        "authenticated", "access_token", "user", "current_chat_id",
        "messages", "chat_history", "show_profile", "category_chats",
        "last_active_category", "settings_loaded",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.authenticated = False
    st.session_state.auth_page = "login"
