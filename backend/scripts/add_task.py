import psycopg2

import sys
sys.path.insert(0, '/app') 

from db_operations.db_operations import create_task_with_files

conn = psycopg2.connect(
    host="db",
    port=5432,
    user="postgres",
    password="password",
    database="postgres"
)

# Przykładowe zadanie
files = [
    {"path": "root/index.html", "language": "html", "content": "<html>...</html>"},
    {"path": "root/app.js",   "language": "javascript", "content": "console.log('XSS')"}
]

task_id = create_task_with_files(
    conn,
    title="XSS Challenge #1",
    difficulty="medium",
    languages=["html", "javascript"],
    description="Znajdź i wykorzystaj podatność XSS.",
    files=files,
    tags=["web", "xss"]
)
print(f"Created task with ID {task_id}")
conn.close()