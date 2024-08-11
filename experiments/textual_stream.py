
from time import sleep
import asyncio
from typing import AsyncGenerator, Generator
from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, Static
from textual import events

def demo_generator(n: int)-> Generator:
    """ Sample normal generator """
    yield "starting"
    for i in range(n):
        yield str(i)
        sleep(0.5)
    yield "done"


# async def async_wrapper_old(normal_generator:Generator)-> AsyncGenerator:
#     """ Convert a normal generator to an async generator """
#     async def getnext(normal_generator):
#         try:
#             v = next(normal_generator)
#             return v,True
#         except StopIteration as e:
#             return None, False
        
#     doloop = True
#     while doloop:
#         val, doloop = await asyncio.create_task(getnext(normal_generator))
#         if doloop:
#             yield val
        
async def async_wrapper(normal_generator:Generator)-> AsyncGenerator:
    async def g(a):
        return a

    for v in normal_generator:
        yield await asyncio.create_task(g(v))

class StreamedTextArea(TextArea):
    """A subclass of TextArea to call parse_and_generate_stream on, 'enter'."""
    # WORKS
    async def stream_to_text_area(self, normal_generator:Generator):
        self.read_only = True
        async_gen_stream = async_wrapper(normal_generator)
        async for i in async_gen_stream:
            self.insert(i)
        self.read_only = False

    def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            # Fire the task but don't wait for it to finish
            asyncio.create_task(self.stream_to_text_area(demo_generator(10)))

class StreamApp(App):
    BINDINGS = [
        ("ctrl+s", "stream", "Stream"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield StreamedTextArea(id="txt_input", text="")
        yield Static("status", id="status_log")
        yield Footer()

    async def action_stream(self):
        # WORKS
        ta = self.query_one("#txt_input", StreamedTextArea)
        async_gen_stream = async_wrapper(demo_generator(10))
        async for i in async_gen_stream:
            ta.insert(i)      

if __name__ == "__main__":
    app = StreamApp()
    app.run()
