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

with conn.cursor() as cur:
    cur.execute("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS answer TEXT")
    conn.commit()

tasks = json.load(open("/app/scripts/tasks/tasks.json", "r"))

for task in tasks:
    num = task["num"]
    topic = task["topic"]
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM tasks WHERE num = %s and title = %s", (num, topic))
        exists = cur.fetchone() is not None
    if exists:
        print(f"Task with num {num} and topic {topic} already exists, updating files/tags.")
        # find task id
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM tasks WHERE num = %s and title = %s", (num, topic))
            row = cur.fetchone()
            if not row:
                print(f"Could not find task id for existing task {num} - {topic}, skipping update.")
                continue
            task_id = row[0]
            # update or insert files: if existing file has empty content and incoming has non-empty, update it;
            # otherwise insert missing files
            for f in task.get("files", []):
                file_path = f.get("path")
                language = f.get("language")
                content = f.get("content", "")
                cur.execute("SELECT content FROM task_files WHERE task_id = %s AND file_path = %s", (task_id, file_path))
                existing = cur.fetchone()
                if existing:
                    existing_content = existing[0]
                    # update if incoming content differs from existing content
                    if existing_content != content:
                        cur.execute(
                            "UPDATE task_files SET content = %s, language = %s WHERE task_id = %s AND file_path = %s",
                            (content, language, task_id, file_path)
                        )
                        print(f"Updated file {file_path} for task {task_id}")
                    else:
                        print(f"Skipping file {file_path} for task {task_id} (content identical)")
                else:
                    cur.execute(
                        "INSERT INTO task_files (task_id, file_path, language, content) VALUES (%s,%s,%s,%s)",
                        (task_id, file_path, language, content)
                    )
                    print(f"Inserted file {file_path} for task {task_id}")
            # update answer if provided
            if task.get("answer") is not None:
                cur.execute("UPDATE tasks SET answer = %s WHERE id = %s", (task.get("answer"), task_id))

            # ensure tags exist and are linked
            for tag in ([task["topic"].lower()] if task.get("topic") else []) + (task.get("tags") or []):
                try:
                    cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (tag,))
                    cur.execute("SELECT id FROM tags WHERE name = %s", (tag,))
                    tag_id = cur.fetchone()[0]
                    cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (task_id, tag_id))
                except Exception:
                    conn.rollback()
                    raise
            conn.commit()
        continue
    
    task_id = create_task_with_files(
        conn,
        title=task["topic"],
        difficulty=task.get("difficulty"),
        languages=task.get("languages"),
        description=task.get("description"),
        files=task.get("files", []),
        tags=[task["topic"].lower()] if task.get("topic") else None,
        num=task["num"]
    )
    # set answer if provided
    if task.get("answer") is not None:
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET answer = %s WHERE id = %s", (task.get("answer"), task_id))
            conn.commit()
    print(f"Created task with ID {task_id}")

conn.close()