import gradio as gr

from ollama import generate_response
from prompts import prompt_summarize, prompt_suggest


def suggest(fullsummary, instructions):
    return generate_response(
        f"{prompt_suggest}\n\nSTORY SO FAR\n\n{fullsummary}\n\nINSTRUCTIONS\n\n{instructions}\n\n"
    )

def summarize(fulltext):
    return generate_response(f"{prompt_summarize}\n\n{fulltext}")

def append(fulltext, tmptext, fullsummary, tmpsummary):
    return f"{fulltext}\n\n{tmptext}", f"{fullsummary}\n\n{tmpsummary}"


def read(file):
    f = open(file, "r")
    lines = f.readlines()
    return lines


initialtext = read("inputs-outputs/text.txt")
initialsymmary = read("inputs-outputs/summary.txt")

# https://www.gradio.app/guides/blocks-and-event-listeners#blocks-structure
with gr.Blocks() as myapp:
    # https://www.gradio.app/guides/controlling-layout#rows
    # text fields
    fulltext = gr.Textbox(value=initialtext, label="Full Text")
    instructions = gr.Textbox(label="instructions")
    tmptext = gr.Textbox(label="tmptext")
    fullsummary = gr.Textbox(value=initialsymmary, label="fullsummary")
    tmpsummary = gr.Textbox(label="tmpsummary")
    # buttons
    suggest_btn = gr.Button("Suggest")
    summarize_btn = gr.Button("Summarize")
    append_btn = gr.Button("Accept")
    # function
    suggest_btn.click(
        fn=suggest,
        inputs=[fullsummary, instructions],
        outputs=tmptext,
        api_name="suggest",
    )
    summarize_btn.click(
        fn=summarize, inputs=fulltext, outputs=tmpsummary, api_name="summarize"
    )
    append_btn.click(
        fn=append,
        inputs=[tmptext, tmpsummary],
        outputs=[fulltext, fullsummary],
        api_name="append",
    )


if __name__ == "__main__":
    myapp.launch()
