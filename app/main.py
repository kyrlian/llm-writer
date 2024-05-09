import gradio as gr

from ollama import generate_response
from prompts import prompt_summarize, prompt_suggest
from fileio import load, save


def suggest(suggestpprompt, fullsummary, instructions):
    prompt = suggestpprompt.format(fullsummary=fullsummary, instructions=instructions)
    return generate_response(prompt)


def summarize(summaryprompt, fulltext):
    prompt = summaryprompt.format(fulltext=fulltext)
    return generate_response(prompt)


def append(full, tmp):
    return f"{full}\n\n{tmp}"


def buildapp(initialtext, initialsummary):
    # https://www.gradio.app/guides/blocks-and-event-listeners#blocks-structure
    with gr.Blocks() as myapp:
        # https://www.gradio.app/guides/controlling-layout#rows
        with gr.Row():
            with gr.Column():
                suggestpprompt_box = gr.Textbox(
                    value=prompt_suggest, label="Suggestion prompt (use {fullsummary}, {instructions} placeholders)", lines=12
                )
                fullsummary_box = gr.Textbox(
                    value=initialsummary, label="Full Summary - {fullsummary}", lines=15
                )
                instructions_box = gr.Textbox(label="Instructions - {instructions}", lines=3)
            with gr.Column():
                summaryprompt_box = gr.Textbox(
                    value=prompt_summarize, label="Summary prompt (use {fulltext} placeholder)", lines=5
                )
                fulltext_box = gr.Textbox(value=initialtext, label="Full Text - {fulltext}", lines=30)
        with gr.Row():
            with gr.Column():
                suggest_btn = gr.Button("Suggest")
                tmptext_box = gr.Textbox(label="Temp text", lines=5)
                appendtext_btn = gr.Button("Accept text")
            with gr.Column():
                summarize_btn = gr.Button("Summarize")
                tmpsummary_box = gr.Textbox(label="Temp summary", lines=5)
                appendsummary_btn = gr.Button("Accept summary")
        with gr.Row():
            save_btn = gr.Button("Save")
        with gr.Row():
            status_box = gr.Markdown(label="Status")

        # match button - function
        suggest_btn.click(
            fn=suggest,
            inputs=[suggestpprompt_box, fullsummary_box, instructions_box],
            outputs=tmptext_box,
            api_name="suggest",
        )
        summarize_btn.click(
            fn=summarize,
            inputs=[summaryprompt_box, fulltext_box],
            outputs=tmpsummary_box,
            api_name="summarize",
        )
        appendtext_btn.click(
            fn=append,
            inputs=[fulltext_box, tmptext_box],
            outputs=[fulltext_box],
            api_name="appendtxt",
        )
        appendsummary_btn.click(
            fn=append,
            inputs=[fullsummary_box, tmpsummary_box],
            outputs=[fullsummary_box],
            api_name="appendsummary",
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
    buildapp(initialtext, initialsummary).launch()
