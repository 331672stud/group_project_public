import os

BASE_URL = os.getenv("USOS_BASE_URL", "https://apps.usos.pw.edu.pl/services/")
APP_URL = os.getenv("APP_URL", "http://localhost:8000/")


ENDPOINTS = {
    "request_token": BASE_URL + "oauth/request_token",
    "authorize": BASE_URL + "oauth/authorize",
    "access_token": BASE_URL + "oauth/access_token",
    "courses": BASE_URL + "courses/user",
    "revoke_token": BASE_URL + "oauth/revoke_token",
    "callback": APP_URL + "callback",
    "user_id": BASE_URL + "users/user"
}