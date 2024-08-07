#!python3

# https://textual.textualize.io/widgets/input/

import sys
from textual.app import App, ComposeResult
from textual.widgets import Log, TextArea, Button, OptionList

from engine_ollama import Engine as ollamaEngine
from prompts import prompts
from fileio import load, save
from parse_generate import (
    parse_and_generate,
    SUMMARY_TAG,
    INSTRUCTION_TAG,
    STATUS_NOTHING,
)

# Init LLM
initialtext = load()
ollama_engine = ollamaEngine()
models_list = ollama_engine.list()
lang = list(prompts.keys())[0]
prompt_suggest = prompts[lang]["prompt_suggest"]
prompt_summarize = prompts[lang]["prompt_summarize"]


class InputApp(App):
    def __init__(self, *args, engine, prompt, **kwargs):
        self.engine = engine
        self.prompt = prompt
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield TextArea(id="txt_input", text=self.prompt)
        yield OptionList(*models_list, id="drop_models")
        yield Button(id="btn_save", label="Save")
        yield Log(id="debug")

    def on_ready(self) -> None:
        self.debug("Ready!")

    def on_text_area_changed(self, message: TextArea.Changed):
        if message.text_area.id == "txt_input":
            tat = message.text_area.text
            if tat[-1] == "\n":  # if just typed enter
                fulltext = tat.strip()
                self.debug(f"fulltext: {fulltext}")
                generated, status = parse_and_generate(
                    self.engine,
                    fulltext,
                    "llama3:latest",
                    prompt_suggest,
                    prompt_summarize,
                    include_input=False,
                )
                self.debug(f"status: {status}")
                if status is not STATUS_NOTHING:
                    self.debug(f"generated: {generated}")
                    message.text_area.insert(generated)

    def debug(self, msg):
        self.query_one("#debug", Log).write_line(f"DEBUG:{msg}")


if __name__ == "__main__":
    args = sys.argv[1:]
    ollama_engine = ollamaEngine()
    app = InputApp(engine=ollama_engine, prompt=initialtext)
    app.run()
