import requests

class Authentication:
    def isAuthenticated(token):
        endpoint = "https://db-auth.herokuapp.com/auth/hasAccess/"
        headers = {"Authorization" : f"JWT {token}"}
        response = requests.post(endpoint, headers = headers)
        if response.status_code == 200:
            return {"success" : True, "data" : response.json()}
        return {"success" : False, "data" : ""}
