from requests_oauthlib import OAuth1Session
import webbrowser
import os

BASE_URL = os.getenv("USOS_BASE_URL", "https://apps.usos.pw.edu.pl/services/")
APP_URL = os.getenv("APP_URL", "http://localhost:8000/")

ENDPOINTS = {
    "request_token": BASE_URL + "oauth/request_token",
    "authorize": BASE_URL + "oauth/authorize",
    "access_token": BASE_URL + "oauth/access_token",
    "courses": BASE_URL + "courses/user",
    "revoke_token": BASE_URL + "oauth/revoke_token"
}


def get_request_token(consumer_key, consumer_secret):
    """uzyskuje token dla aplikacji z USOS'a, z callbackiem do naszej aplikacji

    Args:
        consumer_key (klucz): klucz do api
        consumer_secret (sekret): sekret do api

    Returns:
        token: token dla nas
        secret: sekret dla nas
    """
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    response = oauth.fetch_request_token(
        ENDPOINTS["request_token"],
        params={"oauth_callback": APP_URL + "callback"}
    )

    return response["oauth_token"], response["oauth_token_secret"]


def authorize_token(oauth_token):
    """autoryzuje użytkownika do naszej aplikacji, wracając do callbacku

    Args:
        oauth_token (token): token który wcześniej uzyskaliśmy
    """
    authorization_url = f"{ENDPOINTS['authorize']}?oauth_token={oauth_token}"
    webbrowser.open(authorization_url)

def get_access_token(consumer_key, consumer_secret,
                     request_token, request_token_secret, verifier):

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        verifier=verifier,
    )

    response = oauth.fetch_access_token(ENDPOINTS["access_token"])

    return response["oauth_token"], response["oauth_token_secret"]


def get_user_courses(consumer_key, consumer_secret,
                     access_token, access_token_secret):

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    response = oauth.get(ENDPOINTS["courses"], params={
        "fields": "course_editions",
        "format": "json"
    })

    response.raise_for_status()
    return response.json()

def revoke_access_token(consumer_key, consumer_secret,
                        access_token, access_token_secret,
                        deauthorize=False):
    
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    params = {
        "format": "json"
    }

    if deauthorize:
        params["deauthorize"] = "true"

    response = oauth.post(ENDPOINTS["revoke_token"], params=params)
    response.raise_for_status()

    return response.json()

#TO JEST TYLKO DO WERYFIKACJI LOGOWANIA SKYRPTEM

def get_request_token_old(consumer_key, consumer_secret):
    """uzyskuje token dla aplikacji z USOS'a, BEZ CALLBACKU

    Args:
        consumer_key (klucz): klucz do api
        consumer_secret (sekret): sekret do api

    Returns:
        token: token dla nas
        secret: sekret dla nas
    """
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    response = oauth.fetch_request_token(
        ENDPOINTS["request_token"],
        params={"oauth_callback": "oob"}
    )

    return response["oauth_token"], response["oauth_token_secret"] 

def authorize_token_old(oauth_token):
    authorization_url = f"{ENDPOINTS['authorize']}?oauth_token={oauth_token}"

    print("Open this URL in browser and authorize:")
    print(authorization_url)

    webbrowser.open(authorization_url)

    verifier = input("Enter oauth_verifier (PIN): ").strip()
    return verifier