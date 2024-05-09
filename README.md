# llm-writer

## Design
### Inputs/Outputs
- 1 System instructions for a/ generation and b/ summary (can be edited by user, but shouldn't need to)
- 2 a/ Full text and b/ summary
- 3 User instruction to generate new text  
- 4 a/ Temp text & b/ temp summary for review

### Actions
- Generate : 1a, 2b, 3 => 4a
- Summarize : 1b, 2a => 4b
- Accept text: 2a, 4a => 2a 
- Accept summary: 4b => 2b

### Technology
- [gradio](https://www.gradio.app/)
- [ollama](https://ollama.com/)
- [python](https://www.python.org/)

## Install

- Install [ollama](https://ollama.com/)
- Get ollama model (can be changed in [ollama.py](./app/ollama.py)):
```sh
ollama serve
ollama list
ollama pull llama3
```

- Clone and install requirements:
```sh
git clone https://github.com/kyrlian/llm-writer.git
cd llm-writer
pip install -r requirements.txt -U
```

## Run

```sh
python app/main.py
```

## Ressources

- https://www.langchain.ca/blog/chatgpt-clone-with-ollama-gradio/