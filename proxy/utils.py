import hmac, hashlib, time
from django.conf import settings
import requests

def generate_hmac_headers(endpoint_path):
    timestamp = str(int(time.time()))
    # cleaned_path = endpoint_path.lstrip('/') 
    message = f"{timestamp}:{endpoint_path}"
    secret_key = settings.HMAC_SECRET_KEY.encode()
    signature = hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()

    return {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }

def refresh_access_token(session):
    """
    Attempts to refresh the access token using the refresh token stored in session.
    Returns a new access token if successful, otherwise None.
    """
    refresh_token = session.get('refresh_token')
    
    if not refresh_token:
        print("There is no refresh token")
        return None

    refresh_url = f"{settings.BACKEND_BASE_URL}/api/token/refresh/"
    print(refresh_url)
    try:
        response = requests.post(refresh_url, json={'refresh': refresh_token})
        if response.status_code == 200:
            tokens = response.json()
            session['access_token'] = tokens.get('access')
            session['refresh_token'] = tokens.get('refresh')
            return tokens.get('access')
    except requests.RequestException:
        pass

    return None
