
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
    write(outputdir + "/" + textfile, fulltext)
    write(outputdir + "/" + summaryfile, fullsummary)
