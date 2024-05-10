from datetime import datetime

inputdir = "inputs"
outputdir = "outputs"
textfile = "text.txt"
summaryfile = "summary.txt"

def read(filename):
    f = open(filename, "r")
    lines = f.readlines()
    return "\n".join(lines)


def write(filename, s):
    f = open(filename, "w")
    f.write(s)
    f.close()


def load():
    initialtext = read(inputdir + "/" + textfile)
    initialsummary = read(inputdir + "/" + summaryfile)
    return initialtext, initialsummary


def save(fulltext, fullsummary):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    write(f"{outputdir}/{timestamp}-{textfile}", fulltext)
    write(f"{outputdir}/{timestamp}-{summaryfile}", fullsummary)
    return f"Saved to {outputdir}"
