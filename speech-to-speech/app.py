from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
from gtts import gTTS
import os
import time


app = Flask(__name__)

# Convert audio file to WAV format
def convert_audio(audio_path):
    try:
        sound = AudioSegment.from_file(audio_path)
        converted_path = "converted.wav"
        sound.export(converted_path, format="wav")
        return converted_path
    except Exception as e:
        print("Error converting audio:", e)
        return None

# Speech to Text
def speech_to_text(audio_path, lang="en"):
    recognizer = sr.Recognizer()
    converted_audio_path = convert_audio(audio_path)

    if not converted_audio_path:
        return "Error: Audio conversion failed."

    with sr.AudioFile(converted_audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language=lang)
        return text
    except sr.UnknownValueError:
        return "Error: Could not understand audio."
    except sr.RequestError as e:
        return f"Error: Could not request results from Google Speech Recognition service; {e}"

# Translate Text
def translate_text(text, target_lang):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_lang).text
    return translated_text

# Text to Speech
from gtts.lang import tts_langs  # Import the list of supported languages

def text_to_speech(text, lang):
    if lang not in tts_langs():
        return "Error: Language not supported for text-to-speech."

    timestamp = int(time.time())  
    output_path = f"static/output_{timestamp}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    audio_path = "input_audio." + audio_file.filename.split('.')[-1]
    audio_file.save(audio_path)

    lang_from = request.form.get('lang_from', 'en')
    lang_to = request.form.get('lang_to', 'fr')

    text = speech_to_text(audio_path, lang_from)

    if "Error" in text:
        return jsonify({"error": text})

    translated_text = translate_text(text, lang_to)
    speech_file = text_to_speech(translated_text, lang_to)

    return jsonify({
        "original_text": text,
        "translated_text": translated_text,
        "audio_url": speech_file
    })

@app.route('/retranslate', methods=['POST'])
def retranslate():
    data = request.json
    text = data.get("text")
    target_lang = data.get("lang_to")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Translate the text
    translated_text = translate_text(text, target_lang)

    # Generate a new speech file (IMPORTANT FIX)
    speech_file = text_to_speech(translated_text, target_lang)

    return jsonify({
        "translated_text": translated_text,
        "audio_url": f"/{speech_file}"  # Ensure correct URL path
    })



if __name__ == '__main__':
    app.run(debug=True)
