import requests
import json

# Ollama exposes port 11434 by default


class Engine:
    def __init__(self, model_id="llama3", port=11434, verbose=False):
        self.model = model_id
        self.url = f"http://localhost:{port}/api"
        self.headers = {"Content-Type": "application/json"}
        self.verbose = verbose

    def list(self):
        response = requests.get(f"{self.url}/tags", headers=self.headers)
        if response.status_code == 200:
            response_json = response.json()
            models = response_json["models"]
            modelnames = [m["name"] for m in models]
            return modelnames
        else:
            print("Error:", response.status_code, response.text)
            return []


    def generate_stream(self, prompt, model=None, temperature=None, max_tokens=None, stop=[]):
        if model is None:
            model = self.model
        options={"temperature":temperature, "num_predict":max_tokens, "stop":stop}
        data = {"model": model, "stream": True, "prompt": prompt, "options":options}
        response_stream = requests.post(f"{self.url}/generate", headers=self.headers, json=data)
        full_response=""
        current_line_num=0
        if response_stream.status_code == 200:
            for response_chunk_bytes in response_stream:
                response_chunk_string = response_chunk_bytes.decode("utf-8")
                full_response += response_chunk_string
                full_response_lines = full_response.splitlines()
                working_lines = full_response_lines[current_line_num:-1] # read after previous lines and skip last (incomplete)
                current_line_num += len(working_lines)
                for working_line in working_lines:
                    line_json = json.loads(working_line)
                    if self.verbose:
                        print("Response JSON:", line_json)
                    yield line_json["response"]
            # handle last line
            last_response = full_response.splitlines()[-1]
            last_json = json.loads(last_response)
            if self.verbose:
                print("Response JSON:", last_json)
            yield last_json["response"]
            # yield full_response
        yield ""
            

    def generate_response(self, prompt, model=None, temperature=None, max_tokens=None, stop=[]):
        if model is None:
            model = self.model
        options={"temperature":temperature, "num_predict":max_tokens, "stop":stop}
        data = {"model": model, "stream": False, "prompt": prompt, "options":options}
        response = requests.post(f"{self.url}/generate", headers=self.headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            if self.verbose:
                print("Response JSON:", response_json)
            return response_json
        else:
            print("Error:", response.status_code, response.text)
            return None

    def generate_text(self, prompt, model=None, temperature=None, max_tokens=None, stop=[]):
        response_json = self.generate_response(prompt, model, temperature, max_tokens, stop)
        if response_json is not None:
            actual_response = response_json["response"]
            return actual_response
        return None
    
    def generate(self, prompt, model=None, temperature=None, max_tokens=None, stop=[], stream=False):
        if stream:
            gen = self.generate_stream(prompt, model, temperature, max_tokens, stop)
            for g in gen:
                yield g 
        else:       
            return self.generate_text(prompt, model, temperature, max_tokens, stop)


if __name__ == "__main__":
    en = Engine()
    print("list: " + ", ".join(en.list()))
    print("generate: " + en.generate("Who is obama?"))
