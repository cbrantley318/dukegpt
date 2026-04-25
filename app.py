"""
app.py
Streamlit web UI for the Duke AI Assistant.
Covers the 10-pt "deployed as functional web application with UI" rubric item.

Run with:
    streamlit run app.py
"""

import streamlit as st
from bot.chat import chat, reset_conversation
from rag.retriever import build_index

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DukeBot — AI Student Assistant",
    page_icon="🔵",
    layout="centered",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("DukeBot Settings")

    model_key = st.selectbox(
        "Embedding model",
        options=["minilm", "mpnet"],
        help="MiniLM is faster; MPNet is more accurate. Compare both in your eval!"
    )

    use_rag = st.toggle("Use Duke knowledge base", value=True)

    if st.button("Rebuild knowledge index"):
        with st.spinner("Building index from Duke docs..."):
            build_index(model_key=model_key)
        st.success("Index rebuilt!")

    if st.button("Clear conversation"):
        st.session_state.history = reset_conversation()
        st.session_state.latencies = []
        st.rerun()

    st.divider()
    st.caption("Duke University AI Assistant")
    st.caption("Built for CS 372 Final Project")

    # Show latency stats if available
    if "latencies" in st.session_state and st.session_state.latencies:
        avg = sum(st.session_state.latencies) / len(st.session_state.latencies)
        st.metric("Avg response time", f"{avg:.2f}s")

# ── Initialize session state ──────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = reset_conversation()
if "latencies" not in st.session_state:
    st.session_state.latencies = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🔵 DukeBot")
st.caption("Your AI assistant for Duke University — ask about dining, library hours, academic deadlines, and more.")

# ── Chat display ──────────────────────────────────────────────────────────────
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything about Duke..."):

    # Show user message immediately
    st.session_state.display_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply, st.session_state.history, latency, context = chat(
                prompt,
                st.session_state.history,
                use_rag=use_rag,
                model_key=model_key,
            )
        st.write(reply)

        # Optionally show retrieved context (useful for demo/debugging)
        if use_rag and context:
            with st.expander("📚 Sources retrieved from Duke knowledge base"):
                st.text(context)

    st.session_state.display_messages.append({"role": "assistant", "content": reply})
    st.session_state.latencies.append(latency)
