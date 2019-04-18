import os, sys
global L
L = list()

def main():
    global L
    pid = os.fork()
    if pid == 0:
        L.append('apatata')
    else:
        L.append('je suis ton pere')
    showme()

def showme():
    global L
    print(L)
import time
time.sleep(5)
print('la vraie liste',L)

if __name__ == "__main__" :
    main()
