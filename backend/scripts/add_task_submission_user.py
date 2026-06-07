import psycopg2
import sys

sys.path.insert(0, '/app')

from db_operations.db_operations import create_task_with_files, submit_solution, enqueue_solution_check
from verification import check_submission

conn = psycopg2.connect(
    host="db",
    port=5432,
    user="postgres",
    password="password",
    database="postgres"
)

# 1. Create a task
task_files = [
    {"path": "root/index.html", "language": "html", "content": "<html>...</html>"},
    {"path": "root/app.js",   "language": "javascript", "content": "console.log('XSS')"}
]

task_id = create_task_with_files(
    conn,
    title="XSS Challenge #1",
    difficulty="medium",
    languages=["html", "javascript"],
    description="Znajdź i wykorzystaj podatność XSS.",
    files=task_files,
    tags=["web", "xss"]
)
print(f"Created task with ID {task_id}")

# 2. Ensure a test user exists (or create one)
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO users (id, Uname, Usurename, user_type)
    VALUES (1, 'testuser', 'testuser', 'student')
    ON CONFLICT (id) DO NOTHING
""")
conn.commit()
cursor.close()

# 3. Submit a solution for that user
submission_files = [
    {"path": "root/index.html", "language": "html", "content": "<html><script>alert(1)</script></html>"},
    {"path": "root/app.js",   "language": "javascript", "content": "document.write(location.hash)"}
]

submission_id = submit_solution(
    db=conn,
    user_id=1,
    task_id=task_id,
    files=submission_files
)
enqueue_solution_check(conn, submission_id)
check_submission(conn, submission_id)

print(f"Created submission with ID {submission_id}")

conn.close()