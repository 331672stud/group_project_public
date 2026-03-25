
def insert_user(db, username, token):
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, token) VALUES (%s, %s)", (username, token))
    db.commit()
    cursor.close()

def submit_solution(db, user_id, task_id, solution):
    cursor = db.cursor()
    cursor.execute("INSERT INTO submissions (user_id, task_id, code) VALUES (%s, %s, %s)", (user_id, task_id, solution))
    db.commit()
    cursor.close()

def add_task(db, title, description, code_template):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (title, description, code_template) VALUES (%s, %s, %s)", (title, description, code_template))
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

def assign_task(db, task_id, target_id, assigner_id):
    cursor = db.cursor()
    cursor.execute("SELECT user_type FROM users WHERE id = %s", (assigner_id,))
    assigner_type = cursor.fetchone()[0]
    if assigner_type != 'course_owner':
        cursor.close()
        raise Exception("Only course owners can assign tasks.")
    cursor.execute("INSERT INTO assigned_tasks (user_id, task_id, assigner_id) VALUES (%s, %s, %s)", (target_id, task_id, assigner_id))
    db.commit()
    cursor.close()
    return "Task assigned successfully."