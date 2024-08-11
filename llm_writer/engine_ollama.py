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


    def generate_stream(self, prompt, model=None, temperature=None, max_tokens=None, stop=[], cumulative = False):
        if model is None:
            model = self.model
        options={"temperature":temperature, "num_predict":max_tokens, "stop":stop}
        data = {"model": model, "stream": True, "prompt": prompt, "options":options}
        response_stream = requests.post(f"{self.url}/generate", headers=self.headers, json=data)
        if response_stream.status_code == 200:
            full_response_string=""
            current_line_num=0
            full_generated = ""
            for response_chunk_bytes in response_stream:
                response_chunk_string = response_chunk_bytes.decode("utf-8")
                full_response_string += response_chunk_string
                full_response_lines = full_response_string.splitlines()
                working_lines = full_response_lines[current_line_num:-1] # read after previous lines and skip last (incomplete)
                current_line_num += len(working_lines)
                for working_line in working_lines:
                    line_json = json.loads(working_line)
                    if self.verbose:
                        print("Response JSON:", line_json)
                    generated = line_json["response"]
                    if cumulative:
                        full_generated += generated
                        yield full_generated
                    else:
                        yield generated
            # handle last line
            last_response = full_response_string.splitlines()[-1]
            last_json = json.loads(last_response)
            if self.verbose:
                print("Response JSON:", last_json)
            generated = last_json["response"]
            if cumulative:
                full_generated += generated
                yield full_generated
            else:
                yield generated
        else:
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
    
    def generate(self, prompt, model=None, temperature=None, max_tokens=None, stop=[], stream=False, cumulative= False):
        if stream:
            return self.generate_stream(prompt, model, temperature, max_tokens, stop, cumulative)
            # for g in gen:
            #     yield g 
        else:       
            return self.generate_text(prompt, model, temperature, max_tokens, stop)


if __name__ == "__main__":
    en = Engine()
    print("list: " + ", ".join(en.list()))
    print("generate: " + en.generate("Who is obama?"))
