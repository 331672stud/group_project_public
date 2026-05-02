import time
import psycopg2
from typing import Optional
import os

from fastapi import FastAPI, Request, Response, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from requests_oauthlib import OAuth1Session

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
    get_task,
    get_submissions,
    get_course_tasks
)

CONSUMER_KEY = os.getenv("USOS_CONSUMER_KEY", "YOUR_KEY")
CONSUMER_SECRET = os.getenv("USOS_CONSUMER_SECRET", "YOUR_SECRET")

FRONTEND_URL = os.getenv("FRONTEND_URL")

for _ in range(30):  # retry for ~30 seconds
    try:
        conn = psycopg2.connect(
            host="db",
            port=5432,
            user="postgres",
            password="password",
            database="postgres"
        )
        break
    except psycopg2.OperationalError:
        print("Waiting for database...")
        time.sleep(1)
else:
    raise Exception("Database not available")

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
    oauth_problem: Optional[str] = None
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

    # return {"login successful, user_id": user_data["id"]}
    return RedirectResponse(FRONTEND_URL)

@app.get("/public-tasks")
def public_tasks(request: Request):
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
def profile(request: Request):
    user_data = get_user_data(conn, get_current_user(request))
    return {"message": "Profile endpoint", "user_id": get_current_user(request), "first name": user_data[1], "last name": user_data[2], "user_type": user_data[3]}

@protected_router.get("/tasks")
def tasks(request: Request):
    assigned_tasks = get_assigned_tasks(conn, get_current_user(request))
    if(not assigned_tasks):
        return {"message": "No assigned tasks"}
    return {"message": "Assigned tasks", "tasks": assigned_tasks}

@protected_router.get("/submissions")
def submissions(request: Request):
    submissions = get_submissions(conn, get_current_user(request))
    return {"message": "Submissions endpoint: ", "submissions": submissions}

@protected_router.get("/tasks/{task_id}")
def get_task(request: Request, task_id: int):
    task = get_task(conn, task_id, get_current_user(request))
    return {"message": f"Get task with ID {task_id}", "task": task}

@protected_router.get("/topics") #albo u nas tagi
def get_topics(request: Request):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM tags ORDER BY name")
    topics = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    cursor.close()
    return {"topics": topics}

@protected_router.get("/topics{tag_id}/tasks")
def get_tasks_by_topic(request: Request, tag_id: int):
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
def get_my_submission(request: Request, task_id: int):
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

@protected_router.get("/courses/{course_id}/tasks")
def course_tasks(request: Request, course_id: int):
    user_id = get_current_user(request)
    tasks = get_course_tasks(conn, course_id)  
    if not tasks:
        return {"message": "No tasks in this course", "tasks": []}
    return {"message": f"Tasks for course {course_id}", "tasks": tasks}

@protected_router.patch("/tasks/{task_id}/progress")
def update_progress(request: Request, task_id: int):
    user_id = get_current_user(request)
    body = request.json()
    status = body.get("status")
    last_viewed = body.get("lastViewed")
    # Upsert into user_task_status
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_task_status (user_id, task_id, status, last_viewed)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, task_id) DO UPDATE
        SET status = EXCLUDED.status, last_viewed = EXCLUDED.last_viewed
    """, (user_id, task_id, status, last_viewed))
    conn.commit()
    cursor.close()
    return {"ok": True}

@protected_router.post("/tasks/{task_id}/submit")
def submit_task(request: Request, task_id: int, solution: str):
    submit_solution(conn, get_current_user(request), task_id, solution)
    return {"message": f"Submitted solution for task {task_id}"}

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "SUPER_SECRET_KEY"))

app.include_router(protected_router)
