import os
from datetime import datetime

default_inputdir = "inputs"
default_outputdir = "outputs"
default_textfile = "text.txt"
# summaryfile = "summary.txt"

def load(filename=None):
    if filename is None:
        filename = default_inputdir + "/" + default_textfile
    try:
        f = open(filename, "r")
        lines = f.readlines()
        return "\n".join(lines)
    except FileNotFoundError:
        return ""


def save(fulltext, filename=None, add_timestamp=True):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if filename is None:
        filename=f"{default_outputdir}/{timestamp}-{default_textfile}"
    elif add_timestamp:
        f_name, f_ext = os.path.splitext(filename)
        filename = f'{f_name}-{timestamp}{f_ext}'
    with open(filename, "w") as f:
        f.write(fulltext)
        f.close()
    return f"Saved to {filename}"
