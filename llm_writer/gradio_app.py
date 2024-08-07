import gradio as gr

from engine_ollama import Engine as ollamaEngine
from prompts import prompts
from fileio import load, save
from custom_style import MyStyle
from parse_generate import parse_and_generate, SUMMARY_TAG, INSTRUCTION_TAG

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
initialtext = load()
ollama_engine = ollamaEngine()
default_lang = list(prompts.keys())[0]
prompt_suggest, prompt_summarize = changelang(default_lang)

def fulltext_box_submit(fulltext, modelid, suggestpprompt, summaryprompt):
    generated, status = parse_and_generate(ollama_engine, fulltext, modelid, suggestpprompt, summaryprompt)
    return generated, status

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
