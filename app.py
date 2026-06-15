from flask import Flask, request, jsonify, send_file, send_from_directory, redirect
from flask_cors import CORS
import requests
import os
import sqlite3
import uuid
import datetime
import webbrowser

app = Flask(__name__, static_folder='static')
CORS(app)

API_KEY = os.environ.get("ELEVEN_API_KEY" )
DB_PATH = os.path.join(os.path.dirname(__file__), 'ria.db')

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") 
if not GEMINI_API_KEY:
    print("\n" + "="*80 + "\nERROR: Gemini API Key is missing! Please set the GEMINI_API_KEY environment variable.\n" + "="*80 + "\n")
else:
    print("\n" + "="*80 + "\nSUCCESS: Gemini API Key successfully loaded.\n" + "="*80 + "\n")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Mapping languages to ElevenLabs voice IDs
VOICE_MAP = {
    "english": "EXAVITQu4vr4xnSDxMaL",   # Rachel
    "hindi": "EXAVITQu4vr4xnSDxMaL",     # Rachel fallback
    "telugu": "Yko7PKHZNXotIFUBG7I9",    # Bella
    "tamil": "MF3mGyEYCl7XYWbV9V6O",     # Elli
    "kannada": "EXAVITQu4vr4xnSDxMaL",   # fallback
    "bengali": "EXAVITQu4vr4xnSDxMaL",   # fallback
    "malayalam": "EXAVITQu4vr4xnSDxMaL"  # fallback
}

# Greetings by language code
HOME_GREETINGS = {
    "EN": "Welcome!",
    "HI": "स्वागत है!",
    "TA": "வணக்கம்!",
    "TE": "స్వాగతం!",
    "KN": "ಸ್ವಾಗತ!",
    "BN": "স্বাগতম!",
    "ML": "സ്വാഗതം!"
}

BOT_GREETINGS = {
    "EN": "Hello! How can I assist you today?",
    "HI": "नमस्ते! मैं आपकी किस प्रकार सहायता कर सकती हूँ?",
    "TA": "வணக்கம்! இன்று நான் எப்படி உதவலாம்?",
    "TE": "హలో! నేను మీకు ఈ రోజు ఎలా సహాయం చేయగలను?",
    "KN": "ಹಲೋ! నేను ಇಂದು మీకు ఎలా సహాయం చేయగలను?",
    "BN": "হ্যালো! আজ আমি কীভাবে সাহায্য করতে পারি?",
    "ML": "ഹലോ! ഇന്ന് ഞാൻ എങ്ങനെ സഹായിക്കാമെന്ന് പറയൂ?"
}

def call_gemini(prompt):
    key = GEMINI_API_KEY
    if not key:
        return "Error: Gemini API key is missing. Please set the GEMINI_API_KEY environment variable."
    
    formatted_prompt = f"Answer the user's question concisely in a conversational style suitable for a voice assistant. Keep it short (1-3 sentences) and friendly. User query: {prompt}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": formatted_prompt}]
        }]
    }
    
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.5-flash", "gemini-flash-latest"]
    
    last_error = ""
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            response = requests.post(url, headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                res_data = response.json()
                try:
                    return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError):
                    last_error = f"Error parsing response from Gemini API for model {model}."
            else:
                last_error = f"Gemini API Error for model {model} (status {response.status_code}): {response.text}"
                print(last_error)
        except Exception as e:
            last_error = f"Exception calling Gemini for model {model}: {e}"
            print(last_error)
            
    return "I encountered an error calling the Gemini API. Please make sure the API key is configured correctly."

def get_assistant_response(query, language="english"):
    q = query.lower().strip()
    
    # Check for web commands
    if "open google" in q:
        webbrowser.open("https://www.google.com")
        return "Opening Google for you."
    elif "open youtube" in q:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif "open github" in q:
        webbrowser.open("https://github.com")
        return "Opening GitHub."
    elif "open settings" in q:
        return "Opening Settings menu."
    
    # Check for time/date queries
    elif "time" in q:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}."
    elif "date" in q:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today is {today}."
    
    # Check for typical hello/how are you
    elif "hello" in q or "hi" in q:
        return "Hello! I am RIA, your intelligent voice assistant. How can I help you today?"
    elif "how are you" in q:
        return "I am doing great, thank you! How can I assist you?"
    elif "your name" in q:
        return "My name is RIA, which stands for Realtime Intelligent Assistant."
        
    return call_gemini(query)

# --- Authentication Endpoints ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"success": True, "userId": user_id})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, email FROM users WHERE email = ? AND password = ?', (email, password))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({"success": True, "user": {"id": row[0], "email": row[1]}})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Static File and Page Routing ---
@app.route('/pages/<path:filename>')
def serve_pages(filename):
    return send_from_directory('pages', filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    return send_from_directory('scripts', filename)

@app.route('/')
def index():
    return redirect('/pages/login.html')

# --- Voice & AI Endpoints ---
@app.route("/test")
def test():
    return "APP FILE RUNNING"

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get("text")
    language = data.get("language", "english").lower()
    voice_id = VOICE_MAP.get(language, VOICE_MAP["english"])

    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.75
                }
            }
        )
        if response.status_code == 200:
            os.makedirs("static", exist_ok=True)
            filename = f"static/ria_output_{uuid.uuid4().hex[:8]}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            return jsonify({"audio": f"/static/{os.path.basename(filename)}"})
        else:
            return jsonify({"error": "TTS generation failed", "details": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/welcome-audio")
def welcome_audio():
    lang_code = request.args.get("lang", "EN").upper()
    greeting_type = request.args.get("type", "bot").lower()
    
    if greeting_type == "home":
        text = HOME_GREETINGS.get(lang_code, HOME_GREETINGS["EN"])
        filename = f"static/home_{lang_code}.mp3"
    else:
        text = BOT_GREETINGS.get(lang_code, BOT_GREETINGS["EN"])
        filename = f"static/bot_{lang_code}.mp3"

    # Ensure static folder exists
    os.makedirs("static", exist_ok=True)

    if not os.path.exists(filename):
        # Map lang_code to VOICE_MAP language keys
        lang_key_map = {
            "EN": "english",
            "HI": "hindi",
            "TA": "tamil",
            "TE": "telugu",
            "KN": "kannada",
            "BN": "bengali",
            "ML": "malayalam"
        }
        lang_name = lang_key_map.get(lang_code, "english")
        voice_id = VOICE_MAP.get(lang_name, VOICE_MAP["english"])

        try:
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.4,
                        "similarity_boost": 0.75
                    }
                }
            )
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
            else:
                # If generation fails, fallback to simple welcoming audio or EN fallback file
                fallback_fn = "welcome_EN.mp3"
                if os.path.exists(fallback_fn):
                    return send_file(fallback_fn, mimetype="audio/mpeg")
                return jsonify({"error": "TTS failed", "details": response.text}), 500
        except Exception as e:
            fallback_fn = "welcome_EN.mp3"
            if os.path.exists(fallback_fn):
                return send_file(fallback_fn, mimetype="audio/mpeg")
            return jsonify({"error": str(e)}), 500

    return send_file(filename, mimetype="audio/mpeg")

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    text = data.get("text", "")
    language = data.get("language", "english").lower()
    
    # Process the query using our command processor
    response_text = get_assistant_response(text, language)
    
    # Synthesize speech for response
    voice_id = VOICE_MAP.get(language, VOICE_MAP["english"])
    audio_url = None
    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": response_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.75
                }
            }
        )
        if response.status_code == 200:
            os.makedirs("static", exist_ok=True)
            filename = f"static/response_{uuid.uuid4().hex[:8]}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            audio_url = f"/static/{os.path.basename(filename)}"
    except Exception as e:
        print(f"TTS Error: {e}")
        
    return jsonify({
        "response": response_text,
        "audio": audio_url
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)
