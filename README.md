# llm-writer

## Inputs/Outputs
- 1 instructions
- 2 context & summary
- 3 payload / full text
- 4 logs

## Actions
- generate : 1,2,3 => 3
- summarize : last $ of 3 => +2
- save / restore : 1,2,3 <=> json

## Technology
- dash
- ollama python