import html
from urllib.parse import quote
import streamlit as st
import streamlit.components.v1 as components
from frontend.config import get_google_client_id, get_frontend_url
from frontend.utils.api_client import APIClient
from frontend.utils.session import login_user

api = APIClient()

GOOGLE_ICON_URL = "https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"


def _show_error(key: str, message: str):
    st.session_state[key] = message


def _clear_error(key: str):
    st.session_state.pop(key, None)


def _render_banner(message: str, kind: str = "error"):
    msg = html.escape(message)
    if kind == "success":
        style = "background:#f0fdf4;border:1px solid #bbf7d0;color:#166534;"
    elif kind == "info":
        style = "background:#f3f4f6;border:1px solid #e5e7eb;color:#4b5563;"
    else:
        style = "background:#fef2f2;border:1px solid #fecaca;color:#991b1b;"
    line_count = max(1, len(message) // 50 + 1)
    height = min(120, 36 + line_count * 22)
    components.html(
        f'<div style="{style}border-radius:8px;font-size:14px;font-weight:500;'
        f'padding:10px 14px;font-family:sans-serif;line-height:1.4;">{msg}</div>',
        height=height,
        scrolling=False,
    )


def _render_error(key: str):
    if st.session_state.get(key):
        _render_banner(st.session_state[key], "error")


def _render_success(key: str):
    if st.session_state.get(key):
        _render_banner(st.session_state[key], "success")


def _render_auth_header():
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:1rem;">
            <div style="font-size:1.35rem;font-weight:700;color:#1a1a2e;margin-bottom:6px;">
                Interview Prep AI
            </div>
            <div style="font-size:0.875rem;color:#6b7280;line-height:1.5;">
                Prepare for technical, coding, HR and soft-skill interviews
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_auth_styles():
    st.markdown(
        """
        <style>
        /* Auth tab radio — always visible */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }
        div[data-testid="stRadio"] > div {
            display: flex !important;
            gap: 0 !important;
            background: #f3f4f6 !important;
            border-radius: 10px !important;
            padding: 4px !important;
            width: 100% !important;
        }
        div[data-testid="stRadio"] > div > label {
            flex: 1 !important;
            display: flex !important;
            justify-content: center !important;
            background: transparent !important;
            border: none !important;
            padding: 8px 12px !important;
            margin: 0 !important;
            border-radius: 8px !important;
            cursor: pointer !important;
        }
        div[data-testid="stRadio"] > div > label > div {
            color: #4b5563 !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
        }
        div[data-testid="stRadio"] > div > label[data-checked="true"] {
            background: #ffffff !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        }
        div[data-testid="stRadio"] > div > label[data-checked="true"] > div {
            color: #dc2626 !important;
            font-weight: 600 !important;
        }

        /* White inputs */
        [data-testid="stTextInput"] input {
            background-color: #ffffff !important;
            color: #1a1a2e !important;
            border: 1px solid #d1d5db !important;
            -webkit-text-fill-color: #1a1a2e !important;
        }
        [data-testid="stTextInput"] > div > div,
        [data-testid="stTextInput"] [data-baseweb="base-input"],
        [data-testid="stTextInput"] [data-baseweb="input"] {
            background-color: #ffffff !important;
        }
        [data-testid="stTextInput"] input::placeholder {
            color: #9ca3af !important;
            -webkit-text-fill-color: #9ca3af !important;
        }
        [data-testid="stTextInput"] label,
        [data-testid="stTextInput"] label p {
            color: #374151 !important;
            font-weight: 500 !important;
        }

        /* Password show/hide eye icon — always visible */
        [data-testid="stTextInput"] button[kind="icon"],
        [data-testid="stTextInput"] button {
            opacity: 1 !important;
            visibility: visible !important;
            color: #6b7280 !important;
            background: transparent !important;
            border: none !important;
        }
        [data-testid="stTextInput"] button svg,
        [data-testid="stTextInput"] button path {
            fill: #6b7280 !important;
            color: #6b7280 !important;
        }
        [data-testid="stTextInput"] button:hover {
            color: #374151 !important;
            background: #f3f4f6 !important;
            border-radius: 4px !important;
        }
        [data-testid="stTextInput"] button:hover svg,
        [data-testid="stTextInput"] button:hover path {
            fill: #374151 !important;
        }

        /* Hide "Press Enter to submit form" */
        [data-testid="InputInstructions"] {
            display: none !important;
            height: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Centered "or" divider */
        .auth-divider {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 1.5rem 0 1.25rem !important;
            color: #6b7280 !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            text-transform: lowercase !important;
        }
        .auth-divider::before,
        .auth-divider::after {
            content: "" !important;
            flex: 1 !important;
            border-bottom: 1px solid #e5e7eb !important;
        }
        .auth-divider span {
            padding: 0 1rem !important;
        }

        /* Google sign-in link button */
        a.google-signin-btn {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 10px !important;
            width: 100% !important;
            padding: 11px 16px !important;
            background: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            color: #1a1a2e !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            box-sizing: border-box !important;
            margin: 0 !important;
        }
        a.google-signin-btn:hover {
            background: #f9fafb !important;
            border-color: #9ca3af !important;
            color: #1a1a2e !important;
        }
        a.google-signin-btn img {
            width: 18px !important;
            height: 18px !important;
            display: block !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_or_divider():
    st.html(
        """
        <div class="auth-divider" style="display:flex;align-items:center;width:100%;
            margin:24px 0 20px;color:#6b7280;font-size:13px;font-weight:500;">
            <div style="flex:1;border-bottom:1px solid #e5e7eb;"></div>
            <span style="padding:0 16px;">or</span>
            <div style="flex:1;border-bottom:1px solid #e5e7eb;"></div>
        </div>
        """
    )


def _handle_google_callback() -> bool:
    """Process Google OAuth redirect. Returns True if login succeeded."""
    code = st.query_params.get("code")
    if not code:
        return False

    frontend_url = get_frontend_url()
    with st.spinner("Signing in with Google..."):
        result = api.google_login(code=code, redirect_uri=frontend_url)

    st.query_params.clear()

    if "error" in result:
        st.session_state["auth_login_error"] = result["error"]
        return False

    login_user(result["access_token"], result["user"])
    st.rerun()
    return True


def _render_google_section():
    _render_or_divider()

    google_client_id = get_google_client_id()

    if google_client_id and not google_client_id.startswith("your-"):
        redirect_uri = get_frontend_url()
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={google_client_id}&"
            f"redirect_uri={quote(redirect_uri, safe='')}&"
            "response_type=code&"
            "scope=openid%20email%20profile&"
            "access_type=offline&"
            "prompt=select_account"
        )

        st.html(
            f"""
            <a href="{google_auth_url}" target="_self" style="display:flex;align-items:center;
                justify-content:center;gap:10px;width:100%;padding:11px 16px;background:#ffffff;
                border:1px solid #d1d5db;border-radius:8px;color:#1a1a2e;font-size:15px;
                font-weight:500;text-decoration:none;box-sizing:border-box;font-family:sans-serif;">
                <img src="{GOOGLE_ICON_URL}" alt="Google" width="18" height="18" />
                Continue with Google
            </a>
            """
        )
    else:
        st.info("Google sign-in is not configured. Add GOOGLE_CLIENT_ID to your .env file and restart Streamlit.")


def _render_login_tab():
    _render_error("auth_login_error")
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
        )
        submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")
        if submitted:
            if not email or not password:
                _show_error("auth_login_error", "Please enter email and password.")
                st.rerun()
            with st.spinner("Signing in..."):
                result = api.login(email, password)
            if "error" in result:
                _show_error("auth_login_error", result["error"])
                st.rerun()
            _clear_error("auth_login_error")
            login_user(result["access_token"], result["user"])
            st.rerun()


def _render_signup_tab():
    _render_error("auth_signup_error")
    with st.form("signup_form"):
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Min 8 characters",
            help="Uppercase, lowercase, and a number required",
        )
        confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter password",
        )
        submitted = st.form_submit_button("Create account", use_container_width=True, type="primary")
        if submitted:
            if password != confirm:
                _show_error("auth_signup_error", "Passwords do not match.")
                st.rerun()
            if not full_name or not email or not password:
                _show_error("auth_signup_error", "Please fill all fields.")
                st.rerun()
            with st.spinner("Creating account..."):
                result = api.signup(full_name, email, password)
            if "error" in result:
                _show_error("auth_signup_error", result["error"])
                st.rerun()
            _clear_error("auth_signup_error")
            login_user(result["access_token"], result["user"])
            st.rerun()


def render_auth_page():
    if _handle_google_callback():
        return

    st.markdown('<span class="auth-page-active"></span>', unsafe_allow_html=True)
    _inject_auth_styles()

    _, center, _ = st.columns([1, 1.1, 1], gap="large")

    with center:
        with st.container(border=True):
            _render_auth_header()

            auth_tab = st.radio(
                "Section",
                ["Login", "Sign Up"],
                horizontal=True,
                label_visibility="collapsed",
                key="auth_tab_selector",
            )

            if auth_tab == "Login":
                _render_login_tab()
            else:
                _render_signup_tab()

            _render_google_section()

    query_params = st.query_params
    if query_params.get("reset_token"):
        with center:
            with st.container(border=True):
                render_reset_password(query_params["reset_token"])


def render_reset_password(token: str):
    st.markdown("### Reset password")
    _render_error("auth_reset_error")
    _render_success("auth_reset_success")
    with st.form("reset_form"):
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password",
        )
        confirm = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter new password",
        )
        submitted = st.form_submit_button("Reset password", use_container_width=True, type="primary")
        if submitted:
            if new_password != confirm:
                st.error("Passwords do not match.")
            else:
                result = api.reset_password(token, new_password)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("Password reset successful! Please sign in.")
                    st.query_params.clear()
