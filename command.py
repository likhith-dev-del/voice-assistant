from flask import Flask, send_file, make_response, request, jsonify
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY", "sk_679d8ab54982cae48cf63f1e9ccaba82fd36992be928e7e6")
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
MODEL_ID = "eleven_multilingual_v2"

# Home greetings
HOME_GREETINGS = {
    "EN": "Welcome!",
    "HI": "स्वागत है!",
    "TA": "வணக்கம்!",
    "TE": "స్వాగతం!",
    "KN": "ಸ್ವಾಗತ!",
    "BN": "স্বাগতম!",
    "ML": "സ്വാഗതം!"
}

# Bot (talk_with_bot.html) greetings
BOT_GREETINGS = {
    "EN": "Hello! How can I assist you today?",
    "HI": "नमस्ते! मैं आपकी किस प्रकार सहायता कर सकती हूँ?",
    "TA": "வணக்கம்! இன்று நான் எப்படி உதவலாம்?",
    "TE": "హలో! నేను మీకు ఈ రోజు ఎలా సహాయం చేయగలను?",
    "KN": "ಹಲೋ! ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    "BN": "হ্যালো! আজ আমি কীভাবে সাহায্য করতে পারি?",
    "ML": "ഹലോ! ഇന്ന് ഞാൻ എങ്ങനെ സഹായിക്കാമെന്ന് പറയൂ?"
}

def generate_greeting_audio(lang_code, greeting_type):
    if greeting_type == "home":
        text = HOME_GREETINGS.get(lang_code.upper(), HOME_GREETINGS["EN"])
        filename = f"home_{lang_code}.mp3"
    else:
        text = BOT_GREETINGS.get(lang_code.upper(), BOT_GREETINGS["EN"])
        filename = f"bot_{lang_code}.mp3"
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        output_format="mp3_44100_128"
    )
    save(audio, filename)
    return filename

@app.route("/welcome-audio")
def welcome_audio():
    lang_code = request.args.get("lang", "EN").upper()
    greeting_type = request.args.get("type", "bot").lower()  # default to "bot"
    if greeting_type == "home":
        audio_path = f"home_{lang_code}.mp3"
    else:
        audio_path = f"bot_{lang_code}.mp3"
    try:
        if not os.path.exists(audio_path):
            generate_greeting_audio(lang_code, greeting_type)
        response = make_response(send_file(audio_path, mimetype="audio/mp3"))
        response.headers["Cache-Control"] = "no-cache"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
