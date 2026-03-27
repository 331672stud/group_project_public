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

def submit_solution(db, user_id, task_id, solution):
    cursor = db.cursor()
    cursor.execute("INSERT INTO submissions (user_id, task_id, code) VALUES (%s, %s, %s)", (user_id, task_id, solution,))
    db.commit()
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

def assign_task(db, task_id, target_id, assigner_id,):
    cursor = db.cursor()
    cursor.execute("SELECT user_type FROM users WHERE id = %s", (assigner_id,))
    assigner_type = cursor.fetchone()[0]
    if assigner_type != 'course_owner':
        cursor.close()
        raise Exception("Only course owners can assign tasks.")
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

