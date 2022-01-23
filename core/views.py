from rest_framework import permissions, status
from core import tasks
import json, requests
from problems import middleware
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from core.helper import runcode_helper, runCustomTestCases


class CompileCode(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        headers = request.headers.get("Authorization")
        if not headers:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            access_token = headers.split(" ")[1]
            response = middleware.Authentication.isAuthenticated(access_token)
            if not response["success"]:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        data = runcode_helper(request.data)
        return Response(data=data, status=status.HTTP_200_OK)


class RunTests(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        headers = request.headers.get("Authorization")
        if not headers:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            access_token = headers.split(" ")[1]
            response = middleware.Authentication.isAuthenticated(access_token)
            if not response["success"]:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        data = runCustomTestCases(request.data)
        return Response(data=data, status=status.HTTP_200_OK)


class RunCode(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        body = json.loads(request.body)
        headers = request.headers.get("Authorization")
        mail_id = None
        if not headers:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            access_token = headers.split(" ")[1]
            response = middleware.Authentication.isAuthenticated(access_token)
            if not response["success"]:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                mail_id = response["data"]["email"]
        if not mail_id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        body["created_By"] = mail_id

        arr1 = body["created_By"].split("@")
        arr2 = arr1[1].split(".")
        uid = arr1[0] + arr2[0] + arr2[1]

        context = {"body": body, "uid": uid}
        tasks.runCode.delay(context)
        return Response(status=status.HTTP_202_ACCEPTED)
