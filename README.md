# 🧠 Text-to-SQL Clarification Engine

Ask your MySQL database in plain English — powered by a **local LLM** (Ollama) with a **clarification loop** that asks follow-up questions when your query is ambiguous.

No data leaves your machine. Read-only by design.

---

## ✨ Features

- 🗣️ **Natural language → SQL** using a local LLM (Ollama + Qwen2.5-Coder)
- ❓ **Clarification engine** — asks follow-up questions when the query is ambiguous
- ⚡ **Skip button** — force SQL generation if you don't want to clarify
- 🗄️ **Multi-database dropdown** — pick any MySQL database on your server
- 👀 **Schema viewer** — inspect tables and columns before asking
- 🔒 **Read-only safety** — only `SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN` allowed
- 📊 **Results + NL summary** — see the table and a plain-English explanation
- 💬 **Conversation history** — track your questions and answers
- 🎨 **Clean Streamlit UI**


📂 Project Structure

text-to-sql-clarification-engine/
├── app.py              # Streamlit UI + orchestration
├── db.py               # MySQL connection, schema, query runner
├── llm.py              # Ollama: ambiguity, SQL generation, summary
├── setup_db.sql        # Sample database + table
├── requirements.txt
├── .env                # (not committed)
└── README.md



Create a .env file
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=school
OLLAMA_MODEL=qwen2.5-coder:7b



## 📦 Installation
ollama pull qwen2.5-coder:7b




### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/text-to-sql-clarification-engine.git
cd text-to-sql-clarification-engine

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate



▶️ Run
streamlit run app.py



