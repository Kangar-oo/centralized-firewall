# security_service.py

import datetime

def validate_request(request):
    """
    Placeholder function to validate incoming requests.
    Could include API keys, tokens, or signatures.
    """
    api_key = request.headers.get("X-API-KEY")
    if api_key == "SECRET123":
        return True
    return False

def get_current_time():
    """
    Returns formatted timestamp
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
