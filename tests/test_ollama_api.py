import requests
import json

# Ollama exposes port 11434 by default
url = "http://localhost:11434/api/generate"

headers = {"Content-Type": "application/json"}

data = {"model": "llama3", "stream": False, "prompt": "Why earth is revolves?"}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    response_txt = response.text
    data = json.loads(response_txt)
    actual_response = data["response"]
    print(actual_response)
else:
    print("Error:", response.status_code, response.text)
