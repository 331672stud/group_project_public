import psycopg2

import sys
sys.path.insert(0, '/app') 

from db_operations.db_operations import create_task_with_files

import json

conn = psycopg2.connect(
    host="db",
    port=5432,
    user="postgres",
    password="password",
    database="postgres"
)

tasks = json.load(open("tasks/tasks.json", "r"))

for task in tasks:
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