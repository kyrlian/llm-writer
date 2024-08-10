from textual.app import App, ComposeResult
from textual.widgets import TextArea, Header, Footer, Static
from time import sleep



class StreamApp(App):
    BINDINGS = [
        ("ctrl+s", "stream", "Stream"),
        ("ctrl+q", "quit", "Quit"),
    ]


    def __init__(self, *args, input_file=None, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextArea(id="txt_input", text="")
        yield Static("status", id="status_log")
        yield Footer()

    def mygen(self,n:int):
        yield "starting"
        for i in range(n):
            yield str(i)
            sleep(.5)
        yield "done"
        
    def action_stream(self):
        for i in self.mygen(3):
           ta = self.query_one("#txt_input", TextArea)
           ta.insert(i)

if __name__ == "__main__":
    app = StreamApp()
    app.run()
