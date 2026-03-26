from requests_oauthlib import OAuth1Session
from usos_api import ENDPOINTS

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
        params={"oauth_callback": ENDPOINTS["callback"]}
    )

    return response["oauth_token"], response["oauth_token_secret"]


def authorize_token(oauth_token):
    """autoryzuje użytkownika do naszej aplikacji, wracając do callbacku

    Args:
        oauth_token (token): token który wcześniej uzyskaliśmy
    """
    authorization_url = f"{ENDPOINTS['authorize']}?oauth_token={oauth_token}"
    return authorization_url

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

def revoke_access_token(consumer_key, consumer_secret,
                        access_token, access_token_secret,
                        deauthorize=False):
    """dezaktywuje token, wykorzystywane przy wylogowywaniu

    Args:
        consumer_key (_type_): klucz do api
        consumer_secret (_type_): sekret do api
        access_token (_type_): token dostępowy
        access_token_secret (_type_): sekret dostępowy
        deauthorize (bool, optional): czy zapomnieć zautoryzowane rzeczy. Defaults to False.

    Returns:
    json: odpowiedź z api
    """
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