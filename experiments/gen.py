from time import sleep

def mygen(n:int):
    yield ".", "starting"
    for i in range(n):
        yield str(i), "generating"
    yield ".", "done"

if __name__ == "__main__":
    for i,s in mygen(5):
        print(s)
        print(i)        
        sleep(1)