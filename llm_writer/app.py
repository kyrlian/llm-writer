import gradio as gr

from engine_ollama import Engine as ollamaEngine
from prompts import prompts
from fileio import load, save
from custom_style import MyStyle

# Init sdxlturbo
sdxlturbo_loaded = False
try:
    from sdxlturbo import sdxlturboPipeline

    sdxlturbo_loaded = True
except ImportError:
    print(f"Couldn't load sdxlturbo, deactivating image generation")


def changelang(lang):
    return prompts[lang]["prompt_suggest"], prompts[lang]["prompt_summarize"]


""" Template:
## Instructions

Text

---

Summary
"""

# Const
INSTRUCTION_TAG = "#"
SUMMARY_TAG = "---"

# Init LLM
initialtext = load()
default_lang = list(prompts.keys())[0]
prompt_suggest, prompt_summarize = changelang(default_lang)
ollama_engine = ollamaEngine()


# Functions
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


def fulltext_box_submit(fulltext, modelid, suggestpprompt, summaryprompt):
    lines = fulltext.splitlines()
    last_line = lines[-1]
    prompt_template = None
    generated = ""
    status = "Nothing to do"
    if last_line.startswith(INSTRUCTION_TAG):  # instruction
        prompt_template = suggestpprompt
        status = "Generate"
    elif last_line == SUMMARY_TAG:  # summary
        prompt_template = summaryprompt
        status = "Summary"
    if prompt_template is not None:
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
        if status == "Generate":
            status += ": " + last_instruction
    return fulltext + "\n" + generated, status


def generate_image(imglist, prompt):
    if sdxlturbo_loaded:
        pipe = sdxlturboPipeline()
        img = pipe.generate(prompt)
        if imglist is None:
            imglist = []
        imglist.append(img)
    return imglist


# App
# https://www.gradio.app/guides/blocks-and-event-listeners#blocks-structure
with gr.Blocks(theme=MyStyle()) as demo:
    gr.Markdown("# LLM Writer")
    # https://www.gradio.app/guides/controlling-layout#rows
    with gr.Accordion(label="Setup", open=True):
        lang_drop = gr.Dropdown(
            choices=list(prompts.keys()),
            value=default_lang,
            label="Language",
            show_label=False,
        )
        with gr.Row():
            suggestpprompt_box = gr.Textbox(
                value=prompt_suggest,
                label="Suggestion prompt",
            )
            summaryprompt_box = gr.Textbox(
                value=prompt_summarize,
                label="Summary prompt",
            )
        model_list = ollama_engine.list()
        model_drop = gr.Dropdown(label="Model", choices=model_list, value=model_list[0])
        generate_image_check = gr.Checkbox(
            label="Generate Image with sdxlturbo",
            value=False,
            visible=sdxlturbo_loaded,
        )
    fulltext_box = gr.Textbox(
        value=initialtext,
        label="Text",
        info=f"Use {INSTRUCTION_TAG} to start an instruction, {SUMMARY_TAG} to end a paragraph and generate a summary.",
        show_copy_button=True,
    )
    save_btn = gr.Button("Save to file")
    # image generation
    generate_image_btn = gr.Button("Generate Image", visible=False)
    img_gallery = gr.Gallery(
        label="Illustrations",
        rows=1,
        columns=3,
        interactive=False,
        visible=False,
    )
    status_box = gr.Markdown(label="Status")

    # match button - function
    def sdxlturbo_toggled(toggle):
        return gr.Button(visible=toggle), gr.Gallery(visible=toggle)

    generate_image_check.change(
        fn=sdxlturbo_toggled,
        inputs=generate_image_check,
        outputs=[generate_image_btn, img_gallery],
    )

    lang_drop.change(
        fn=changelang,
        inputs=[lang_drop],
        outputs=[suggestpprompt_box, summaryprompt_box],
        api_name="changelang",
    )

    fulltext_box.submit(
        fn=fulltext_box_submit,
        inputs=[fulltext_box, model_drop, suggestpprompt_box, summaryprompt_box],
        outputs=[fulltext_box, status_box],
    )

    save_btn.click(
        fn=save,
        inputs=fulltext_box,
        outputs=status_box,
        api_name="save",
    )


if __name__ == "__main__":
    demo.launch()
