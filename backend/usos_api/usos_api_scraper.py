from requests_oauthlib import OAuth1Session
from usos_api import ENDPOINTS

def get_user_courses(consumer_key, consumer_secret,
                     access_token, access_token_secret):
    """Zwraca aktywne kursy WAŻNE: usos api nie działa i trzeba samemu filtrować semestr XD

    Args:
        consumer_key (_type_): klucz do api
        consumer_secret (_type_): sekret do api
        access_token (_type_): token dostępowy
        access_token_secret (_type_): sekret dostępowy

    Returns:
        json: lista kursów z teraźniejszego semestru
    """

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
    data = response.json()
    terms = data["course_editions"].keys()
    latest_term = sorted(terms)[-1]

    current_courses = data["course_editions"][latest_term]

    return current_courses

def get_user(consumer_key, consumer_secret,
                access_token, access_token_secret):
    """Zwraca dane użytkownika

    Args:
        consumer_key (_type_): klucz do api
        consumer_secret (_type_): sekret do api
        access_token (_type_): token dostępowy
        access_token_secret (_type_): sekret dostępowy

    Returns:
        json: dane użytkownika
    """

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    response = oauth.get(ENDPOINTS["user_id"], params={
        "fields": "id|first_name|last_name|staff_status",
        "format": "json"
    })
    
    response.raise_for_status()
    
    return response.json()