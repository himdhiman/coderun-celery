from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from problems.models import (
    Problem,
    Submission,
    Tag,
    UpvotesDownvote,
    Bookmark,
    Editorial,
    SavedCode,
)
import json, ast
from problems import middleware
import cloudinary
import cloudinary.uploader
import cloudinary.api
from problems.serializers import (
    AllSubmissionsSerializer,
    TagSerializer,
    TagSerializerCreateProblem,
    ProblemListSerializer,
    ProblemSerializer,
    GetProblemSerializer,
    ProblemListStatusSerializer,
    SubmissionListSerializer,
    EditorialSerializer,
    SavedCodeSerializer,
)
from datetime import datetime
from core.helper import encode_data, decode_data
from ratelimit.decorators import ratelimit


class getTagList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        data = Tag.objects.all().order_by("name")
        data = TagSerializer(data, many=True)
        return Response(data=data.data, status=status.HTTP_200_OK)


class getTagListCreateProblem(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        data = Tag.objects.all().order_by("name")
        data = TagSerializerCreateProblem(data, many=True)
        res_dict = {}
        res_dict["success"] = True
        res_dict["results"] = data.data
        return Response(data=res_dict, status=status.HTTP_200_OK)


class getProblemsList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        data = Problem.objects.filter(approved_by_admin=True)
        data = ProblemListSerializer(data, many=True, context={})
        return Response(data=data.data, status=status.HTTP_200_OK)


class getFilteredProblemList(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        req_data = request.data
        tags = req_data.get("tags")
        difficulty = req_data.get("difficulty")
        keyword = req_data.get("keyword")
        data = Problem.objects.filter(approved_by_admin=True)
        if keyword and keyword != "":
            data = data.filter(title__icontains = keyword).distinct()
        if tags and len(tags) > 0:
            data = data.filter(tags__id__in = tags).distinct()
        if difficulty:
            data = data.filter(problem_level__in = difficulty).distinct()
        data = ProblemListSerializer(data, many=True, context={})
        return Response(data=data.data, status=status.HTTP_200_OK)


class getProblemsStatus(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        req_data = request.data["data"]
        data = Problem.objects.filter(id__in=req_data["ids"])
        if request.headers.get("Authorization"):
            access_token = request.headers["Authorization"].split(" ")[1]
            response = middleware.Authentication.isAuthenticated(access_token)
            if response["success"]:
                data = ProblemListStatusSerializer(
                    data, many=True, context={"mail_id": response["data"]["email"]}
                )
                return Response(data=data.data, status=status.HTTP_200_OK)
        return Response(
            data="Authorization Failed", status=status.HTTP_401_UNAUTHORIZED
        )


class AddProblem(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data["data"]
        request_data["created_by"] = response["data"]["email"]
        serializer_obj = ProblemSerializer(data=request_data)
        if serializer_obj.is_valid():
            obj = serializer_obj.save()
            setattr(obj, "max_score", 100)
            obj.save()
            return_data = serializer_obj.data
            return_data["id"] = obj.id
            return Response(data=return_data, status=status.HTTP_201_CREATED)
        return Response(data=serializer_obj.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProblem(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data["data"]
        problem = Problem.objects.get(id = request_data["id"])
        for key, value in request_data.items():
            if key == "tags":
                pass
            elif key != "id":
                setattr(problem, key, value)
        problem.save()
        return Response(status=status.HTTP_202_ACCEPTED)

class UploadTestCases(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        probId = request.data["probId"]
        problem = Problem.objects.get(id=probId)
        setattr(problem, "sample_Tc", request.data["custom_test_cases"])
        setattr(problem, "total_Tc", request.data["test_cases"])
        problem.save()
        for key, value in request.FILES.items():
            cloudinary.uploader.upload(
                request.FILES[key],
                resource_type="auto",
                public_id=key,
                folder=f"TestCases/{str(probId)}/",
            )
        return Response(status=status.HTTP_200_OK)


class GetProblem(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        prob_obj = Problem.objects.get(id=id)
        data = GetProblemSerializer(prob_obj)
        return Response(data=data.data, status=status.HTTP_200_OK)


class HandleUpvoteDownvote(APIView):
    permission_classes = (permissions.AllowAny,)

    def convert_to_list(self, data):
        try:
            return_data = ast.literal_eval(data)
        except:
            qery_list = json.dumps(data)
            return_data = ast.literal_eval(qery_list)
        return return_data

    def post(self, request):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data["data"]
        request_data["email"] = response["data"]["email"]

        problem_obj = Problem.objects.get(id=request_data["problem_id"])

        obj = UpvotesDownvote.objects.filter(mail_Id=request_data["email"])
        if len(obj) == 0:
            vote_object = UpvotesDownvote(
                mail_Id=request_data["email"], upvote="[]", downvote="[]"
            )
            vote_object.save()
        else:
            vote_object = obj.first()
        if request_data["type"] == "upvote":
            list_data = self.convert_to_list(vote_object.upvote)
            if request_data["problem_id"] in list_data:
                problem_obj.up_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.up_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "upvote", str(list_data))
            vote_object.save()
        elif request_data["type"] == "downvote":
            list_data = self.convert_to_list(vote_object.downvote)
            if request_data["problem_id"] in list_data:
                problem_obj.down_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.down_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "downvote", str(list_data))
            vote_object.save()
        else:
            list_data = self.convert_to_list(vote_object.upvote)
            if request_data["problem_id"] in list_data:
                problem_obj.up_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.up_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "upvote", str(list_data))
            vote_object.save()
            list_data = self.convert_to_list(vote_object.downvote)
            if request_data["problem_id"] in list_data:
                problem_obj.down_votes -= 1
                problem_obj.save()
                list_data.remove(request_data["problem_id"])
            else:
                problem_obj.down_votes += 1
                problem_obj.save()
                list_data.append(request_data["problem_id"])
            setattr(vote_object, "downvote", str(list_data))
            vote_object.save()
        return Response(status=status.HTTP_200_OK)


class GetProblemPageData(APIView):
    permission_classes = (permissions.AllowAny,)

    def convert_to_list(self, data):
        try:
            return_data = ast.literal_eval(data)
        except:
            qery_list = json.dumps(data)
            return_data = ast.literal_eval(qery_list)
        return return_data

    def get(self, request, id):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        request_data["problem_id"] = id
        request_data["email"] = response["data"]["email"]

        obj = UpvotesDownvote.objects.filter(mail_Id=request_data["email"])
        return_data = {
            "upvote": False,
            "downvote": False,
            "bookmarked": False,
            "submissions": 0,
        }
        submission_data = Submission.objects.filter(
            created_By=request_data["email"], problem_Id=request_data["problem_id"]
        )
        if len(submission_data) > 0:
            return_data["submissions"] = len(submission_data)
        bookmark_obj = Bookmark.objects.filter(user=request_data["email"])
        if len(bookmark_obj) != 0:
            bookmark_obj = bookmark_obj.first()
            bookmark_list = self.convert_to_list(bookmark_obj.data)
            if request_data["problem_id"] in bookmark_list:
                return_data["bookmarked"] = True
        if len(obj) == 0:
            return Response(data=return_data, status=status.HTTP_200_OK)
        obj = obj.first()
        list_data = self.convert_to_list(obj.upvote)
        if request_data["problem_id"] in list_data:
            return_data["upvote"] = True
            return Response(data=return_data, status=status.HTTP_200_OK)
        list_data = self.convert_to_list(obj.downvote)
        if request_data["problem_id"] in list_data:
            return_data["downvote"] = True
            return Response(data=return_data, status=status.HTTP_200_OK)
        return Response(data=return_data, status=status.HTTP_200_OK)


class GetSubmissionsList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        request_data["problem_id"] = id
        request_data["email"] = response["data"]["email"]

        data = Submission.objects.filter(
            created_By=request_data["email"], problem_Id=request_data["problem_id"]
        ).order_by("-submission_Date_Time")
        return_data = SubmissionListSerializer(data, many=True)
        return Response(data=return_data.data, status=status.HTTP_200_OK)


class HandleBookmark(APIView):
    permission_classes = (permissions.AllowAny,)

    def convert_to_list(self, data):
        try:
            return_data = ast.literal_eval(data)
        except:
            qery_list = json.dumps(data)
            return_data = ast.literal_eval(qery_list)
        return return_data

    def post(self, request):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        request_data["email"] = response["data"]["email"]

        obj = Bookmark.objects.filter(user=request_data["email"])
        print(obj)
        if len(obj) == 0:
            bookmark_object = Bookmark(user=request_data["email"], data="[]")
            bookmark_object.save()
        else:
            bookmark_object = obj.first()
        list_data = self.convert_to_list(bookmark_object.data)
        if request_data["problem_id"] in list_data:
            list_data.remove(request_data["problem_id"])
        else:
            list_data.append(request_data["problem_id"])
        setattr(bookmark_object, "data", list_data)
        bookmark_object.save()
        return Response(status=status.HTTP_200_OK)


class GetEditorial(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = Editorial.objects.filter(problem_Id=request.data["problem_id"])
        if len(data) > 0:
            data = EditorialSerializer(data.first())
            return Response(data=data.data, status=status.HTTP_200_OK)
        else:
            return Response(data="No Editorial Available", status=status.HTTP_200_OK)


class SaveCodeCloud(APIView):
    permissions = (permissions.AllowAny,)

    # @ratelimit(key='ip', rate='5/m')
    def post(self, request):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        request_data["email"] = response["data"]["email"]

        obj = SavedCode.objects.filter(
            problem_Id=request_data["probId"], created_By=request_data["email"]
        )
        if len(obj) > 0:
            obj = obj.first()
            setattr(obj, "code", encode_data(request_data["code"]))
            setattr(obj, "language", request_data["language"])
            setattr(obj, "submission_Date_Time", datetime.now())
            obj.save()
        else:
            SavedCode.objects.create(
                problem_Id=request_data["probId"],
                created_By=request_data["email"],
                code=encode_data(request_data["code"]),
                language=request_data["language"],
            )
        return Response(status=status.HTTP_200_OK)


class GetsavedCode(APIView):
    permissions = (permissions.AllowAny,)

    def get(self, request, id):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        request_data["problem_id"] = id
        request_data["email"] = response["data"]["email"]

        obj = SavedCode.objects.filter(
            problem_Id=request_data["problem_id"], created_By=request_data["email"]
        )
        data = SavedCodeSerializer(obj, many=True)
        return Response(data=data.data, status=status.HTTP_200_OK)


class GetUserSubmissions(APIView):
    permissions = (permissions.AllowAny,)

    def get(self, request):
        access_token = request.headers["Authorization"].split(" ")[1]
        response = middleware.Authentication.isAuthenticated(access_token)
        if not response["success"]:
            data = {"success": False, "message": "Unauthorized Request !"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)
        request_data = request.data
        request_data["email"] = response["data"]["email"]
        data = Submission.objects.filter(
            created_By=request_data["email"],
        ).order_by("-submission_Date_Time")
        return_data = AllSubmissionsSerializer(data, many=True)
        return Response(data=return_data.data, status=status.HTTP_200_OK)
