from flask import Flask, render_template, request
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)

@app.route('/')
def index1():
    return render_template('index1.html')
@app.route('/index' ,methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/choi',methods=['GET'])
def choi():
    return render_template('choi.html')


@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Vérifie si un fichier audio a été soumis
    if 'audio_file' not in request.files:
        return "Aucun fichier audio n'a été sélectionné."

    audio_file = request.files['audio_file']
    
    # Enregistre le fichier audio temporairement
    audio_path = 'temp.wav'
    audio_file.save(audio_path)

    # Convertit le fichier audio en format WAV
    wav_path = 'temp_converted.wav'
    convert_audio_to_wav(audio_path, wav_path)

    # Transcrit le fichier audio en texte
    text = convert_audio_to_text(wav_path)

    # Supprime les fichiers audio temporaires
    os.remove(audio_path)
    os.remove(wav_path)

    # Affiche le texte transcrit sur la page de résultat
    return render_template('result.html', transcribed_text=text)

def convert_audio_to_wav(audio_path, output_path):
    audio = AudioSegment.from_file(audio_path)
    audio.export(output_path, format='wav')

def convert_audio_to_text(audio_path):
    r = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="fr-FR")
            return text
        except sr.UnknownValueError:
            return "Impossible de transcrire l'audio."
        except sr.RequestError as e:
            return "Erreur lors de la requête : {0}".format(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
