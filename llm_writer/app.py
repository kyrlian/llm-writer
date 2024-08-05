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

# Init LLM
initialtext, initialsummary = load()
default_lang = list(prompts.keys())[0]
prompt_suggest, prompt_summarize = changelang(default_lang)
ollama_engine = ollamaEngine()

# Functions
def llm_suggest(modelid, suggestpprompt, summaryprompt, fulltext, fullsummary, instructions):
    prompt = suggestpprompt.format(
        fulltext=fulltext, fullsummary=fullsummary, instructions=instructions
    )
    new_text = ollama_engine.generate(prompt, model=modelid)
    summary_prompt = summaryprompt.format(fulltext=fulltext, tmptext=new_text)

    new_summary = ollama_engine.generate(summary_prompt, model=modelid)
    return new_text, new_summary


def llm_summarize(modelid, summaryprompt, fulltext, tmptext):
    summary_prompt = summaryprompt.format(fulltext=fulltext, tmptext=new_text)
    new_summary = ollama_engine.generate(summary_prompt, model=modelid)
    return new_summary

def generate_image(imglist, prompt):
    if sdxlturbo_loaded:
        pipe = sdxlturboPipeline()
        img = pipe.generate(prompt)
        if imglist is None:
            imglist = []
        imglist.append(img)
    return imglist


def accept(fulltext, tmptext, fullsummary, tmpsummary, imglist):
    return (
        f"{fulltext}\n\n{tmptext}",
        f"{fullsummary}\n\n{tmpsummary}",
        generate_image(imglist, tmpsummary),
    )

# App
# https://www.gradio.app/guides/blocks-and-event-listeners#blocks-structure
with gr.Blocks(theme=MyStyle()) as demo:
    gr.Markdown("# LLM Writer")
    # https://www.gradio.app/guides/controlling-layout#rows
    with gr.Accordion(label="Setup",open=True):
        lang_drop = gr.Dropdown(
            choices=list(prompts.keys()),
            value=default_lang,
            label="Language",
            show_label=False,
        )
        with gr.Row():
            suggestpprompt_box = gr.Textbox(
                value=prompt_suggest,
                label="Suggestion prompt - use {fulltext}, {fullsummary}, {instructions} placeholders",
            )
            summaryprompt_box = gr.Textbox(
                value=prompt_summarize,
                label="Summary prompt - use {fulltext}, {tmptext} placeholders",
            )
        model_list = ollama_engine.list()
        model_drop = gr.Dropdown(label="Model", choices=model_list, value=model_list[0])# TODO get ollama models
        if sdxlturbo_loaded:
            generate_image_check = gr.Checkbox(label="Generate Image with sdxlturbo",value=True)
    fulltext_box = gr.Textbox(
        value=initialtext, label="Full Text - {fulltext}"
    )
    fullsummary_box = gr.Textbox(
        value=initialsummary, label="Full Summary - {fullsummary}"
    )

    instructions_box = gr.Textbox(label="Instructions - {instructions}")
    suggest_btn = gr.Button("Suggest")
    tmptext_box = gr.Textbox(label="Temp text - {tmptext}")
    summarize_btn = gr.Button("Summarize")
    tmpsummary_box = gr.Textbox(label="Temp summary")
    accept_btn = gr.Button("Accept")
    # add option to generate image
    save_btn = gr.Button("Save to file")
    status_box = gr.Markdown(label="Status")
    img_gallery = gr.Gallery(label="Illustrations",rows=1, columns=3, interactive=False, visible=sdxlturbo_loaded)

    # match button - function
    lang_drop.change(
        fn=changelang,
        inputs=[lang_drop],
        outputs=[suggestpprompt_box, summaryprompt_box],
        api_name="changelang",
    )
    suggest_btn.click(
        fn=llm_suggest,
        inputs=[model_drop,
            suggestpprompt_box,
            summaryprompt_box,
            fulltext_box,
            fullsummary_box,
            instructions_box,
        ],
        outputs=[tmptext_box, tmpsummary_box],
        api_name="suggest",
    )
    summarize_btn.click(
        fn=llm_summarize,
        inputs=[model_drop, summaryprompt_box, fulltext_box, tmptext_box],
        outputs=tmpsummary_box,
        api_name="summarize",
    )
    accept_btn.click(
        fn=accept,
        inputs=[
            fulltext_box,
            tmptext_box,
            fullsummary_box,
            tmpsummary_box,
            img_gallery,
        ],
        outputs=[fulltext_box, fullsummary_box, img_gallery],
        api_name="accept",
    )
    save_btn.click(
        fn=save,
        inputs=[fulltext_box, fullsummary_box],
        outputs=status_box,
        api_name="save",
    )


if __name__ == "__main__":
    demo.launch()
