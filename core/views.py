from rest_framework import permissions, status
from core import tasks
import json, requests
from problems import middleware
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

class CompileCode(APIView):
    permission_classes = (permissions.AllowAny, )
    language_mapping = {
        "C++ 17" : 53,
        "C++ 14" : 52,
        "C" : 48,
        "Java" : 26,
        "Python 2" : 36,
        "Python 3" : 71
    }
    def post(self, request):
        req_data = request.data
        url = "https://judge0-ce.p.rapidapi.com/submissions"
        querystring = {"base64_encoded":"true","wait":"true","fields":"*"}
        payload = {
            "language_id" : self.language_mapping[req_data["lang"]],
            "source_code" : req_data["code"],
            "stdin" : req_data["input"]
        }
        headers = {
            'content-type': "application/json",
            'x-rapidapi-host': "judge0-ce.p.rapidapi.com",
            'x-rapidapi-key': "3bad142ebamshd424a4c3b68c90ep1da74ajsneb947385a6ff"
        }
        res = requests.request("POST", url, data = json.dumps(payload), headers = headers, params = querystring)
        return Response(data = res.json(), status = status.HTTP_200_OK)


class RunCode(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request, uid):
        body = json.loads(request.body)
        headers = request.headers.get("Authorization")
        mail_id = None
        if not headers:
            return Response(status = status.HTTP_401_UNAUTHORIZED)
        else:
            access_token = headers.split(' ')[1]
            response = middleware.Authentication.isAuthenticated(access_token)
            if not response["success"]:
                return Response(status = status.HTTP_401_UNAUTHORIZED)
            else:
                mail_id = response['data']['email']
        if not mail_id:
            return Response(status = status.HTTP_401_UNAUTHORIZED)
        body["created_By"] = mail_id
        context = {"body" : body, "uid": uid}
        tasks.runCode.delay(context)
        return Response(status = status.HTTP_202_ACCEPTED)

