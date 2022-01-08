import os, urllib3, requests
from celery import shared_task
from problems.serializers import SubmissionSerializer
from pathlib import Path
from problems.models import Problem, Submission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers as djSerializer
from django.db.models import F
from problems import middleware
from core.helper import runcode_helper, encode_data, decode_data
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent
channel_layer = get_channel_layer()
http = urllib3.PoolManager()
BASE_URL = "https://res.cloudinary.com/hhikcz56h/raw/upload/v1636969572/TestCases/"

@shared_task(bind = True)
def runCode(self, context):
    body = context["body"]
    response = SubmissionSerializer(data = body)
    if(response.is_valid()):
        inst = response.save()
        setattr(inst, "status", "Running")
        setattr(inst, "task_id", self.request.id)
        inst.save()
        probId = body["problem_Id"]
        prob = Problem.objects.get(id = probId)
        totaltc = prob.total_Tc
        counter = 0
    
        for i in range(1, totaltc+1):
            input_target_url = BASE_URL + str(probId) + "/" + f"tc-input{str(i)}.txt"
            input_response = http.request('GET', input_target_url)
            input_data = input_response.data.decode('utf-8')
            data = {
                "code" : body["code"],
                "lang" : body["language"],
                "input" : encode_data(input_data.strip())
            }
            result = runcode_helper(data)
            if result["status"]["description"] == "Accepted":
                if result["stdout"]:
                    decoded_stdout = decode_data(result["stdout"])
                    decoded_stdout = decoded_stdout.strip()
                    output_target_url = BASE_URL + str(probId) + "/" + f"tc-output{str(i)}.txt"
                    output_response = http.request('GET', output_target_url)
                    output_data = output_response.data.decode('utf-8')
                    output_data = output_data.strip()
                    if output_data == decoded_stdout:
                        counter += 1
                        async_to_sync(channel_layer.group_send)("user_" + str(context["uid"]), {'type': 'sendStatus', 'text' : f"Passed/{i}/{totaltc}"})
                    else:
                        async_to_sync(channel_layer.group_send)("user_" + str(context["uid"]), {'type': 'sendStatus', 'text' : f"Wrong Answer/{i}/{totaltc}"})
                        setattr(inst, "status", "Wrong Answer")
                        setattr(inst, "test_Cases_Passed", counter)
                        setattr(inst, "total_Test_Cases", totaltc)
                        setattr(inst, "score", int((counter/totaltc))*prob.max_score)
                        setattr(inst, "total_score", prob.max_score)
                        inst.save()
                        response = Submission.objects.filter(id = inst.id)
                        async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})
                        return
                else:
                    async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendStatus', 'text' : f"Wrong Answer/{i}/{totaltc}"})
                    setattr(inst, "status", "Wrong Answer")
                    setattr(inst, "test_Cases_Passed", counter)
                    setattr(inst, "total_Test_Cases", totaltc)
                    setattr(inst, "score", int((counter/totaltc))*prob.max_score)
                    setattr(inst, "total_score", prob.max_score)
                    inst.save()
                    response = Submission.objects.filter(id = inst.id)
                    async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})
                    return
            else:
                status = result["status"]["description"]
                async_to_sync(channel_layer.group_send)("user_" + str(context["uid"]), {'type': 'sendStatus', 'text' : f"{status}/{i}/{totaltc}"})
                if result["compile_output"]:
                    setattr(inst, "error", decode_data(result["compile_output"]))
                if result["stderr"]:
                    setattr(inst, "error", decode_data(result["stderr"]))
                setattr(inst, "status", status)
                setattr(inst, "test_Cases_Passed", counter)
                setattr(inst, "total_Test_Cases", totaltc)
                setattr(inst, "score", int((counter/totaltc))*prob.max_score)
                setattr(inst, "total_score", prob.max_score)
                inst.save()
                response = Submission.objects.filter(id = inst.id)
                async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})
                return
        if counter == totaltc:
            setattr(inst, "status", "Accepted")
        else:
            setattr(inst, "status", "Error not defined")
        prev_submissions = Submission.objects.filter(created_By = inst.created_By, problem_Id = inst.problem_Id, score = F('total_score'))
        setattr(inst, "test_Cases_Passed", counter)
        setattr(inst, "total_Test_Cases", totaltc)
        setattr(inst, "score", int((counter/totaltc))*prob.max_score)
        setattr(inst, "total_score", prob.max_score)
        inst.save()
        response = Submission.objects.filter(id = inst.id)
        if len(prev_submissions) == 0:
            requests.post(settings.AUTH_SERVER_URL, data = {
                "email" : inst.created_By,
                "inc" : prob.max_score
            })
            async_to_sync(channel_layer.group_send)("user_" + str(context["uid"]), {'type': 'sendStatus', 'text' : "inc_submissions/none/none"})
            async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})
            prob_obj = Problem.objects.get(id = inst.problem_Id)
            prob_obj.totalSubmissions = prob_obj.totalSubmissions + 1;
            prob_obj.save()
        else:
            async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})
        return