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
    for l in lines:
        if l.startswith(INSTRUCTION_TAG):  # instruction
            texts, summaries, current_text, current_summary = flush(
                texts, summaries, current_text, current_summary
            )
            instructions.append(l.replace(INSTRUCTION_TAG, ""))
            mode = "text"
        elif l == SUMMARY_TAG:  # summary
            texts, summaries, current_text, current_summary = flush(
                texts, summaries, current_text, current_summary
            )
            mode = "summary"
        else:
            if mode == "text":
                current_text += l + "\n"
            elif mode == "summary":
                current_summary += l + "\n"
    # last flush
    texts, summaries, _, _ = flush(texts, summaries, current_text, current_summary)
    print(
        f"""========= parse_lines() =========
        == summaries ==
        => {"\n => ".join(summaries)}
        == texts ==
        => {"\n => ".join(texts)}
        == instructions ==
        => {"\n => ".join(instructions)}"""
    )
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
        print(
            f"""========= fulltext_box_submit() =========
            == status ==
            => {status}
            == prompt ==
            => {prompt}
            == generated ==
            => {generated}"""
        )
        if status == STATUS_GENERATE:
            status += ": " + last_instruction
    if include_input:
        return fulltext + "\n" + generated, status
    else:
        return generated, status
