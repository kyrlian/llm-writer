import gradio as gr

from ollama import generate_response
from prompts import prompts
from fileio import load, save

sdxlturbo_loaded = False
try:
    from sdxlturbo import sdxlturboPipeline

    sdxlturbo_loaded = True
except ImportError:
    print(f"Couldn't load sdxlturbo, deactivating image generation")


def changelang(lang):
    return prompts[lang]["prompt_suggest"], prompts[lang]["prompt_summarize"]


def suggest(suggestpprompt, fulltext, fullsummary, instructions):
    prompt = suggestpprompt.format(
        fulltext=fulltext, fullsummary=fullsummary, instructions=instructions
    )
    return generate_response(prompt)


def summarize(summaryprompt, fulltext, tmptext):
    prompt = summaryprompt.format(fulltext=fulltext, tmptext=tmptext)
    return generate_response(prompt)


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


def buildapp(initialtext, initialsummary, prompts):
    default_lang = list(prompts.keys())[0]
    prompt_suggest, prompt_summarize = changelang(default_lang)
    # https://www.gradio.app/guides/blocks-and-event-listeners#blocks-structure
    with gr.Blocks() as myapp:
        with gr.Row():
            gr.Markdown("# LLM Writer")
            lang_drop = gr.Dropdown(
                choices=list(prompts.keys()),
                value=default_lang,
                label="Language",
                show_label=False,
            )
        # https://www.gradio.app/guides/controlling-layout#rows
        with gr.Row():
            with gr.Column():
                suggestpprompt_box = gr.Textbox(
                    value=prompt_suggest,
                    label="Suggestion prompt - use {fulltext}, {fullsummary}, {instructions} placeholders",
                )
                fullsummary_box = gr.Textbox(
                    value=initialsummary, label="Full Summary - {fullsummary}"
                )
                instructions_box = gr.Textbox(label="Instructions - {instructions}")
            with gr.Column():
                summaryprompt_box = gr.Textbox(
                    value=prompt_summarize,
                    label="Summary prompt - use {fulltext}, {tmptext} placeholders",
                )
                fulltext_box = gr.Textbox(
                    value=initialtext, label="Full Text - {fulltext}"
                )
        with gr.Column():
            suggest_btn = gr.Button("Suggest")
            tmptext_box = gr.Textbox(label="Temp text")
            summarize_btn = gr.Button("Summarize")
            tmpsummary_box = gr.Textbox(label="Temp summary")
            accept_btn = gr.Button("Accept")
            save_btn = gr.Button("Save")
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
            fn=suggest,
            inputs=[
                suggestpprompt_box,
                fulltext_box,
                fullsummary_box,
                instructions_box,
            ],
            outputs=tmptext_box,
            api_name="suggest",
        )
        summarize_btn.click(
            fn=summarize,
            inputs=[summaryprompt_box, fulltext_box, tmptext_box],
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
    return myapp


if __name__ == "__main__":
    initialtext, initialsummary = load()
    buildapp(initialtext, initialsummary, prompts).launch()
