from usos_api import (
    get_request_token_old,
    authorize_token_old,
    get_access_token,
    get_user_courses,
    revoke_access_token
)
import os

CONSUMER_KEY = os.getenv("USOS_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("USOS_CONSUMER_SECRET")

def main():
    #krótki showcase api

    req_token, req_secret = get_request_token_old(
        CONSUMER_KEY, CONSUMER_SECRET
    )

    verifier = authorize_token_old(req_token)

    access_token, access_secret = get_access_token(
        CONSUMER_KEY, CONSUMER_SECRET,
        req_token, req_secret, verifier
    )

    courses = get_user_courses(
        CONSUMER_KEY, CONSUMER_SECRET,
        access_token, access_secret
    )

    print("User courses:")
    print(courses)
    
    result = revoke_access_token(
        CONSUMER_KEY, CONSUMER_SECRET,
        access_token, access_secret,
        deauthorize=True 
    )

    print("Revoke result:", result)


if __name__ == "__main__":
    main()