from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from problems.models import Problem, Tag
from problems.serializers import TagSerializer, TagSerializerCreateProblem, ProblemListSerializer, ProblemSerializer, GetProblemSerializer
from django.conf import settings
import os, requests, json
from problems import middleware
from cloudinary import uploader

class getTagList(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        data = Tag.objects.all().order_by('name')
        data = TagSerializer(data, many = True)
        return Response(data = data.data, status = status.HTTP_200_OK)

class getTagListCreateProblem(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request):
        data = Tag.objects.all().order_by('name')
        data = TagSerializerCreateProblem(data, many = True)
        res_dict = {}
        res_dict["success"] = True
        res_dict["results"] = data.data
        return Response(data = res_dict, status = status.HTTP_200_OK)


class getProblemsList(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request):
        req_data = request.data
        tags = req_data.get("tags")
        level = req_data.get("level")
        # data = Problem.objects.filter(approved_by_admin = True)
        data = Problem.objects.all()
        if tags and len(tags) > 0:
            data = data.filter(tags__in = tags).distinct()
        if level:
            data = data.filter(problem_level = level).distinct()
        is_data = False
        print(request.headers)
        if request.headers.get('Authorization'):
            access_token = request.headers['Authorization'].split(' ')[1]
            response = middleware.Authentication.isAuthenticated(access_token)
            if response["success"]:
                data = ProblemListSerializer(data, many = True, context = {'mail_id': response['data']['email']})
                is_data = True
        if not is_data:
            data = ProblemListSerializer(data, many = True, context = {})
        return Response(data = data.data, status = status.HTTP_200_OK)


class AddProblem(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request):
        access_token = request.headers['Authorization'].split(' ')[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success" : False, "message" : "Unauthorized Request !"}
            return Response(data = data, status = status.HTTP_401_UNAUTHORIZED)
        request_data = request.data["data"]
        request_data["created_by"] = response['data']['email']
        serializer_obj = ProblemSerializer(data = request_data)
        if serializer_obj.is_valid():
            obj = serializer_obj.save()
            return_data = serializer_obj.data
            return_data["id"] = obj.id
            return Response(data = return_data, status = status.HTTP_201_CREATED)
        return Response(data = serializer_obj.errors, status = status.HTTP_400_BAD_REQUEST)


class GetProblem(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request):
        prob_obj = Problem.objects.get(id = request.data["id"])
        data = GetProblemSerializer(prob_obj)
        return Response(data = data.data, status = status.HTTP_200_OK)


class UploadTestCases(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request):
        probId = request.data["probId"]
        problem = Problem.objects.get(id = probId)
        setattr(problem, "sample_Tc", request.data["custom_test_cases"])
        setattr(problem, "total_Tc", request.data["test_cases"])
        problem.save()
        path = os.path.join(settings.MEDIA_ROOT, "TestCases", str(probId))
        if not os.path.exists(path):
            os.mkdir(path)
        for key, value in request.FILES.items():
            file_path = os.path.join(path, key + ".txt")
            with open(file_path, 'w') as f:
                data = value.read()
                f.write(data.decode("utf-8"))
        return Response(status = status.HTTP_200_OK)
