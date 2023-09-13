from flask import Flask, render_template, request
from google.cloud import speech
import pyaudio
from six.moves import queue
import os
import csv
import sys
import re
import itertools
from datetime import datetime

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "traffic-day-86c0cf212577.json"

app = Flask(__name__)

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    # Reste du code...


    @app.route('/')
    def index():
        return render_template('info.html')


    @app.route('/save', methods=['POST'])
    def save_transcription():
        transcript = request.form['transcript']
        now = datetime.now()
        id_value = now.strftime("%Y%m%d%H%M%S")

        # Ajoutez ici la logique pour enregistrer le texte transcrit dans un fichier CSV avec un ID

        # Exemple d'enregistrement dans un fichier CSV nommé "transcriptions.csv"
        with open('transcriptions.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([id_value, transcript])

        return 'Transcription enregistrée.'


    @app.route('/transcribe', methods=['POST'])
    def transcribe():
        language_code = "fr-FR"

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
            id_counter = itertools.count(start=1)
            csv_filename = "base.csv"
            file_mode = "a" if os.path.exists(csv_filename) else "w"

            with open(csv_filename, file_mode, newline="", encoding='utf-8') as f:
                writer = csv.writer(f)

                if file_mode == "w":
                    writer.writerow(["ID", "Transcript"])

                audio_generator = stream.generator()
                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )

                responses = client.streaming_recognize(streaming_config, requests)

                listen_print_loop(responses, writer, id_counter)

        return 'Transcription completed.'


    def listen_print_loop(responses, writer, id_counter):
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
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)

                if re.search(r"\b(exit|quit)\b", transcript, re.I):
                    print("Exiting..")

                num_chars_printed = 0
                id_value = next(id_counter)
                writer.writerow([id_value, transcript])


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
