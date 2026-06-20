import json

def insert_user(db, index, name, surname, user_type):
    """dodaje użytkownika do bazy

    Args:
        db (psycopg2): połączenie z bazą danych
        index (int): numer indeksu użytkownika
        name (str): Imię użytkownika
        surname (str): Nazwisko użytkownika
        user_type (int): Typ użytkownika (0 - student, 1 albo 2 - pracownik)
    """

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
        db (psycopg2): połączenie z bazą danych
        user_id (int): id użytkownika

    Returns:
        tuple: id, imie nazwisko TYP: 0 - student, 1 albo 2 - pracownik
    """
    cursor = db.cursor()
    cursor.execute("SELECT id, Uname, Usurename, user_type FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    return user_data

def submit_solution(db, user_id, task_id, files):
    """
    Zapisuje stan plików przesłanych przez użytkownika jako nowe zgłoszenie (submission) i aktualizuje status w user_task_status na 'in_progress'.

    Args:
        db (psycopg2): połączenie z bazą danych
        user_id (int): id użytkownika
        task_id (int): id zadania
        files (list): lista słowników z informacjami o plikach, np. [{"path": "root/index.html", "language": "html", "content": "<!doctype>..."}, ...]
    """
    cursor = db.cursor()
    try:
        # Snapshot plików jako JSONB
        content_json = json.dumps(files)
        cursor.execute(
            """
            INSERT INTO submissions (user_id, task_id, content)
            VALUES (%s, %s, %s::jsonb) RETURNING id
            """,
            (user_id, task_id, content_json)
        )
        submission_id = cursor.fetchone()[0]
        
        # aktualizacja statusu
        cursor.execute(
            """
            INSERT INTO user_task_status (user_id, task_id, status, last_viewed, content)
            VALUES (%s, %s, 'in_progress', NOW(), %s::jsonb)
            ON CONFLICT (user_id, task_id) DO UPDATE
                SET status = 'in_progress', last_viewed = NOW(), content = EXCLUDED.content
            """,
            (user_id, task_id, content_json)
        )

        db.commit()
        return submission_id
    finally:
        cursor.close()

def get_all_tasks(db):
    """zwraca id i tytuły wszystkich zadań

    Args:
        db (psycopg2): połączenie z bazą danych

    Returns:
        list: lista krotek (id, title) z id i tytułami zadań
    """
    cursor = db.cursor()
    cursor.execute("SELECT id, title FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def get_assigned_tasks(db, user_id):
    """zwraca przypisane zadania dla użytkownika, wraz z ich id i tytułami

    Args:
        db (psycopg2): połączenie z bazą danych
        user_id (int): id użytkownika

    Returns:
        list: lista krotek (id, title) z id i tytułami przypisanych zadań
    """    
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
    """przypisuje użytkownikowi zadanie o konkretnym ID

    Args:
        db (psycopg2): połączenie z bazą danych
        course_id (int): id kursu
        task_id (int): id zadania
        target_id (int): id użytkownika, któremu przypisujemy zadanie
        assigner_id (int): id użytkownika, który przypisuje zadanie


    Raises:
        Exception: Tylko właściciel kursu może przypisywać zadania

    Returns:
        str: komunikat o sukcesie
    """
    cursor = db.cursor()
    cursor.execute("SELECT id FROM courses WHERE id = %s AND course_owner_id = %s", (course_id, assigner_id))
    if not cursor.fetchone():
        raise Exception("Tylko właściciel kursu może przypisywać zadania.")
    cursor.execute("INSERT INTO assigned_tasks (user_id, task_id, assigner_id) VALUES (%s, %s, %s)", (target_id, task_id, assigner_id,))
    db.commit()
    cursor.close()
    return "Zadanie przypisane pomyślnie."

def get_course_tasks(db, course_id):
    """zwraca zadania dla konkretnego kursu

    Args:
        db (psycopg2): połączenie z bazą danych
        course_id (int): id kursu

    Returns:
        list: lista krotek (id, title) z id i tytułami zadań dla danego kursu
    """
    cursor = db.cursor()
    cursor.execute("SELECT t.id, t.title FROM tasks t JOIN course_tasks ct ON t.id = ct.task_id WHERE ct.course_id = %s", (course_id,))
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def filter_by_tags(db, tags):
    """zwraca zadania z określonym tagiem

    Args:
        db (psycopg2): połączenie z bazą danych
        tags (list): lista tagów

    Returns:
        list: lista krotek (id, title) z id i tytułami zadań dla danego tagu
    """
    cursor = db.cursor()
    query = "SELECT id, title FROM tasks WHERE "
    query += " OR ".join(["%s = ANY(tags)" for _ in tags])
    cursor.execute(query, tags)
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def get_submissions(db, user_id):
    """zwraca wszystkie oddane zadania użytkownika

    Args:
        db (psycopg2): połączenie z bazą danych
        user_id (int): id użytkownika

    Returns:
        list: lista krotek (id, task_id, title) z id, id zadania i tytułem oddanych zadań
    """
    cursor = db.cursor()
    cursor.execute("SELECT s.id, s.task_id, t.title FROM submissions s JOIN tasks t ON s.task_id = t.id WHERE s.user_id = %s", (user_id,))
    submissions = cursor.fetchall()
    cursor.close()
    return submissions

def get_task(db, task_id, user_id):
    """
    Zwraca szczegółowe informacje o zadaniu, w tym:
        - id, tytuł, opis, trudność, języki
        - tags: lista tagów
        - files: lista oryginalnych plików zadania
        - submission: pliki z ostatniego zgłoszenia jeśli istnieją

    Args:
        db (psycopg2): połączenie z bazą danych
        task_id (int): id zadania
        user_id (int): id użytkownika

    Returns:
        słownik albo nic jeśli nie znajdzie zadania
    """
    cursor = db.cursor()
    try:
        # podstawowe dane o zadaniu
        # rola użytkownika: 0 = student, 1/2 = pracownik
        cursor.execute("SELECT user_type FROM users WHERE id = %s", (user_id,))
        urow = cursor.fetchone()
        try:
            user_type = int(urow[0]) if urow and urow[0] is not None else 0
        except Exception:
            user_type = 0

   
        if user_type and user_type > 0:
            cursor.execute(
                """
                SELECT id, title, description, difficulty, languages, COALESCE(answer, NULL), (answer IS NOT NULL) as has_answer
                FROM tasks
                WHERE id = %s
                """,
                (task_id,)
            )
        else:
            cursor.execute(
                """
                SELECT id, title, description, difficulty, languages, NULL as answer, (answer IS NOT NULL) as has_answer
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
            "languages": row[4],         
            "answer": row[5],
            "has_answer": bool(row[6])
        }

      
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
        task["submission"] = sub[0] if sub else None  

        return task

    finally:
        cursor.close()

def get_task_by_topic_and_num_db(db, topic, num, user_id):
    """zwraca zadanie na podstawie tematu i numeru w bazie

    Args:
        db (psycopg2): połączenie z bazą danych
        topic (str): temat(tag) zadania
        num (int): numer zadania
        user_id (int): id użytkownika

    Returns:
        dict albo nic jeśli nie znajdzie zadania
    """    
    cursor = db.cursor()
    try:
        
        cursor.execute("SELECT user_type FROM users WHERE id = %s", (user_id,))
        urow = cursor.fetchone()
        try:
            user_type = int(urow[0]) if urow and urow[0] is not None else 0
        except Exception:
            user_type = 0

        answer_select = "COALESCE(t.answer, NULL)"

        cursor.execute(f"""
            SELECT
                t.id, t.title, t.description, t.difficulty, t.languages, {answer_select}, (t.answer IS NOT NULL) as has_answer,
                COALESCE(uts.status, 'new') AS status,
                uts.last_viewed AS last_viewed,
                COALESCE(
                    array_agg(tg.name ORDER BY tg.name)
                    FILTER (WHERE tg.name IS NOT NULL),
                    ARRAY[]::text[]
                ) AS tags
            FROM tasks t
            JOIN task_tags tt ON t.id = tt.task_id
            JOIN tags tg ON tt.tag_id = tg.id
            LEFT JOIN user_task_status uts ON uts.task_id = t.id AND uts.user_id = %s
            WHERE t.title = %s AND t.num = %s
            GROUP BY t.id, uts.status, uts.last_viewed
            """,
            (user_id, topic, num)
        )
        row = cursor.fetchone()
        if not row:
            return None
            

        task = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "difficulty": row[3],
            "languages": row[4],
            "answer": row[5],
            "has_answer": bool(row[6]),
            "status": row[7],
            "lastViewed": row[8].isoformat() if row[8] else None,
            "tags": row[9]
        }

        # Task files (folder tree)
        cursor.execute(
            """
            SELECT file_path, language, content
            FROM task_files
            WHERE task_id = %s
            ORDER BY file_path
            """,
            (task['id'],)
        )
        task["files"] = [
            {"path": r[0], "language": r[1], "content": r[2]}
            for r in cursor.fetchall()
        ]

     
        cursor.execute(
            """
            SELECT content
            FROM submissions
            WHERE user_id = %s AND task_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id, task['id'])
        )
        sub = cursor.fetchone()
        task["submission"] = sub[0] if sub else None   # JSONB, deserialised automatically

        return task

    finally:
        cursor.close()
        
def get_task_files(db, task_id):
    """Return list of {path, language, content} for a task."""
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            SELECT file_path, language, content
            FROM task_files
            WHERE task_id = %s
            ORDER BY file_path
            """,
            (task_id,)
        )
        rows = cursor.fetchall()
        return [
            {"path": row[0], "language": row[1], "content": row[2]}
            for row in rows
        ]
    finally:
        cursor.close()

def enqueue_solution_check(db, submission_id: int):
    """Tworzy wpis w submission_results ze statusem 'queued'."""
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO submission_results (submission_id, status) VALUES (%s, 'queued')",
            (submission_id,)
        )
        db.commit()
    finally:
        cursor.close()

def get_submission_result(db, submission_id: int):
    """Zwraca wynik sprawdzania dla danego zgłoszenia."""
    cursor = db.cursor()
    cursor.execute(
        "SELECT status, score, message, checked_at FROM submission_results WHERE submission_id = %s",
        (submission_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return None
    return {
        "status": row[0],
        "score": float(row[1]) if row[1] else None,
        "message": row[2],
        "checked_at": row[3].isoformat() if row[3] else None
    }
    
def create_task_with_files(db, title: str, difficulty: str, languages: list,
                           description: str, files: list, num: int, tags: list = None) -> int:
    """
    Tworzy zadanie wraz z plikami startowymi i tagami.
    files: lista słowników [{"path": ..., "language": ..., "content": ...}]
    tags: lista nazw tagów (opcjonalnie)
    Zwraca id nowego zadania.
    """
    cursor = db.cursor()
    try:
        # 1. Dodaj zadanie
        cursor.execute(
            "INSERT INTO tasks (title, num, difficulty, languages, description) VALUES (%s, %s, %s,%s,%s) RETURNING id",
            (title, num, difficulty, languages, description)
        )
        task_id = cursor.fetchone()[0]

        # 2. Dodaj pliki
        for f in files:
            cursor.execute(
                "INSERT INTO task_files (task_id, file_path, language, content) VALUES (%s,%s,%s,%s)",
                (task_id, f["path"], f.get("language"), f["content"])
            )

        # 3. Dodaj tagi
        if tags:
            for tag_name in tags:
                cursor.execute(
                    "INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                    (tag_name,)
                )
                cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
                tag_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (task_id, tag_id)
                )

        db.commit()
        return task_id
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()
        
def get_tasks_for_user(db, user_id):
    """
    Zwraca listę zadań ze statusem i tagami.
    zadanie:
        topic, num, difficulty, status, lastViewed, languages, description
    """
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            SELECT
                t.title,
                t.id,
                t.num,
                t.difficulty,
                t.languages,
                t.description,
                COALESCE(uts.status, 'new') AS status,
                uts.last_viewed AS last_viewed,
                COALESCE(
                    array_agg(tg.name ORDER BY tg.name)
                    FILTER (WHERE tg.name IS NOT NULL),
                    ARRAY[]::text[]
                ) AS tags
            FROM tasks t
            LEFT JOIN user_task_status uts
                ON uts.task_id = t.id AND uts.user_id = %s
            LEFT JOIN task_tags tt ON tt.task_id = t.id
            LEFT JOIN tags tg ON tg.id = tt.tag_id
            GROUP BY t.id, uts.status, uts.last_viewed
            ORDER BY t.id
            """,
            (user_id,)
        )
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            topic, task_id, num, difficulty, languages, description, status, last_viewed, tags = row
            tasks.append({
                "topic": topic,   # tagi jako topic,
                "tags": tags,
                "num": num,              
                "difficulty": difficulty,
                "status": status,
                "lastViewed": last_viewed.isoformat() if last_viewed else None,
                "languages": languages,             
                "description": description
            })

        return tasks
    finally:
        cursor.close()