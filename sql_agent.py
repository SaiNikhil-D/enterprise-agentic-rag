import os
import sqlite3
import re

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# Configuration
# ============================================================

DB_PATH = "data/structured/company.db"


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:

    raise ValueError(
        "GROQ_API_KEY was not found in .env"
    )


# ============================================================
# Groq client
# ============================================================

llm = Groq(
    api_key=api_key
)


# ============================================================
# Database schema
# ============================================================

SCHEMA = """
TABLE employees:

employee_id INTEGER
name TEXT
department TEXT
role TEXT
location TEXT
annual_leave INTEGER
sick_leave INTEGER


TABLE departments:

department_id INTEGER
department_name TEXT
employee_count INTEGER
manager TEXT
"""


# ============================================================
# Generate SQL
# ============================================================

def generate_sql(question):

    prompt = f"""
You are an SQL generation agent.

Convert the user's question into a SQLite SELECT query.

Database schema:

{SCHEMA}

Rules:

1. Generate ONLY a SELECT statement.
2. Never generate INSERT.
3. Never generate UPDATE.
4. Never generate DELETE.
5. Never generate DROP.
6. Never generate ALTER.
7. Never generate CREATE.
8. Do not use tables that are not in the schema.
9. Return ONLY SQL.
10. Do not use markdown code fences.

User question:

{question}
"""


    response = llm.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0

    )


    sql = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


    # Remove code fences if returned
    sql = sql.replace(
        "```sql",
        ""
    )

    sql = sql.replace(
        "```",
        ""
    )

    return sql.strip()


# ============================================================
# Validate SQL
# ============================================================

def validate_sql(sql):

    sql_clean = sql.strip().lower()


    # Must start with SELECT
    if not sql_clean.startswith("select"):

        raise ValueError(
            "Only SELECT queries are allowed."
        )


    # Block dangerous operations
    forbidden = [

        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "replace ",
        "truncate "

    ]


    for keyword in forbidden:

        if keyword in sql_clean:

            raise ValueError(
                f"Unsafe SQL detected: {keyword}"
            )


    return True


# ============================================================
# Execute SQL
# ============================================================

def execute_sql(sql):

    validate_sql(sql)


    connection = sqlite3.connect(
        DB_PATH
    )

    cursor = connection.cursor()


    try:

        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]


    finally:

        connection.close()


    return columns, rows


# ============================================================
# Generate natural language answer
# ============================================================

def generate_answer(
    question,
    sql,
    columns,
    rows
):

    result_text = str(
        [
            dict(
                zip(columns, row)
            )
            for row in rows
        ]
    )


    prompt = f"""
You are an enterprise SQL assistant.

Answer the user's question using the database result.

User question:

{question}

SQL query:

{sql}

Database result:

{result_text}

Give a concise and clear answer.

Do not invent information.
"""


    response = llm.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0

    )


    return (
        response
        .choices[0]
        .message
        .content
    )


# ============================================================
# SQL Agent Node
# ============================================================

def sql_agent_node(state):

    question = state["question"]


    print(
        "\n[SQL AGENT] Processing question..."
    )


    sql = generate_sql(
        question
    )


    print(
        "\nGenerated SQL:"
    )

    print(sql)


    columns, rows = execute_sql(
        sql
    )


    answer = generate_answer(

        question,

        sql,

        columns,

        rows

    )


    return {

        "answer": answer,

        "next_agent": "SQL"

    }