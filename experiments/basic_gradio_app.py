# https://www.langchain.ca/blog/chatgpt-clone-with-ollama-gradio/

import requests
import json
import gradio as gr

url = "http://localhost:11434/api/generate"

headers = {"Content-Type": "application/json"}


def generate_response(prompt):
    data = {"model": "llama2", "stream": False, "prompt": prompt}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_txt = response.text
        data = json.loads(response_txt)
        actual_response = data["response"]
        return actual_response
    else:
        print("Error:", response.status_code, response.text)


iface = gr.Interface(fn=generate_response, inputs=["text"], outputs=["text"])

if __name__ == "__main__":
    iface.launch()
