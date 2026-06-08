import psycopg2
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/app')
from db_operations.db_operations import (
    create_task_with_files,
    submit_solution,
    enqueue_solution_check,
    insert_user,
)

conn = psycopg2.connect(
    host="db",
    port=5432,
    user="postgres",
    password="password",
    database="postgres"
)

def truncate_all(cursor):
    """Clean out existing data – order respects foreign keys."""
    tables = [
        "submission_results",
        "submissions",
        "user_task_status",
        "assigned_tasks",
        "course_tasks",
        "task_files",
        "task_tags",
        "tasks",
        "tags",
        "courses",
        "users",
    ]
    for t in tables:
        cursor.execute(f"TRUNCATE TABLE {t} CASCADE;")

try:
    cursor = conn.cursor()
    truncate_all(cursor)
    conn.commit()
    print("Cleared old data.")

    # ------- 1. Users -------
    insert_user(conn, 1, "Alice", "Student", "student")
    insert_user(conn, 2, "Bob", "Teacher", "teacher")
    print("Users inserted.")

    # ------- 2. Tasks with tags -------
    # Helper: each task gets a single stub file and a descriptive title.
    def make_stub_file(path, lang):
        return {"path": path, "language": lang, "content": f"// Stub content for {path}"}

    # Task 1 – topic1, easy, Java
    task1_id = create_task_with_files(
        conn,
        title="Task 1: Hello World",
        difficulty="easy",
        languages=["Java"],
        description="Stub description for Task 1.",
        files=[make_stub_file("root/Main.java", "java")],
        tags=["topic1", "java-basics"]
    )
    # Task 2 – topic1, medium, Java
    task2_id = create_task_with_files(
        conn,
        title="Task 2: Variables",
        difficulty="medium",
        languages=["Java"],
        description="Stub description for Task 2.",
        files=[make_stub_file("root/Main.java", "java")],
        tags=["topic1", "java-basics"]
    )
    # Task 3 – topic1, hard, Java
    task3_id = create_task_with_files(
        conn,
        title="Task 3: OOP Principles",
        difficulty="hard",
        languages=["Java"],
        description="Stub description for Task 3.",
        files=[make_stub_file("root/Main.java", "java")],
        tags=["topic1", "oop"]
    )
    # Task 4 – topic2, easy, Python
    task4_id = create_task_with_files(
        conn,
        title="Task 4: Python Intro",
        difficulty="easy",
        languages=["Python"],
        description="Stub description for Task 4.",
        files=[make_stub_file("root/main.py", "python")],
        tags=["topic2", "python-basics"]
    )
    # Task 5 – topic2, medium, Python
    task5_id = create_task_with_files(
        conn,
        title="Task 5: Data Structures",
        difficulty="medium",
        languages=["Python"],
        description="Stub description for Task 5.",
        files=[make_stub_file("root/main.py", "python")],
        tags=["topic2", "python-basics"]
    )
    # Task 6 – topic2, hard, Python
    task6_id = create_task_with_files(
        conn,
        title="Task 6: Web Scraping",
        difficulty="hard",
        languages=["Python"],
        description="Stub description for Task 6.",
        files=[make_stub_file("root/main.py", "python")],
        tags=["topic2", "web"]
    )
    # Task 7 – mixed tags, medium, JavaScript
    task7_id = create_task_with_files(
        conn,
        title="Task 7: DOM Manipulation",
        difficulty="medium",
        languages=["JavaScript"],
        description="Stub description for Task 7.",
        files=[make_stub_file("root/index.html", "html"), make_stub_file("root/app.js", "javascript")],
        tags=["web", "frontend"]
    )
    # Task 8 – theory (difficulty = 'theory' not allowed by CHECK, so use 'easy')
    # But your frontend had 'theory' – we'll treat it as a tag instead.
    task8_id = create_task_with_files(
        conn,
        title="Task 8: Theory Quiz",
        difficulty="easy",
        languages=[],
        description="Stub description for a theory exercise.",
        files=[],  # no files for theory tasks
        tags=["topic1", "theory"]
    )

    print("Tasks created.")

    # ------- 3. User progress (user_task_status) -------
    # Mix of statuses for user 1 (Alice)
    base_date = datetime(2020, 1, 1)
    status_data = [
        (1, task1_id, "inProgress", base_date),
        (1, task2_id, "new", None),
        (1, task3_id, "done", base_date + timedelta(days=2)),
        (1, task4_id, "done", base_date + timedelta(days=1)),
        (1, task5_id, "inProgress", base_date + timedelta(days=2)),
        (1, task6_id, "new", None),
        (1, task7_id, "done", base_date + timedelta(days=5)),
        (1, task8_id, "inProgress", base_date + timedelta(days=3)),
    ]
    # Also user 2 has some progress (teacher can also see tasks)
    status_data += [
        (2, task1_id, "done", base_date + timedelta(days=10)),
        (2, task4_id, "new", None),
    ]

    for user_id, t_id, st, last_view in status_data:
        cursor.execute(
            """
            INSERT INTO user_task_status (user_id, task_id, status, last_viewed)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, task_id) DO UPDATE
                SET status = EXCLUDED.status, last_viewed = EXCLUDED.last_viewed
            """,
            (user_id, t_id, st, last_view)
        )
    conn.commit()
    print("User statuses inserted.")

    # ------- 4. Submissions (for tasks marked 'done' or 'inProgress') -------
    def quick_submit(user_id, task_id, files):
        sub_id = submit_solution(conn, user_id, task_id, files)
        enqueue_solution_check(conn, sub_id)
        # optionally manually update the check result to completed
        cursor.execute(
            "UPDATE submission_results SET status='completed', score=100 WHERE submission_id=%s",
            (sub_id,)
        )
        conn.commit()
        return sub_id

    # User 1 submissions
    quick_submit(1, task1_id, [{"path": "root/Main.java", "language": "java", "content": "class Main {}"}])
    quick_submit(1, task3_id, [{"path": "root/Main.java", "language": "java", "content": "// OOP solution"}])
    quick_submit(1, task4_id, [{"path": "root/main.py", "language": "python", "content": "print('hello')"}])
    quick_submit(1, task5_id, [{"path": "root/main.py", "language": "python", "content": "list comprehension"}])
    quick_submit(1, task7_id, [{"path": "root/index.html", "language": "html", "content": "<html></html>"}])

    # User 2 submission
    quick_submit(2, task1_id, [{"path": "root/Main.java", "language": "java", "content": "// Teacher solution"}])

    print("Submissions created.")

    conn.commit()
    print("\n Database populated successfully!")

except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()