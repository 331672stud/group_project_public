import json

def insert_user(db, index, name, surname, user_type):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s", (index,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO users (id, Uname, Usurename, user_type) VALUES (%s, %s, %s, %s)", (index, name, surname, user_type,))
    db.commit()
    cursor.close()
    
def get_user_data(db, user_id):
    """zwraca zapisane dane użytkownika

    Args:
        db (_type_): baza
        user_id (_type_): id użytkownika

    Returns:
        _type_: id, imie nazwisko TYP: 0 - student, 1 albo 2 - pracownik
    """
    cursor = db.cursor()
    cursor.execute("SELECT id, Uname, Usurename, user_type FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    return user_data

def submit_solution(db, user_id, task_id, files):
    """
    Inserts a multi-file submission (stored as JSONB) and marks the task as 'done'.

    Args:
        db: psycopg2 connection
        user_id: int
        task_id: int
        files: list of dicts, each with keys "path", "language", "content"

    Example:
        files = [
            {"path": "root/index.html", "language": "html", "content": "<!doctype>..."},
            {"path": "root/src/App.jsx", "language": "javascript", "content": "import..."}
        ]
    """
    cursor = db.cursor()
    try:
        # Insert the full files snapshot as JSONB
        content_json = json.dumps(files)
        cursor.execute(
            """
            INSERT INTO submissions (user_id, task_id, content)
            VALUES (%s, %s, %s::jsonb)
            """,
            (user_id, task_id, content_json)
        )

        # Upsert progress to 'done'
        cursor.execute(
            """
            INSERT INTO user_task_status (user_id, task_id, status, last_viewed)
            VALUES (%s, %s, 'done', NOW())
            ON CONFLICT (user_id, task_id) DO UPDATE
                SET status = 'done', last_viewed = NOW()
            """,
            (user_id, task_id)
        )

        db.commit()
    finally:
        cursor.close()

def add_task(db, title, description, code_template):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (title, description, code_template) VALUES (%s, %s, %s)", (title, description, code_template,))
    db.commit()
    cursor.close()

def get_all_tasks(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, title FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def get_assigned_tasks(db, user_id):
    cursor = db.cursor()
    cursor.execute("""
        SELECT t.id, t.title 
        FROM tasks t
        JOIN assigned_tasks at ON t.id = at.task_id
        WHERE at.user_id = %s
    """, (user_id,))
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def assign_task(db, course_id, task_id, target_id, assigner_id,):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM courses WHERE id = %s AND course_owner_id = %s", (course_id, assigner_id))
    if not cursor.fetchone():
        raise Exception("Only the course owner can assign tasks")
    cursor.execute("INSERT INTO assigned_tasks (user_id, task_id, assigner_id) VALUES (%s, %s, %s)", (target_id, task_id, assigner_id,))
    db.commit()
    cursor.close()
    return "Task assigned successfully."

def get_course_tasks(db, course_id):
    cursor = db.cursor()
    cursor.execute("SELECT t.id, t.title FROM tasks t JOIN course_tasks ct ON t.id = ct.task_id WHERE ct.course_id = %s", (course_id,))
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def filter_by_tags(db, tags):
    cursor = db.cursor()
    query = "SELECT id, title FROM tasks WHERE "
    query += " OR ".join(["%s = ANY(tags)" for _ in tags])
    cursor.execute(query, tags)
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def get_submissions(db, user_id):
    cursor = db.cursor()
    cursor.execute("SELECT s.id, s.task_id, t.title FROM submissions s JOIN tasks t ON s.task_id = t.id WHERE s.user_id = %s", (user_id,))
    submissions = cursor.fetchall()
    cursor.close()
    return submissions

def get_task(db, task_id, user_id):
    """
    Returns a dictionary with:
        - id, title, description, difficulty, languages
        - tags: list of tag names
        - files: list of {path, language, content} (the task template)
        - submission: user's latest submitted files (or None)

    Args:
        db: psycopg2 connection
        task_id: int
        user_id: int

    Returns:
        dict or None if task not found
    """
    cursor = db.cursor()
    try:
        # Basic task info
        cursor.execute(
            """
            SELECT id, title, description, difficulty, languages
            FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        task = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "difficulty": row[3],
            "languages": row[4],          # list or None
        }

        # Tags (topics)
        cursor.execute(
            """
            SELECT t.name
            FROM tags t
            JOIN task_tags tt ON t.id = tt.tag_id
            WHERE tt.task_id = %s
            ORDER BY t.name
            """,
            (task_id,)
        )
        task["tags"] = [r[0] for r in cursor.fetchall()]

        # Task files (folder tree)
        cursor.execute(
            """
            SELECT file_path, language, content
            FROM task_files
            WHERE task_id = %s
            ORDER BY file_path
            """,
            (task_id,)
        )
        task["files"] = [
            {"path": r[0], "language": r[1], "content": r[2]}
            for r in cursor.fetchall()
        ]

        # User's latest submission (if any)
        cursor.execute(
            """
            SELECT content
            FROM submissions
            WHERE user_id = %s AND task_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id, task_id)
        )
        sub = cursor.fetchone()
        task["submission"] = sub[0] if sub else None   # JSONB, deserialised automatically

        return task

    finally:
        cursor.close()

