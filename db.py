import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection(database=None):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=database
    )

def list_databases():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SHOW DATABASES")
    dbs = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return dbs

def get_schema(database):
    conn = get_connection(database)
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]

    schema_lines = []
    for table in tables:
        cur.execute(f"DESCRIBE `{table}`")
        cols = cur.fetchall()
        col_defs = ", ".join([f"{c[0]} {c[1]}" for c in cols])
        schema_lines.append(f"{table}({col_defs})")

    cur.close()
    conn.close()
    return "\n".join(schema_lines) if schema_lines else "(no tables)"

def run_query(database, sql):
    allowed = ("select", "show", "describe", "desc", "explain")
    if not sql.strip().lower().startswith(allowed):
        raise ValueError("Only read-only queries (SELECT/SHOW/DESCRIBE/EXPLAIN) are allowed.")

    conn = get_connection(database)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description] if cur.description else []
    cur.close()
    conn.close()
    return columns, rows