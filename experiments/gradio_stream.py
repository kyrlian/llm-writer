import gradio as gr
from time import sleep

def gen(v):
    for i in range(v):
        si = f"{i}"
        yield si,si
        sleep(1)

with gr.Blocks() as demo:
    fulltext_box = gr.Textbox(label="Text"    )
    status_box = gr.Markdown(label="Status")
    save_btn = gr.Button("generate").click(fn=gen, inputs=gr.Number(value=10), outputs=[fulltext_box,status_box])

demo.launch()
