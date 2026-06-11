import psycopg2, time, sys, os

sys.path.insert(0, '/app') 

from db_operations.db_operations import create_task_with_files

import json

while True:
    try:
        conn = psycopg2.connect(
            host="db",
            port=5432,
            user="postgres",
            password="password",
            database="postgres"
        )
        break
    except:
        print('Database not ready, sleeping 2s')
        time.sleep(2)


print('Database ready')

tasks = json.load(open("/app/scripts/tasks/tasks.json", "r"))

for task in tasks:
    num = task["num"]
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM tasks WHERE num = %s", (num,))
        exists = cur.fetchone() is not None

    if exists:
        print(f"Task with num {num} already exists, skipping.")
        continue
    
    task_id = create_task_with_files(
        conn,
        title=task["topic"],
        difficulty=task["difficulty"],
        languages=task["languages"],
        description=task["description"],
        files=task["files"],
        tags=[task["topic"].lower()],
        num=task["num"]
    )
    print(f"Created task with ID {task_id}")

conn.close()