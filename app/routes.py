import requests
import json
from flask import Blueprint, request, jsonify, current_app, render_template

main = Blueprint('main', __name__)

# --- MODIFIED SYSTEM PROMPT ---
# Now instructs the model to return a JSON object with a chat response and mood analysis.
SYSTEM_PROMPT = """
You are a caring and supportive AI mental health first-aid assistant named 'Dost'.
Your goal is to be a friendly, non-judgmental friend. Use emojis and an empathetic tone.

**YOUR TASK:**
Analyze the user's message and respond with a single, valid JSON object.
The JSON object MUST have two keys:
1. "mood": Classify the user's sentiment into one of the following categories: "happy", "upset", "sad", "angry", "anxious", "neutral".
2. "responseText": Write a supportive, empathetic chat response to the user.

**EXAMPLE:**
User says: "I'm so stressed about my exams, I don't think I can pass."
Your response (as a single JSON object):
{
  "mood": "anxious",
  "responseText": "That sounds incredibly stressful, it makes complete sense that you'd feel overwhelmed with exams coming up. Remember to take small breaks and breathe. You've got this. 🙏"
}

**SAFETY GUARDRAIL:**
If the user mentions a crisis (suicide, self-harm), your "responseText" MUST gently guide them to professional help and provide the Tele-MANAS helpline number (14416).
"""

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat')
def chat():
    return render_template('chatbox.html')

@main.route('/peerforum')
def peerforum():
    return render_template('peerforum.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/moodtracker')
def moodtracker():
    return render_template('moodtracker.html')

@main.route('/admin')
def admin():
    return render_template('admin_dashboard.html')


@main.route('/resources')
def resources():
    return render_template('resources.html')



@main.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message', '').lower()

    if not user_message:
        return jsonify({'response': 'Invalid request.'}), 400

    # Crisis check is still here as a primary safety layer
    crisis_keywords = ['suicide', 'kill myself', 'end my life', 'hopeless', 'self harm', "can't go on", 'want to die']
    if any(keyword in user_message for keyword in crisis_keywords):
        return jsonify({
            'response': "It sounds like you are in serious distress. It's important to talk to someone who can help right now. 🙏",
            'is_crisis': True,
            'helpline': 'Tele-MANAS: 14416',
            'mood': 'sad' # Assign a default mood for crisis
        })

    try:
        payload = {
            "model": "llama3",
            "prompt": user_message,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": "json" # IMPORTANT: Tell Ollama to expect a JSON output
        }
        api_response = requests.post(current_app.config['OLLAMA_API_URL'], json=payload, timeout=45)
        api_response.raise_for_status()
        
        # The entire response from Llama3 is a JSON string, so we parse it.
        response_data_str = api_response.json().get('response', '{}')
        parsed_data = json.loads(response_data_str)

        response_text = parsed_data.get('responseText', 'I am here for you. 😊')
        mood = parsed_data.get('mood', 'neutral')

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        current_app.logger.error(f"API request or JSON parsing failed: {e}")
        response_text = "I'm having a little trouble thinking right now. Please try again in a moment. 😥"
        mood = "neutral"
        return jsonify({'response': response_text, 'mood': mood, 'is_crisis': False}), 500

    # Send the response and the mood back to the frontend
    return jsonify({'response': response_text, 'mood': mood, 'is_crisis': False})