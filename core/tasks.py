import os
from celery import shared_task
from problems import models, serializers
from pathlib import Path
from problems.models import Problem, Submission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers as djSerializer
from problems import middleware

BASE_DIR = Path(__file__).resolve().parent.parent
channel_layer = get_channel_layer()

@shared_task(bind = True)
def runCode(discarded_arg, context):
    print(f"body - {context}")
    response = serializers.SubmissionSerializer(data = context["body"])
    if(response.is_valid()):
        inst = response.save()
    
    else:
        print("invalid")

    #     if(inst.inputGiven != ""):
    #         data = {'id' : inst.id, 'code' : inst.code, 'lang' : inst.language, 'inp' : inst.inputGiven, 'problemId' : inst.problemId}
    #     else:
    #         data = {'id' : inst.id, 'code' : inst.code, 'lang' : inst.language, 'problemId' : inst.problemId}

    #     probId = data['problemId']
    #     totaltc = Problem.objects.get(id = probId).totalTC

    #     tempPath = os.path.join(BASE_DIR, "Codes", str(uid))
    #     os.system(f"mkdir {tempPath}")

    #     inpPath = tempPath+"/"+"input.txt"
    #     os.system(f"touch {inpPath}")
    #     outPath = tempPath+"/"+"output.txt"
    #     os.system(f"touch {outPath}")
    #     logPath = tempPath+"/"+"output.log"
    #     os.system(f"touch {logPath}")
    #     progPath = None
    #     bashPath = tempPath+"/"+"a.out"

    #     if data['lang'] == "CP":
    #         progPath = tempPath+"/"+"main.cpp"
    #         os.system(f"touch {progPath}")
    #         f = open(os.path.join(tempPath, 'main.cpp'), "w")
    #         f.write(data['code'])
    #         f.close()

    #     if data['lang'] == "P3":
    #         progPath = tempPath+"/"+"main.py"
    #         os.system(f"touch {progPath}")
    #         f = open(os.path.join(tempPath, 'main.py'), "w")
    #         f.write(data['code'])
    #         f.close()

    #     isInputGiven = False

    #     if('inp' in data.keys() and data['inp'] != None):
    #         isInputGiven = True
    #         f = open(inpPath, "w")
    #         f.write(data['inp'])
    #         f.close()

    #     os.chdir(tempPath)
    #     if data['lang'] == "CP":
    #         os.system(f'g++ {progPath}')
    #         cnt = 0
    #         if(isInputGiven == False):
    #             for i in range(1, totaltc+1):
    #                 isSame = True
    #                 inpPath = os.path.join(BASE_DIR, "media", 'TestCases', str(probId), 'input'+str(i)+'.txt')
    #                 os.system(f'{bashPath} < {inpPath} > {outPath}')
    #                 with open(os.path.join(BASE_DIR, "media", 'TestCases', str(probId), 'output'+str(i)+'.txt')) as f1, open(outPath) as f2:
    #                     for line1, line2 in zip(f1, f2):
    #                         if line1 != line2:
    #                             isSame = False
    #                             break
    #                 if(isSame):
    #                     cnt += 1
    #                     async_to_sync(channel_layer.group_send)("user_"+str(uid), {'type': 'sendStatus', 'text' : f"1/{i}/{totaltc}"})
    #                 else:
    #                     async_to_sync(channel_layer.group_send)("user_"+str(uid), {'type': 'sendStatus', 'text' : f"0/{i}/{totaltc}"})
    #             os.system(f"rm -rf {outPath}")
    #             os.system(f"touch {outPath}")
                
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