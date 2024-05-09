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
                suggestpprompt = gr.Textbox(value=prompt_suggest, label="Suggestion prompt", lines=12)
                fullsummary = gr.Textbox(value=initialsummary, label="Full Summary", lines=15)
                instructions = gr.Textbox(label="Instructions", lines=3)
            with gr.Column():
                summaryprompt = gr.Textbox(value=prompt_summarize, label="Summary prompt", lines=5)
                fulltext = gr.Textbox(value=initialtext, label="Full Text", lines=30)
        with gr.Row():
            with gr.Column():
                suggest_btn = gr.Button("Suggest")
                tmptext = gr.Textbox(label="Tmp text", lines=5)
                appendtext_btn = gr.Button("Accept text")
            with gr.Column():
                summarize_btn = gr.Button("Summarize")
                tmpsummary = gr.Textbox(label="Tmp summary", lines=5)
                appendsummary_btn = gr.Button("Accept summary")
        with gr.Row():
            save_btn = gr.Button("Save")

        # match button - function
        suggest_btn.click(
            fn=suggest,
            inputs=[suggestpprompt, fullsummary, instructions],
            outputs=tmptext,
            api_name="suggest",
        )
        summarize_btn.click(
            fn=summarize, inputs=[summaryprompt, fulltext], outputs=tmpsummary, api_name="summarize"
        )
        appendtext_btn.click(
            fn=append,
            inputs=[fulltext, tmptext],
            outputs=[fulltext],
            api_name="appendtxt",
        )
        appendsummary_btn.click(
            fn=append,
            inputs=[fullsummary, tmpsummary],
            outputs=[fullsummary],
            api_name="appendsummary",
        )
        save_btn.click(
            fn=save,
            inputs=[fulltext, fullsummary],
            api_name="save",
        )
    return myapp


if __name__ == "__main__":
    initialtext, initialsummary = load()
    buildapp(initialtext, initialsummary).launch()
