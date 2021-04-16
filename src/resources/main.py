import os
import socket
from multiprocessing import Process
from HandGesture import *
from SpeechToText import *
import time
def startVoice():
    os.system("python3 SpeechToText.py")

def startGesture():
    os.system("python3 HandGesture.py")

if __name__ == '__main__':
    p = Process(target=startVoice, args = ()).start()
    time.sleep(4)
    q = Process(target=startGesture, args = ()).start()
