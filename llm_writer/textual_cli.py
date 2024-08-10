#!python3
print("In module products __package__, __name__ ==", __package__, __name__)

# https://textual.textualize.io/widgets/input/

import sys
import asyncio
from functools import partial
from typing import Generator
from time import sleep
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, Static
from textual.command import Hit, Hits, DiscoveryHit, Provider
from engine_ollama import Engine as ollamaEngine
from prompts import prompts
from fileio import load, save
from parse_generate import (
    parse_and_generate_stream,
    STATUS_NOTHING,
)
from async_wrapper import async_wrapper

def simple_highlight(provider:Provider, txt: str, match: str) -> Text:
    rich_text = Text(txt)
    offset = txt.find(match)
    if offset >= 0 and len(match) > 0:
        match_style = provider.matcher(match).match_style
        rich_text.stylize(match_style, offset, offset + len(match))
    return rich_text

# Use custom commands to switch lang (complements 'next lang')
class SelectLangCommands(Provider):
    """A command provider to select a lang."""
    async def search(self, query: str) -> Hits:
        """Search for Langs."""
        app = self.app
        for lang in app.langs:
            if query in f"Select language {lang}":
                yield Hit(
                    1,
                    simple_highlight(self,f"Select language {lang}", query),
                    partial(app.set_lang, lang),
                )

    async def discover(self) -> Hits:
        """Display Models"""
        app = self.app
        for lang in app.langs:
            yield DiscoveryHit(f"Select language {lang}", partial(app.set_lang, lang))

# https://textual.textualize.io/guide/command_palette/
class SelectModelCommands(Provider):
    """A command provider to select a model."""
    async def search(self, query: str) -> Hits:
        """Search for Models."""
        app = self.app
        for model in app.models:
            if query in "Select model {model}":
                yield Hit(
                    1,
                    simple_highlight(self,f"Select model {model}", query),
                    partial(app.set_model, model),
                )

    async def discover(self) -> Hits:
        """Display Models"""
        app = self.app
        for model in app.models:
            yield DiscoveryHit(f"Select model {model}", partial(app.set_model, model))

# Use custom text area with hook on \n
# https://textual.textualize.io/widgets/text_area/#hooking-into-key-presses
class StreamedTextArea(TextArea):
    """A subclass of TextArea to call parse_and_generate_stream on, 'enter'."""
    async def stream_to_text_area(self, normal_generator:Generator):
        app = self.app
        app.set_status("Processing...", save_status=False)
        self.read_only = True
        async_gen_stream = async_wrapper(normal_generator)
        async for generated, status in async_gen_stream:
            if status is not STATUS_NOTHING:
                if generated is not None and len(generated) > 0:
                    self.insert(generated)
        self.read_only = False
        app.set_status()

    def _on_key(self, event: events.Key) -> None:
        # self.insert(f"event.key:{event.key}")
        if event.key == "enter":
            app = self.app
            fulltext = self.text.strip()
            self.insert("\n")
            ## STREAM
            gen_stream = parse_and_generate_stream(
                app.engine,
                fulltext,
                app.model,
                app.prompt_suggest,
                app.prompt_summarize,
                include_input=False,
                cumulative=False,
            )
            # Fire the task but don't wait for it to finish
            asyncio.create_task(self.stream_to_text_area(gen_stream))

class WriterApp(App):
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+m", "next_model", "next Model"),
        ("ctrl+l", "next_lang", "next Language"),
        ("ctrl+q", "quit", "Quit"),
    ]
    COMMANDS = {SelectModelCommands} | {SelectLangCommands} | App.COMMANDS
    # CSS_PATH = "textual.tcss"

    def __init__(self, *args, input_file=None, **kwargs):
        self.engine = ollamaEngine()
        self.input_file = input_file
        self.models = self.engine.list()
        self.model_idx = 0
        self.status_msg = "Initializing..."
        self.langs = list(prompts.keys())
        self.lang_idx = 0
        self.lang = self.langs[self.lang_idx]
        self.prompt_suggest = prompts[self.lang]["prompt_suggest"]
        self.prompt_summarize = prompts[self.lang]["prompt_summarize"]
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield StreamedTextArea(
            id="txt_input", text=load(self.input_file), tab_behavior="indent"
        )
        yield Static(self.status_msg, id="status_log")
        yield Footer()

    def on_ready(self) -> None:
        self.set_model(self.models[self.model_idx])

    def set_model(self, model):
        self.model = model
        self.set_status(f"Model: {self.model}, Language: {self.lang}")

    def set_lang(self, lang):
        self.lang = lang
        self.prompt_suggest = prompts[self.lang]["prompt_suggest"]
        self.prompt_summarize = prompts[self.lang]["prompt_summarize"]
        self.set_status(f"Model: {self.model}, Language: {self.lang}")

    def action_next_model(self):
        self.model_idx = (self.model_idx + 1) % len(self.models)
        self.set_model(self.models[self.model_idx])

    def action_next_lang(self):
        self.lang_idx = (self.lang_idx + 1) % len(self.langs)
        self.set_lang(self.langs[self.lang_idx])

    def action_save(self):
        self.set_status("Saving...")
        txt = self.query_one("#txt_input", TextArea).text
        save(txt)

    def set_status(self, msg=None, save_status=True):
        if msg is None:
            msg = self.status_msg
        elif save_status:
            self.status_msg = msg
        self.query_one("#status_log", Static).update(msg)  # .write_line(msg)


def main():
    args = sys.argv[1:]
    input_file = None if len(args) == 0 else args[0]
    app = WriterApp(input_file)
    app.run()

if __name__ == "__main__":
    main()