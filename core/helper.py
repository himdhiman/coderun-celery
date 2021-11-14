import requests, json, base64

language_mapping = {
    "C++ 17" : 53,
    "C++ 14" : 52,
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

def encode_data(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def decode_data(base64_message):
    return base64.b64decode(base64_message).decode("utf-8")