import requests, json, base64, urllib3
from problems.models import Problem

BASE_URL = "https://res.cloudinary.com/hhikcz56h/raw/upload/v1636969572/TestCases/"
http = urllib3.PoolManager()


language_mapping = {
    "C++" : 53,
    "C" : 48,
    "Java" : 26,
    "Python 2" : 36,
    "Python 3" : 71
}

def runcode_helper(req_data):
    url = "https://judge0-ce.p.rapidapi.com/submissions"
    querystring = {"base64_encoded":"true","wait":"true","fields":"*"}
    payload = {
        "language_id" : language_mapping[req_data["lang"]],
        "source_code" : req_data["code"],
        "stdin" : req_data["input"]
    }
    headers = {
        'content-type': "application/json",
        'x-rapidapi-host': "judge0-ce.p.rapidapi.com",
        'x-rapidapi-key': "3bad142ebamshd424a4c3b68c90ep1da74ajsneb947385a6ff"
    }
    res = requests.request("POST", url, data = json.dumps(payload), headers = headers, params = querystring)
    return res.json()


def runCustomTestCases(req_data):
    probId = req_data["problem_Id"]
    prob = Problem.objects.get(id = probId)
    totaltc = prob.sample_Tc
    for i in range(1, totaltc+1):
        input_target_url = BASE_URL + str(probId) + "/" + f"sc-input{str(i)}.txt"
        input_response = http.request('GET', input_target_url)
        input_data = input_response.data.decode('utf-8')
        data = {
            "code" : req_data["code"],
            "lang" : req_data["language"],
            "input" : encode_data(input_data.strip())
        }
        result = runcode_helper(data)
        if result["status"]["description"] == "Accepted":
            if result["stdout"]:
                decoded_stdout = decode_data(result["stdout"])
                decoded_stdout = decoded_stdout.strip()
                output_target_url = BASE_URL + str(probId) + "/" + f"sc-output{str(i)}.txt"
                output_response = http.request('GET', output_target_url)
                output_data = output_response.data.decode('utf-8')
                output_data = output_data.strip()
                if output_data != decoded_stdout:
                    return {"status" : "error", "error" : f"Wrong Ans", "testCase No" : i}
            else:
                return {"status" : "error", "error" : f"No Output Generated", "testCase No" : i}
                
        else:
            status = result["status"]["description"]
            if result["compile_output"]:
                return {"status" : status, "error" : decode_data(result["compile_output"]), "testCase No" : i}
            if result["stderr"]:
                return {"status" : status, "error" : decode_data(result["stderr"]), "testCase No" : i}
            else:
                return {"status" : status, "error" : None, "testCase No" : i}
    return {"status" : "Accepted", "error" : None};


def encode_data(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def decode_data(base64_message):
    return base64.b64decode(base64_message).decode("utf-8")