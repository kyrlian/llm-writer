#!python3

# https://textual.textualize.io/widgets/input/

import sys
from time import sleep
from functools import partial
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, Static
from textual.command import Hit, Hits, DiscoveryHit, Provider
from engine_ollama import Engine as ollamaEngine
from prompts import prompts
from fileio import load, save
from parse_generate import (
    parse_and_generate,
    parse_and_generate_stream,
    STATUS_NOTHING,
)
from experiments.gen import mygen

# Use custom commands to switch model (instead of 'next model')
# https://textual.textualize.io/guide/command_palette/
class SelectModelCommands(Provider):
    """A command provider to select a model."""
    def simple_highlight(self, txt:str, match: str) -> Text:
        rich_text = Text(txt)
        offset = txt.find(match)
        if offset >= 0 and len(match)>0:
            match_style = self.matcher(match).match_style  
            rich_text.stylize(match_style, offset, offset + len(match))
        return rich_text
    
    async def search(self, query: str) -> Hits:  
        """Search for Models."""
        app = self.app
        for model in app.models:
            if query in model:
                yield Hit(
                    1,
                    self.simple_highlight(f"Select {model}", query),
                    partial(app.set_model, model),
                )

    async def discover(self) ->  Hits:
        """Display Models"""
        for model in app.models:
            yield DiscoveryHit(f"Select {model}", partial(app.set_model, model))


class WriterApp(App):

    BINDINGS = [("ctrl+s","save","Save"), ("ctrl+m","next_model","next Model"),("ctrl+q", "quit", "Quit")]
    COMMANDS =  {SelectModelCommands}  | App.COMMANDS
    # CSS_PATH = "textual.tcss"

    def __init__(self, *args, input_file=None, **kwargs):
        self.engine = ollamaEngine()
        self.input_file = input_file
        self.models = self.engine.list()
        self.model_idx = 0
        self.status_msg = "Initializing..."
        lang = list(prompts.keys())[0]
        self.prompt_suggest = prompts[lang]["prompt_suggest"]
        self.prompt_summarize = prompts[lang]["prompt_summarize"]
        self.updating=False
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextArea(id="txt_input", text= load(self.input_file ), tab_behavior='indent')
        yield Static(self.status_msg, id="status_log")
        yield Footer()

    def on_ready(self) -> None:
        self.set_model ( self.models[self.model_idx])

    def on_text_area_changed(self, message: TextArea.Changed):
        if message.text_area.id == "txt_input" and not self.updating: #as I update the text area direcly, I need avoid updating  on my own updates
            if message.text_area.text[-1] == "\n":  # if just typed enter
                self.updating = True
                self.set_status("Processing...", save_status=False)
                fulltext = message.text_area.text.strip()
                # Old - no stream
                # generated, status = parse_and_generate(
                #     self.engine,
                #     fulltext,
                #     self.model,
                #     self.prompt_suggest,
                #     self.prompt_summarize,
                #     include_input=False,
                # )
                # if status is not STATUS_NOTHING:
                #     self.set_status(f"{status} : {generated}")
                #     message.text_area.insert(generated)
                # else:
                #     self.set_status()
                ## STREAM
                # full_generated = message.text_area.text
                gen_stream = parse_and_generate_stream(
                    self.engine,
                    fulltext,
                    self.model,
                    self.prompt_suggest,
                    self.prompt_summarize,
                    include_input=False,
                )
                for generated, status in gen_stream:
                    if status is not STATUS_NOTHING:
                        self.set_status(f"{status} : {generated}")
                        if generated is not None and len(generated)>0:
                            message.text_area.insert(generated) # this does not update until the end, useless in streaming :(
                            # full_generated += generated
                            # message.text_area.text = full_generated
                            # message.text_area.insert("-")
                            # message.text_area.render()
                            # message.text_area.refresh()
                            # message.text_area.recompose()
                            # message.text_area.app.render()
                            # message.text_area.app.refresh()
                            # message.text_area.app.recompose()

                    else:
                        self.set_status()
                # message.text_area.replace("")# To move the cursor at the end of the text
                self.updating = False


    def set_model(self,model):
        self.model = model
        self.set_status(f"Model: {self.model}")

    def action_next_model(self):
        self.model_idx = (self.model_idx + 1) % len(self.models)
        self.set_model ( self.models[self.model_idx])

    def action_save(self):
        self.set_status("Saving...")
        txt = self.query_one("#txt_input", TextArea).text
        save(txt)

    def set_status(self, msg=None, save_status=True):
        if msg is None:
            msg = self.status_msg
        elif save_status:
           self.status_msg = msg
        self.query_one("#status_log", Static).update(msg)# .write_line(msg)


if __name__ == "__main__":
    args = sys.argv[1:]
    input_file = None if len(args) == 0 else args[0]
    app = WriterApp(input_file)
    app.run()
