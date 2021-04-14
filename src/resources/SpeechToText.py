from __future__ import division
import re
import sys
import pyautogui
import pynput
from pynput.mouse import Button, Controller

from google.cloud import speech

import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

"""
API key to run script:
export GOOGLE_APPLICATION_CREDENTIALS="api_key.json"
"""


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


class Main(object):
    
    def main(self):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code = "en-US"  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            self.listen_loop(responses)
    def listen_loop_keyboard(self, responses):
        mouse = Controller()
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                pass
                # sys.stdout.write(transcript + overwrite_chars + "\r")
                # sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                keyboard = pynput.keyboard.Controller()
                if re.search(r"\b(stop keyboard)\b", transcript, re.I):
                    print("Stop Keyboard..")
                    keyboard.type(transcript.replace("stop keyboard", ""))
                    return
                else:
                    keyboard.type(transcript)
                
         
    def listen_loop(self, responses):
        mouse = Controller()
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                # sys.stdout.write(transcript + overwrite_chars + "\r")
                # sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                #Final Transcription here
                print(transcript + overwrite_chars)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r"\b(right press|rite press)\b", transcript, re.I):
                    print("Right Clicking..")
                    mouse.click(Button.right, 1)
                    continue

                if re.search(r"\b(double-press|double press)\b", transcript, re.I):
                    print("Double Clicking..")
                    mouse.click(Button.left, 2)
                    continue

                if re.search(r"\b(press)\b", transcript, re.I):
                    print("Clicking..")
                    mouse.click(Button.left, 1)
                    continue
                

                if re.search(r"\b(scroll up)\b", transcript, re.I):
                    print("Scrolling up..")
                    mouse.scroll(0, 15)

                if re.search(r"\b(scroll down)\b", transcript, re.I):
                    print("Scrolling down..")
                    mouse.scroll(0, -15)

                if re.search(r"\b(start keyboard)\b", transcript, re.I):
                    print("Typing..")
                    self.listen_loop_keyboard(responses)

                if re.search(r"\b(exit|quit)\b", transcript, re.I):
                    print("Exiting..")
                    break

                num_chars_printed = 0

if __name__ == "__main__":
    m = Main()
    m.main()

