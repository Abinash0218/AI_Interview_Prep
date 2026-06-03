import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.utils.session import get_category_chat, set_category_chat, clear_category_chat

api = APIClient()

TABS = [
    ("technical_interview", "💻 Technical Interview"),
    ("coding_assessment", "🧮 Coding Assessment"),
    ("hr_interview", "👔 HR Interview"),
    ("non_technical_skills", "📚 Non-Technical Skills"),
]

TAB_DESCRIPTIONS = {
    "technical_interview": "Prepare for DSA theory, DBMS, OS, Networks, System Design, and mock technical interviews. **No code solutions** — use Coding Assessment for that.",
    "coding_assessment": "Get complete coding solutions with brute force, optimized approach, complexity analysis, and dry runs.",
    "hr_interview": "Practice behavioral questions, STAR method, mock HR interviews, and communication feedback.",
    "non_technical_skills": "Aptitude, Communication Skills, and Group Discussion practice. **No coding** — use Coding Assessment for that.",
}

FAQS = {
    "technical_interview": [
        "What are ACID properties in DBMS?",
        "Explain stack vs queue",
        "How to prepare for system design?",
    ],
    "coding_assessment": [
        "Solve two sum problem",
        "Explain binary search approach",
        "What is dynamic programming?",
    ],
    "hr_interview": [
        "Tell me about yourself",
        "Strengths and weaknesses",
        "Explain STAR method",
    ],
    "non_technical_skills": [
        "Aptitude percentage question",
        "Professional email writing tips",
        "Group discussion on current affairs",
    ],
}


def _messages_to_text(messages: list) -> str:
    lines = []
    for m in messages:
        role = "You" if m["role"] == "user" else "Assistant"
        lines.append(f"{role}:\n{m['content']}")
    return "\n\n".join(lines)


def _send_message(token: str, category: str, message: str):
    state = get_category_chat(category)
    with st.spinner("Thinking..."):
        result = api.send_chat(
            token,
            message,
            category,
            state.get("chat_id"),
        )
    if "error" in result:
        st.error(result["error"])
    else:
        set_category_chat(
            category,
            result["chat_id"],
            result.get("messages", []),
        )
        st.rerun()


def render_chat_interface():
    token = st.session_state.access_token
    tab_labels = [t[1] for t in TABS]
    tab_keys = [t[0] for t in TABS]

    selected = st.tabs(tab_labels)
    for idx, tab in enumerate(selected):
        with tab:
            category = tab_keys[idx]
            st.session_state.last_active_category = category
            render_category_chat(token, category, tab_labels[idx])


def _render_faq_suggestions(token: str, category: str):
    faqs = FAQS.get(category, [])
    if not faqs:
        return

    st.markdown('<p class="faq-label">Suggested questions — click to ask:</p>', unsafe_allow_html=True)
    cols = st.columns(len(faqs))
    for i, question in enumerate(faqs):
        with cols[i]:
            if st.button(question, key=f"faq_{category}_{i}", use_container_width=True, type="secondary"):
                _send_message(token, category, question)


def render_chat_actions(token: str, chat_id: int, messages: list, category: str):
    c1, c2, c3, _ = st.columns([1, 1, 1, 8])

    with c1:
        pdf_result = api.export_pdf(token, chat_id)
        if "content" in pdf_result:
            st.download_button(
                label="",
                icon=":material/download:",
                data=pdf_result["content"],
                file_name=f"chat_{chat_id}.pdf",
                mime="application/pdf",
                key=f"dl_pdf_{chat_id}",
                help="Download PDF",
            )
        else:
            st.button("", icon=":material/download:", disabled=True, key=f"dl_pdf_dis_{chat_id}", help="Download PDF")

    with c2:
        chat_text = _messages_to_text(messages)
        st.download_button(
            label="",
            icon=":material/content_copy:",
            data=chat_text,
            file_name=f"chat_{chat_id}.txt",
            mime="text/plain",
            key=f"copy_txt_{chat_id}",
            help="Copy chat as text",
        )

    with c3:
        if st.button("", icon=":material/delete:", key=f"del_chat_{chat_id}", help="Delete chat"):
            api.delete_chat(token, chat_id)
            clear_category_chat(category)
            st.rerun()


def render_category_chat(token: str, category: str, tab_name: str):
    if st.session_state.get("show_profile"):
        return

    st.markdown(
        f'<p class="tab-desc">{TAB_DESCRIPTIONS.get(category, "")}</p>',
        unsafe_allow_html=True,
    )

    state = get_category_chat(category)
    messages = state.get("messages", [])
    chat_id = state.get("chat_id")

    for msg in messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    if messages and chat_id:
        render_chat_actions(token, chat_id, messages, category)

    # FAQs only before first message in this tab
    if not messages:
        _render_faq_suggestions(token, category)

    clean_name = tab_name.replace("💻 ", "").replace("🧮 ", "").replace("👔 ", "").replace("📚 ", "")
    prompt = st.chat_input(f"Ask about {clean_name}...", key=f"chat_input_{category}")
    if prompt:
        _send_message(token, category, prompt)
