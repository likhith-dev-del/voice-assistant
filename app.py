from flask import Flask, request, jsonify, send_file, render_template
import requests
from google import genai
import os


app = Flask(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Homepage Route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chat_with_bot.html')
def chat():
    return render_template('chat_with_bot.html')

@app.route('/features.html')
def features():
    return render_template('features.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/history.html')
def history():
    return render_template('history.html')

@app.route('/image_search.html')
def image_search():
    return render_template('image_search.html')

@app.route('/language.html')
def language():
    return render_template('language.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/settings.html')
def settings():
    return render_template('settings.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/talk_with_bot.html')
def talk():
    return render_template('talk_with_bot.html')

@app.route('/tutorial.html')
def tutorial():
    return render_template('tutorial.html')

@app.route('/welcome-audio')
def welcome_audio():
    return "", 200

# Mapping languages to voice IDs
VOICE_MAP = {
    "english": "EXAVITQu4vr4xnSDxMaL",
    "hindi": "EXAVITQu4vr4xnSDxMaL",
    "telugu": "Yko7PKHZNXotIFUBG7I9",
    "tamil": "MF3mGyEYCl7XYWbV9V6O",
}

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    user_text = data.get("text")
    language = data.get("language", "english").lower()
    voice_id = VOICE_MAP.get(language, VOICE_MAP["english"])

    response_ai = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=user_text
)

    bot_reply = response_ai.text


    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
       },
        json={
            "text": bot_reply,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.75
            }
        }
    )

    if response.status_code == 200:
        with open("static/ria_output.mp3", "wb") as f:
            f.write(response.content)
        return jsonify({
            "response" : bot_reply,
            "audio": "/static/ria_output.mp3"})
    else:
        return jsonify({
            "error": "TTS generation failed",
            "details": response.text
        }), 500

if __name__ == "__main__":
    app.run(debug=True)