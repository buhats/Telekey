import speech_recognition as sr

#filename must be .wav or .flac
def speechToText(filename):
    rec = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = rec.record(source)
        text = rec.recognize_google(audio_data)
        return text

def speechToTextCont():
    rec = sr.Recognizer()

    while(True):
        try:
            with sr.Microphone() as src:
                rec.adjust_for_ambient_noise(src, duration=.5)
                aud = rec.listen(src)

                text = rec.recognize_google(aud).lower()

                print(text)

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

        except sr.UnknownValueError:
            print("Unknown error occured /;")
