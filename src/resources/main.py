import os
import socket
from multiprocessing import Process
from HandGesture import *
from SpeechToText import *
import time

# os call to start the voice recognition script
def startVoice():
    os.system("python3 SpeechToText.py")

#os call to start the gesture recognition script
def startGesture():
    os.system("python3 HandGesture.py")


if __name__ == '__main__':
    '''
    The two calls below start the two processes asynchronosly. 
    There is a brief waiting period to start the gesture script
    in order to start the server socket within startVoice().
    '''
    p = Process(target=startVoice, args = ()).start()
    time.sleep(4)
    q = Process(target=startGesture, args = ()).start()
