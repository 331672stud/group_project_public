import time
import psycopg2
from typing import Optional
import os
import json

from fastapi import FastAPI, Request, Response, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from requests_oauthlib import OAuth1Session
from pydantic import BaseModel

from usos_api.usos_api_auth import (
    get_request_token,
    authorize_token,
    get_access_token,
    revoke_access_token
)

from usos_api.usos_api_scraper import (
    get_user_courses,
    get_user
)

from db_operations.db_operations import (
    insert_user,
    submit_solution,
    get_all_tasks,
    get_assigned_tasks,
    get_user_data,
    get_task as get_task_db,
    get_submissions,
    get_course_tasks,
    enqueue_solution_check,
    get_submission_result,
    get_tasks_for_user,
    get_task_files,
    get_task_by_topic_and_num_db
)

from db_operations.pool import(
    init_pool,
    close_pool,
    get_connection,
    release_connection
)

from verification import (
    check_submission
)

CONSUMER_KEY = os.getenv("USOS_CONSUMER_KEY", "YOUR_KEY")
CONSUMER_SECRET = os.getenv("USOS_CONSUMER_SECRET", "YOUR_SECRET")

FRONTEND_URL = os.getenv("FRONTEND_URL")

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)

# login check
def get_current_user(request: Request):
    """sprawdza czy użytkownik jest zalogowany,
       zwraca id jeśli przypisane.
    Args:
        request (Request): sesja

    Raises:
        HTTPException: błąd jeśli nie jesteś zalogowany

    Returns:
        int: id użytkownika
    """
    user_id = request.session.get("user_id")
    print(f"Current user ID: {user_id}")  # Debug print
    if not user_id:
        raise HTTPException(status_code=401, detail="Nie zalogowany")
    return user_id

app = FastAPI()

origins = [
    FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_pool()
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS answer TEXT;")
        conn.commit()
        cur.close()
        release_connection(conn)
    except Exception as e:
        print('Warning: could not ensure tasks.answer column:', e)
    
@app.on_event("shutdown")
def shutdown_event():
    close_pool()

# api endpoints
@app.get("/login")
async def login(request: Request):
    try:
        req_token, req_secret = get_request_token(CONSUMER_KEY, CONSUMER_SECRET)
    except Exception as e:
        raise HTTPException(500, f"Failed to get request token: {str(e)}")
    try:
        request.session["request_token"] = req_token
        request.session["request_secret"] = req_secret
    except Exception as e:
        raise HTTPException(500, f"Failed to store request token in session: {str(e)}")
    # autoryzacja
    authorize_url = authorize_token(req_token)
    return RedirectResponse(authorize_url)

@app.get("/callback")
async def callback(
    request: Request,
    oauth_verifier: Optional[str] = None,
    oauth_token: Optional[str] = None,
    oauth_problem: Optional[str] = None,
    conn = Depends(get_db)
):
    if oauth_token != request.session.get("request_token"):
        return {"error": "Invalid oauth_token"}

    if oauth_problem:
        return {"error": f"OAuth failed: {oauth_problem}"}

    if not oauth_verifier:
        return {"error": "Missing oauth_verifier"}
    
    #uzyskanie dostępu
    try:
        access_token, access_secret = get_access_token(
            CONSUMER_KEY, CONSUMER_SECRET,
            oauth_token, request.session.get("request_secret"), oauth_verifier
        )
    except Exception as e:
        raise HTTPException(500, f"Failed to get access token: {str(e)}")
    
    request.session["access_token"] = access_token
    request.session["access_secret"] = access_secret

    user_data = get_user(CONSUMER_KEY, CONSUMER_SECRET,
                access_token, access_secret)
    
    request.session["user_id"] = user_data["id"]
    insert_user(conn, user_data["id"], user_data["first_name"], user_data["last_name"], user_data["staff_status"])

    return RedirectResponse(FRONTEND_URL)

@app.get("/public-tasks")
def public_tasks(request: Request, conn = Depends(get_db)):
    tasks = get_all_tasks(conn)
    return {"message": "All tasks", "tasks": tasks}

#chroniony router
protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@protected_router.get("/logout")
async def logout(request: Request):
    revoke_access_token(
        CONSUMER_KEY, CONSUMER_SECRET,
        request.session.get("access_token"), request.session.get("access_secret"),
        deauthorize=False
    )
    request.session.clear()
    return {"message": "Logged out"}

@protected_router.get("/my-courses")
async def my_courses(request: Request):
    access_token = request.session.get("access_token")
    access_secret = request.session.get("access_secret")
    if not access_token or not access_secret:
        raise HTTPException(401, "Access token missing")

    courses = get_user_courses(CONSUMER_KEY, CONSUMER_SECRET, access_token, access_secret)
    return courses

@protected_router.get("/profile")
def profile(request: Request, conn = Depends(get_db)):
    user_data = get_user_data(conn, get_current_user(request))
    return {"message": "Profile endpoint", "user_id": get_current_user(request), "first name": user_data[1], "last name": user_data[2], "user_type": user_data[3]}

@protected_router.get("/assigned_tasks")
def tasks(request: Request, conn = Depends(get_db)):
    assigned_tasks = get_assigned_tasks(conn, get_current_user(request))
    if(not assigned_tasks):
        return {"message": "No assigned tasks"}
    return {"message": "Assigned tasks", "tasks": assigned_tasks}

@protected_router.get("/tasks")
def list_tasks(request: Request, conn = Depends(get_db)):
    user = get_current_user(request)
    tasks_data = get_tasks_for_user(conn, user)
    return {"tasks": tasks_data}

@protected_router.get("/submissions")
def submissions(request: Request, conn = Depends(get_db)):
    submissions = get_submissions(conn, get_current_user(request))
    return {"message": "Submissions endpoint: ", "submissions": submissions}

@protected_router.get("/tasks/{task_id}")
def get_task(request: Request, task_id: int, conn = Depends(get_db)):
    task = get_task_db(conn, task_id, get_current_user(request))
    return {"message": f"Get task with ID {task_id}", "task": task}

@protected_router.get("/tasks/{task_id}/files")
def task_files(request: Request, task_id: int, conn = Depends(get_db)):
    files = get_task_files(conn, task_id)
    if not files:
        raise HTTPException(status_code=404, detail="Task not found or no files")
    return {"task_id": task_id, "files": files}

@protected_router.get("/topics") #albo u nas tagi
def get_topics(request: Request, conn = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM tags ORDER BY name")
    topics = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    cursor.close()
    return {"topics": topics}

@protected_router.get("/topics/{tag_id}/tasks")
def get_tasks_by_topic(request: Request, tag_id: int, conn = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.title
        FROM tasks t
        JOIN task_tags tt ON t.id = tt.task_id
        WHERE tt.tag_id = %s
        ORDER BY t.title
    """, (tag_id,))
    tasks = [{"id": row[0], "title": row[1]} for row in cursor.fetchall()]
    cursor.close()
    return {"tasks": tasks}

@protected_router.get("/tasks/{task_id}/submission")
def get_my_submission(request: Request, task_id: int, conn = Depends(get_db)):
    user_id = get_current_user(request)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content FROM submissions
        WHERE user_id = %s AND task_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (user_id, task_id))
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return {"files": None}
    return {"files": row[0]}  

@protected_router.get("/tasks/{topic}/{num}")
def get_task_by_topic_and_num(request: Request, topic: str, num: int, conn = Depends(get_db)):
    task = get_task_by_topic_and_num_db(conn, topic, num, get_current_user(request))
    return {"message": f"Get task with topic '{topic}' and number {num}", "task": task}


@protected_router.get("/courses/{course_id}/tasks")
def course_tasks(request: Request, course_id: int, conn = Depends(get_db)):
    user_id = get_current_user(request)
    tasks = get_course_tasks(conn, course_id)  
    if not tasks:
        return {"message": "No tasks in this course", "tasks": []}
    return {"message": f"Tasks for course {course_id}", "tasks": tasks}

class ProgressUpdate(BaseModel):
    status: str
    lastViewed: str | None = None
    files: list[dict] | None = None

@protected_router.patch("/tasks/{task_id}/progress")
def update_progress(
    task_id: int,
    payload: ProgressUpdate,
    user_id: int = Depends(get_current_user),
    conn = Depends(get_db)
    ):
    status = payload.status
    last_viewed = payload.lastViewed
    
    content_json = json.dumps(payload.files) if payload.files is not None else None
    # Upsert into user_task_status
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_task_status (user_id, task_id, status, last_viewed, content)
        VALUES (%s, %s, %s, %s, COALESCE(%s, '[]'::jsonb))
        ON CONFLICT (user_id, task_id) DO UPDATE
        SET status = EXCLUDED.status, 
        last_viewed = EXCLUDED.last_viewed,
        content = COALESCE(%s, user_task_status.content)
    """, (user_id, task_id, status, last_viewed, content_json, content_json))
    conn.commit()
    cursor.close()
    return {"ok": True}

class TaskSubmit(BaseModel):
    files: list


class AnswerSubmit(BaseModel):
    answer: str

@protected_router.post("/tasks/{task_id}/submit")
def submit_task(
        task_id: int,
        payload: TaskSubmit,
        user_id: int = Depends(get_current_user),
        conn = Depends(get_db)
    ):
    submission_id = submit_solution(conn, user_id, task_id, payload.files)
    enqueue_solution_check(conn, submission_id)
    check_submission(conn, submission_id)
    return {"message": f"Submitted solution for task {task_id}", "submission_id": submission_id}


@protected_router.post("/tasks/{task_id}/submit_answer")
def submit_answer(task_id: int, payload: AnswerSubmit, user_id: int = Depends(get_current_user), conn = Depends(get_db)):
    task = get_task_db(conn, task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    correct = row[0] if row else None
    if correct is None:
        raise HTTPException(status_code=400, detail="Task does not accept answer submissions")

    user_answer = (payload.answer or "").strip()


    import re, json as _json
    def tokenize(s: str):
        parts = [p.strip() for p in re.split(r"[;,\\s]+", s) if p.strip()]
        return parts

  
    stored = correct
    ordered_flag = False
    correct_value = None
    try:

        if isinstance(correct, str):
            try:
                parsed = _json.loads(correct)
            except Exception:
                parsed = None
        else:
            parsed = correct

        if isinstance(parsed, dict) and 'value' in parsed:
            correct_value = parsed['value']
            ordered_flag = bool(parsed.get('ordered', False))
        else:
            correct_value = correct
    except Exception:
        correct_value = correct

    correct_tokens = tokenize(str(correct_value))
    user_tokens = tokenize(user_answer)

    is_multi = len(correct_tokens) > 1

    if is_multi and ordered_flag:
        matches = 0
        for i, t in enumerate(correct_tokens):
            if i < len(user_tokens) and user_tokens[i].lower() == t.lower():
                matches += 1
        score = 100.0 * (matches / len(correct_tokens)) if len(correct_tokens) > 0 else 0.0
        is_correct = matches == len(correct_tokens)
        if is_correct:
            message = 'Poprawna odpowiedź'
        elif matches == 0:
            message = 'Niepoprawna odpowiedź'
        else:
            message = f'Partially correct ({matches}/{len(correct_tokens)})'
    elif is_multi:
        correct_set = set([t.lower() for t in correct_tokens])
        user_set = set([t.lower() for t in user_tokens])
        intersection = correct_set.intersection(user_set)
        score = 0.0
        if len(correct_set) > 0:
            score = 100.0 * (len(intersection) / len(correct_set))
        is_correct = intersection == correct_set
        if is_correct:
            message = 'Poprawna odpowiedź'
        elif len(intersection) == 0:
            message = 'Niepoprawna odpowiedź'
        else:
            message = f'Partially correct ({len(intersection)}/{len(correct_set)})'
    else:
        is_correct = user_answer.strip().lower() == str(correct_value).strip().lower()
        score = 100.0 if is_correct else 0.0
        message = 'Poprawna odpowiedź' if is_correct else 'Niepoprawna odpowiedź'


    submission_id = submit_solution(conn, user_id, task_id, [{"path": "answer", "language": "text", "content": user_answer}])

    cursor = conn.cursor()
    try:
        status = 'completed'
        cursor.execute("INSERT INTO submission_results (submission_id, status, score, message, checked_at) VALUES (%s,%s,%s,%s,NOW())", (submission_id, status, score, message))
        conn.commit()
    finally:
        cursor.close()

    return {"submission_id": submission_id, "correct": is_correct, "message": message, "score": score}

@protected_router.get("/submissions/{submission_id}/result")
def get_submission_result_endpoint(request: Request, submission_id: int, conn = Depends(get_db)):
    result = get_submission_result(conn, submission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Submission not found")
    return result

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "SUPER_SECRET_KEY"))

app.include_router(protected_router)
