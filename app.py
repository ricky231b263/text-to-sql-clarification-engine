import streamlit as st
from db import list_databases, get_schema, run_query
from llm import check_ambiguity, generate_sql, summarize

st.set_page_config(
    page_title="Text to SQL",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .result-card {
        background: #f9fafb;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }
    .chat-user {
        background: #eef2ff;
        padding: 0.6rem 0.9rem;
        border-radius: 8px;
        margin: 0.3rem 0;
    }
    .chat-bot {
        background: #ecfdf5;
        padding: 0.6rem 0.9rem;
        border-radius: 8px;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 Text to SQL</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask in plain English — powered by a local LLM (Ollama) and MySQL.</div>', unsafe_allow_html=True)

# ---------- Session state ----------
defaults = {
    "db": None,
    "history": [],
    "pending": None,
    "final_question": None,
    "schema_cache": {},
    "last_result": None,
    "chat_log": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")

    databases = list_databases()
    db = st.selectbox("Database", databases, index=0)

    if db != st.session_state.db:
        st.session_state.db = db
        st.session_state.history = []
        st.session_state.pending = None
        st.session_state.final_question = None
        st.session_state.last_result = None

    st.divider()
    st.caption(f"**Model:** qwen2.5-coder:7b")
    st.caption("All processing is local. No data leaves your machine.")

    st.divider()
    with st.expander("📋 Schema viewer"):
        if st.session_state.db not in st.session_state.schema_cache:
            st.session_state.schema_cache[st.session_state.db] = get_schema(st.session_state.db)
        schema_view = st.session_state.schema_cache[st.session_state.db]
        st.code(schema_view if schema_view else "(no tables)", language="text")

    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.pending = None
        st.session_state.final_question = None
        st.session_state.chat_log = []
        st.session_state.last_result = None
        st.rerun()


# ---------- Helpers ----------
def get_cached_schema(db_name):
    if db_name not in st.session_state.schema_cache:
        st.session_state.schema_cache[db_name] = get_schema(db_name)
    return st.session_state.schema_cache[db_name]


def build_question(base):
    q = base
    for h in st.session_state.history:
        q += f"\n(Clarification: {h['answer']})"
    return q


# ---------- Main input area ----------
st.markdown("### 💬 Ask your question")
question = st.text_input(
    "Question",
    placeholder="e.g. Show all employees in the Sales department",
    label_visibility="collapsed",
)

c1, c2, c3 = st.columns([1, 1, 3])
with c1:
    ask_btn = st.button("🚀 Ask", use_container_width=True, type="primary")
with c2:
    skip_btn = st.button("⚡ Skip clarification", use_container_width=True)


# ---------- Handle Ask ----------
if ask_btn and question.strip():
    st.session_state.history = []
    st.session_state.pending = None
    st.session_state.last_result = None
    st.session_state.chat_log.append({"role": "user", "text": question})

    schema = get_cached_schema(st.session_state.db)
    with st.spinner("🤔 Analyzing your question..."):
        result = check_ambiguity(question, schema)

    if result.get("ambiguous") and result.get("questions"):
        st.session_state.pending = result
        st.session_state.chat_log.append({
            "role": "bot",
            "text": f"Need clarification: {result.get('reason','')}"
        })
    else:
        st.session_state.final_question = question

if skip_btn and question.strip():
    st.session_state.final_question = build_question(question)
    st.session_state.pending = None


# ---------- Clarification loop ----------
if st.session_state.pending:
    result = st.session_state.pending
    st.markdown("---")
    st.warning(f"**Ambiguity detected:** {result.get('reason', '')}")

    for i, q in enumerate(result.get("questions", [])):
        ans = st.text_input(f"❓ {q}", key=f"clarify_{i}")
        if st.button(f"Submit answer", key=f"sub_{i}"):
            if ans.strip():
                st.session_state.history.append({"question": q, "answer": ans})
                st.session_state.chat_log.append({"role": "user", "text": f"(answer) {ans}"})
                schema = get_cached_schema(st.session_state.db)
                combined = build_question(question)
                with st.spinner("🔍 Re-checking..."):
                    new_result = check_ambiguity(combined, schema)
                if new_result.get("ambiguous") and new_result.get("questions"):
                    st.session_state.pending = new_result
                else:
                    st.session_state.final_question = combined
                    st.session_state.pending = None
                st.rerun()


# ---------- Final: SQL + results ----------
if st.session_state.final_question:
    q = st.session_state.final_question
    schema = get_cached_schema(st.session_state.db)

    st.markdown("---")

    with st.spinner("🧩 Generating SQL..."):
        sql = generate_sql(q, schema)

    st.markdown("### 🧾 Generated SQL")
    st.code(sql, language="sql")

    try:
        with st.spinner("⚙️ Running query..."):
            columns, rows = run_query(st.session_state.db, sql)

        st.markdown("### 📊 Results")
        if rows:
            st.dataframe(
                [dict(zip(columns, row)) for row in rows],
                use_container_width=True,
                hide_index=True,
            )

            with st.spinner("✍️ Summarizing..."):
                summary = summarize(q, columns, rows)

            st.markdown("### 💡 Summary")
            st.success(summary)

            st.session_state.last_result = {"columns": columns, "rows": rows}
            st.session_state.chat_log.append({"role": "bot", "text": summary})
        else:
            st.info("No results found.")
            st.session_state.chat_log.append({"role": "bot", "text": "No results found."})
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.session_state.chat_log.append({"role": "bot", "text": f"Error: {e}"})

    # Follow-up hint
    st.caption("💬 Tip: ask a follow-up — previous clarification answers are remembered.")


# ---------- Chat log ----------
if st.session_state.chat_log:
    st.markdown("---")
    with st.expander("🕘 Conversation history", expanded=False):
        for entry in st.session_state.chat_log:
            if entry["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 <b>You:</b> {entry["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">🤖 <b>Bot:</b> {entry["text"]}</div>', unsafe_allow_html=True)