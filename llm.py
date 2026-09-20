import os
import json
import logging
import ollama
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")


AMBIGUITY_PROMPT = """You are a MySQL expert. Decide if the user's question is ambiguous given the schema.

Ambiguous means: unclear which table, column, value, or filter the user means.
If the question is clear enough to write a SQL query, it is NOT ambiguous.

Schema:
{schema}

Respond ONLY with valid JSON, nothing else:
{{"ambiguous": true/false, "reason": "short reason", "questions": ["question1"]}}

If not ambiguous, questions must be an empty list.
"""

SQL_PROMPT = """You are a MySQL expert. Convert the user's question into a valid MySQL query.

STRICT RULES:
- Use ONLY the tables and columns listed in the schema below.
- NEVER invent a column or table name.
- ALWAYS include a FROM clause.
- Only output the raw SQL query — no explanation, no markdown, no backticks.
- Use SELECT only.

Schema:
{schema}

Examples of correct output:
SELECT COUNT(*) FROM employees;
SELECT name FROM students WHERE class = 'Data Science';

Now write the SQL for the user's question.
"""

SUMMARY_PROMPT = """You are a data analyst. The user asked a question and got these results.

Question: {question}
Columns: {columns}
Rows: {rows}

Write a short, clear natural-language answer (1-2 sentences).
"""


def check_ambiguity(question, schema):
    prompt = AMBIGUITY_PROMPT.format(schema=schema)
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": f"{prompt}\nQuestion: {question}"}]
    )
    raw = response["message"]["content"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("not a dict")
        parsed.setdefault("ambiguous", False)
        parsed.setdefault("reason", "")
        parsed.setdefault("questions", [])
        return parsed
    except Exception as e:
        logger.warning(f"Ambiguity JSON parse failed: {e} | raw={raw[:200]}")
        return {"ambiguous": False, "reason": "parse failed", "questions": []}


def generate_sql(question, schema):
    prompt = SQL_PROMPT.format(schema=schema)
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": f"{prompt}\nQuestion: {question}"}]
    )
    sql = response["message"]["content"].strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def summarize(question, columns, rows):
    prompt = SUMMARY_PROMPT.format(question=question, columns=columns, rows=rows)
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()