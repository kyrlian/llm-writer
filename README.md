# llm-writer

## Design
### Inputs/Outputs
- 1 instructions
- 2 context & summary
- 3 payload / full text
- 4 logs

### Actions
- generate : 1,2,3 => 3
- summarize : last $ of 3 => +2
- save / restore : 1,2,3 <=> json

### Technology
- gradio
- ollama 
- python

## Install

- Install [ollama](https://ollama.com/)
- Get ollama model:
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
python main.py
```

## Ressources

- https://www.langchain.ca/blog/chatgpt-clone-with-ollama-gradio/