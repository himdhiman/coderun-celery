import requests
from django.conf import settings

class Authentication:
    def isAuthenticated(token):
        endpoint = settings.AUTH_SERVER_URL + "auth/hasAccess/"
        headers = {"Authorization" : f"JWT {token}"}
        response = requests.post(endpoint, headers = headers)
        if response.status_code == 200:
            return {"success" : True, "data" : response.json()}
        return {"success" : False, "data" : ""}
