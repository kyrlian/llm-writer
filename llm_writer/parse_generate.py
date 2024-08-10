from time import sleep
from typing import Generator

""" Template:
## Instructions

Text

---

Summary
"""

# Const
INSTRUCTION_TAG = "#"
SUMMARY_TAG = "---"

STATUS_NOTHING = "Nothing to do"
STATUS_GENERATE = "Generate"
STATUS_SUMMARY = "Summary"


def flush(texts, summaries, current_text, current_summary):
    if current_summary != "":
        summaries.append(current_summary)  # flush summary
    if current_text != "":
        texts.append(current_text)  # flush text
    return texts, summaries, "", ""


def parse_lines(lines):
    instructions = []
    texts = []
    summaries = []
    # lines = fulltext.splitlines()
    mode = "text"
    current_text = ""
    current_summary = ""
    for line in lines:
        if line.startswith(INSTRUCTION_TAG):  # instruction
            texts, summaries, current_text, current_summary = flush(
                texts, summaries, current_text, current_summary
            )
            instructions.append(line.replace(INSTRUCTION_TAG, ""))
            mode = "text"
        elif line == SUMMARY_TAG:  # summary
            texts, summaries, current_text, current_summary = flush(
                texts, summaries, current_text, current_summary
            )
            mode = "summary"
        else:
            if mode == "text":
                current_text += line + "\n"
            elif mode == "summary":
                current_summary += line + "\n"
    # last flush
    texts, summaries, _, _ = flush(texts, summaries, current_text, current_summary)
    return summaries, texts, instructions


def parse_and_generate(
    ollama_engine, fulltext, modelid, suggestpprompt, summaryprompt, include_input=True
):
    lines = fulltext.splitlines()
    last_line = lines[-1]
    prompt_template = None
    generated = ""
    status = STATUS_NOTHING
    if last_line.startswith(INSTRUCTION_TAG):  # instruction
        prompt_template = suggestpprompt
        status = STATUS_GENERATE
    elif last_line == SUMMARY_TAG:  # summary
        prompt_template = summaryprompt
        status = STATUS_SUMMARY
    if status is not STATUS_NOTHING:
        summaries, texts, instructions = parse_lines(lines)
        last_instruction = instructions[-1] if len(instructions) > 0 else ""
        last_text = texts[-1] if len(texts) > 0 else ""
        # all_summaries = "\n".join(summaries) if len(summaries) > 0 else ""
        # all_texts = "\n".join(texts) if len(texts) > 0 else ""
        previous_summaries = "\n".join(summaries[:-1]) if len(summaries) > 0 else ""
        prompt = prompt_template.format(
            summary=previous_summaries, text=last_text, instructions=last_instruction
        )
        generated = "\n" + ollama_engine.generate(prompt, model=modelid)
        if status == STATUS_GENERATE:
            status += ": " + last_instruction
    if include_input:
        return fulltext + "\n" + generated, status
    else:
        return generated, status

def parse_and_generate_stream(
    ollama_engine, fulltext, modelid, suggestpprompt, summaryprompt, include_input=True, cumulative=False
)-> Generator:
    lines = fulltext.splitlines()
    last_line = lines[-1]
    prompt_template = None
    status = STATUS_NOTHING
    if last_line.startswith(INSTRUCTION_TAG):  # instruction
        prompt_template = suggestpprompt
        status = STATUS_GENERATE
    elif last_line == SUMMARY_TAG:  # summary
        prompt_template = summaryprompt
        status = STATUS_SUMMARY
    if status is not STATUS_NOTHING:
        summaries, texts, instructions = parse_lines(lines)
        last_instruction = instructions[-1] if len(instructions) > 0 else ""
        last_text = texts[-1] if len(texts) > 0 else ""
        # all_summaries = "\n".join(summaries) if len(summaries) > 0 else ""
        # all_texts = "\n".join(texts) if len(texts) > 0 else ""
        previous_summaries = "\n".join(summaries[:-1]) if len(summaries) > 0 else ""
        prompt = prompt_template.format(
            summary=previous_summaries, text=last_text, instructions=last_instruction
        )
        ### STREAM
        if status == STATUS_GENERATE:
            status += ": " + last_instruction
        if include_input:
            yield fulltext, status
        yield (fulltext if cumulative else "")+"\n", status
        generate_stream = ollama_engine.generate(prompt, model=modelid, stream=True, cumulative=cumulative)
        for chunk in generate_stream:
            yield (fulltext+"\n" if cumulative else "")+ chunk, status
            # sleep(.1)
    else:
        yield fulltext+"\n" if include_input else "", status
