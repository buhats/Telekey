import speech_recognition as sr

#filename must be .wav or .flac
def speechToText(filename):
    rec = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = rec.record(source)
        text = rec.recognize_google(audio_data)
        print(text)


