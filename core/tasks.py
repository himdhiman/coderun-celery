import os, urllib3
from celery import shared_task
from problems.serializers import SubmissionSerializer
from pathlib import Path
from problems.models import Problem, Submission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers as djSerializer
from problems import middleware
from core.helper import runcode_helper, encode_data, decode_data

BASE_DIR = Path(__file__).resolve().parent.parent
channel_layer = get_channel_layer()
http = urllib3.PoolManager()
BASE_URL = "https://res.cloudinary.com/hhikcz56h/raw/upload/v1636969572/TestCases/"

@shared_task(bind = True)
def runCode(discarded_arg, context):
    body = context["body"]
    response = SubmissionSerializer(data = body)
    if(response.is_valid()):
        inst = response.save()
        setattr(inst, "status", "Running")
        inst.save()
        probId = body["problem_Id"]
        prob = Problem.objects.get(id = probId)
        totaltc = prob.total_Tc
        counter = 0
        temp_result = "Accepted"
    
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
                else:
                    setattr(inst, "status", "Wrong Answer")
                    inst.save()
                    async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : "Wrong Ans"})
            else:
                status = result["status"]["description"]
                temp_result = status + " - " + str(counter + 1)
                setattr(inst, "error", decode_data(result["compile_output"]))
                setattr(inst, "status", status)
                inst.save()
                async_to_sync(channel_layer.group_send)("user_" + str(context["uid"]), {'type': 'sendStatus', 'text' : f"{status}/{i}/{totaltc}"})
                async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : status})
                break
        if counter == totaltc:
            setattr(inst, "status", "Accepted")
        else:
            setattr(inst, "status", temp_result)
        setattr(inst, "test_Cases_Passed", counter)
        setattr(inst, "total_Test_Cases", totaltc)
        setattr(inst, "score", int((counter/totaltc))*prob.max_score)
        setattr(inst, "total_score", prob.max_score)
        inst.save()
        response = Submission.objects.filter(id = inst.id)
        async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})
        async_to_sync(channel_layer.group_send)("user_" + context["uid"], {'type': 'sendResult', 'text' : "Completed"})