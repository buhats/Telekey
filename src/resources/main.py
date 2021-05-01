import os
import socket
from multiprocessing import Process
from HandGesture import *
from SpeechToText import *
from Application import *
import time

# os call to start the voice recognition script
def startApp():
    os.system("python3 Application.py")
    # a = ApplicationMain()
    # a.runMain()


def startVoice():
    os.system("python3 SpeechToText.py")
    # s = SpeechMain()
    # s.runMain()

#os call to start the gesture recognition script
def startGesture():
    os.system("python3 HandGesture.py")
    # g = GestureMain()
    # g.runMain()

if __name__ == '__main__':
    '''
    The two calls below start the two processes asynchronosly. 
    There is a brief waiting period to start the gesture script
    in order to start the server socket within startVoice().
    '''
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "tkey_api.json"
    a = Process(target=startApp, args=()).start()
    p = Process(target=startVoice, args = ()).start()
    q = Process(target=startGesture, args = ()).start()
