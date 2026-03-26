import time
import psycopg2
from typing import Optional
import os

from fastapi import FastAPI, Request, Response, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
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
    get_user_id
)

from db_operations.db_operations import (
    insert_user,
    submit_solution,
    add_task,
    get_all_tasks,
    get_assigned_tasks,
    assign_task
)

CONSUMER_KEY = os.getenv("USOS_CONSUMER_KEY", "YOUR_KEY")
CONSUMER_SECRET = os.getenv("USOS_CONSUMER_SECRET", "YOUR_SECRET")

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
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

#chroniony router
protected_router = APIRouter(
    dependencies=[Depends(get_current_user)]
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

    user_id = get_user_id(CONSUMER_KEY, CONSUMER_SECRET,
                access_token, access_secret)
    
    request.session["user_id"] = user_id

    return {"login successful, user_id": user_id}

@app.get("/logout")
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
    user_id = get_current_user(request)
    return {"message": "Profile endpoint", "user_id": user_id}

@protected_router.get("/tasks")
def tasks(request: Request):
    assigned_tasks = get_assigned_tasks(conn, get_current_user(request))
    if(not assigned_tasks):
        return {"message": "No assigned tasks"}
    return {"message": "Assigned tasks", "tasks": assigned_tasks}

def public_tasks(request: Request):
    tasks = get_all_tasks(conn)
    return {"message": "All tasks", "tasks": tasks}

@protected_router.get("/submissions")
def submissions(request: Request):
    return {"message": "Submissions endpoint"}

@protected_router.get("/tasks/{task_id}")
def get_task(request: Request, task_id: int):
    return {"message": f"Get task with ID {task_id}"}
    
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "SUPER_SECRET_KEY"))
app.include_router(protected_router)