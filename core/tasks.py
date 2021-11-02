import os, base64
from celery import shared_task
from problems import models, serializers
from pathlib import Path
from problems.models import Problem, Submission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers as djSerializer
from problems import middleware
from core.helper import runcode_helper

BASE_DIR = Path(__file__).resolve().parent.parent
channel_layer = get_channel_layer()

@shared_task(bind = True)
def runCode(discarded_arg, context):
    print(context)
    body = context["body"]
    response = serializers.SubmissionSerializer(data = body)
    if(response.is_valid()):
        inst = response.save()
        probId = body["problem_Id"]
        prob = models.Problem.objects.get(id = probId)
        totaltc = prob.total_Tc
        print(totaltc)
    
        for i in range(1, totaltc+1):
            print(1)
            isSame = True
            inpPath = os.path.join(BASE_DIR, "media", 'TestCases', str(probId), 'tc-input'+str(i)+'.txt')
            input_data = open(inpPath, 'r').read()
            print(input_data)
            data = {
                "code" : body["code"],
                "lang" : body["language"],
                "input" : base64.b64encode(input_data.encode('ascii')) 
            }
            result = runcode_helper(data)
            print(result)
    else:
        print("invalid", response.error_messages)

        #     with open(os.path.join(BASE_DIR, "media", 'TestCases', str(probId), 'tc-output'+str(i)+'.txt')) as f1, open(outPath) as f2:
        #         for line1, line2 in zip(f1, f2):
        #             if line1 != line2:
        #                 isSame = False
        #                 break
        #     if(isSame):
        #         cnt += 1
        #         async_to_sync(channel_layer.group_send)("user_"+str(uid), {'type': 'sendStatus', 'text' : f"1/{i}/{totaltc}"})
        #     else:
        #         async_to_sync(channel_layer.group_send)("user_"+str(uid), {'type': 'sendStatus', 'text' : f"0/{i}/{totaltc}"})
        # os.system(f"rm -rf {outPath}")
        # os.system(f"touch {outPath}")
                
    #         else:
    #             os.system(f'{bashPath} < {inpPath} > {outPath}')

    #         os.system(f'g++ {progPath} 2> {logPath}')

    #     if data['lang'] == "P3":
    #         os.system('python main.py < input.txt > output.txt 2>"output.log"')
    #     os.chdir(BASE_DIR)
    #     out = open(os.path.join(tempPath, 'output.txt'), "r")
    #     code_output = out.read()
    #     out.close()
    #     os.system(f"rm -rf {inpPath}")
    #     os.system(f"touch {inpPath}")
    #     tcString = str(cnt) + "/" + str(totaltc)
    #     if os.stat(os.path.join(tempPath, "output.log")).st_size != 0:
    #         f = open(os.path.join(tempPath, "output.log"), "r")
    #         error = f.read()
    #         f.close()
    #         os.system(f"rm -rf {tempPath}")
    #         Submission.objects.filter(pk = data['id']).update(error = error, status = "CE", testCasesPassed = tcString)
    #     else:
    #         os.system(f"rm -rf {tempPath}")
    #         Submission.objects.filter(pk = data['id']).update(outputGen = code_output, status = "AC", testCasesPassed = tcString)

    #     response = models.Submission.objects.filter(id = inst.id)
    #     async_to_sync(channel_layer.group_send)("user_"+str(uid), {'type': 'sendResult', 'text' : djSerializer.serialize('json', response)})