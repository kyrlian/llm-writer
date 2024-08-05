import requests

# Ollama exposes port 11434 by default


class Engine:
    def __init__(self, model_id="llama3", port=11434):
        self.model = model_id
        self.url = f"http://localhost:{port}/api"
        self.headers = {"Content-Type": "application/json"}

    def list(self):
        response = requests.get(f"{self.url}/tags", headers=self.headers)
        if response.status_code == 200:
            response_json = response.json()
            models = response_json["models"]
            modelnames = [m["name"] for m in models]
            return modelnames
        else:
            print("Error:", response.status_code, response.text)

    def generate(self, prompt, model=None):
        if model is None:
            model = self.model
        data = {"model": model, "stream": False, "prompt": prompt}
        response = requests.post(f"{self.url}/generate", headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            actual_response = response_json["response"]
            return actual_response
        else:
            print("Error:", response.status_code, response.text)


if __name__ == "__main__":
    en = Engine()
    print("list: " + ", ".join(en.list()))
    print("generate: " + en.generate("Who is obama?"))
