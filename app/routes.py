import requests
import json
import csv
import io
import google.generativeai as genai
from flask import Blueprint, request, jsonify, current_app, render_template, Response
from .extensions import socketio, db
from .models import ResearchLog, Therapist, Product

main = Blueprint('main', __name__)

# --- SYSTEM PROMPT (Unchanged) ---
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

# --- seed_data (Unchanged) ---
def seed_data():
    """Seeds the database with sample data if it's empty."""
    try:
        if Therapist.query.first() is None and Product.query.first() is None:
            print("Seeding database with sample marketplace data...")
            
            # Sample Therapists
            t1 = Therapist(
                name="Dr. Priya Sharma",
                specialty="Cognitive Behavioral Therapy (CBT), Student Anxiety",
                description="Helping students manage academic pressure and anxiety for over 10 years. Specializes in practical coping strategies.",
                price=1500,
                image_url="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&ixlib=rb-4.0.3&q=80&w=600"
            )
            t2 = Therapist(
                name="Mr. Arjun Gupta",
                specialty="Career Counseling, Stress Management",
                description="Former student counselor at a top university. Helps with career confusion, burnout, and finding a healthy work-life balance.",
                price=1200,
                image_url="https://images.unsplash.com/photo-1593186237573-cabe46175932?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&ixlib=rb-4.0.3&q=80&w=600"
            )
            
            # Sample Products
            p1 = Product(
                name="Mindfulness & Meditation Course",
                description="A 10-part video course designed for busy students. Learn to de-stress in 10 minutes a day. Lifetime access.",
                price=499,
                image_url="https://images.unsplash.com/photo-1506126613408-eca07ce6877e?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&ixlib=rb-4.0.3&q=80&w=600"
            )
            p2 = Product(
                name="Digital Exam Planner Pro",
                description="An interactive digital planner to organize your study schedule, track revision, and manage deadlines effectively. Reduces overwhelm.",
                price=250,
                image_url="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&ixlib=rb-4.0.3&q=80&w=600"
            )
            
            db.session.add_all([t1, t2, p1, p2])
            db.session.commit()
            print("Database seeded successfully.")
    except Exception as e:
        current_app.logger.error(f"Error seeding database: {e}")
        db.session.rollback()


# --- Routes ---
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat')
def chat():
    return render_template('chatbox.html')

@main.route('/peerforum')
def peerforum():
    return render_template('peerforum.html')

# --- NEW: Added route for virtual_lounge.html ---
@main.route('/virtual-lounge')
def virtual_lounge():
    return render_template('virtual_lounge.html')
# --- END NEW ---

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

@main.route('/marketplace')
def marketplace():
    try:
        therapists = Therapist.query.all()
        products = Product.query.all()
    except Exception as e:
        current_app.logger.error(f"Error querying marketplace: {e}")
        therapists = []
        products = []
        
    return render_template(
        'marketplace.html', 
        therapists=therapists, 
        products=products
    )

@main.route('/admin/export-data')
def export_data():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['timestamp', 'mood', 'user_message', 'bot_response'])
    try:
        logs = ResearchLog.query.order_by(ResearchLog.timestamp.asc()).all()
        for log in logs:
            writer.writerow([log.timestamp, log.mood, log.user_message, log.bot_response])
    except Exception as e:
        current_app.logger.error(f"Error querying research logs: {e}")
        writer.writerow(["Error exporting data.", str(e)])
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=research_data.csv"}
    )


@main.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message', '').lower()
    location = data.get('location', None)
    consent_given = data.get('consent', False)

    if not user_message:
        return jsonify({'response': 'Invalid request.'}), 400

    # Crisis check
    crisis_keywords = ['suicide', 'kill myself', 'end my life', 'hopeless', 'self harm', "can't go on", 'want to die']
    if any(keyword in user_message for keyword in crisis_keywords):
        
        socketio.emit('CRISIS_ALERT', {'message': user_message})
        
        return jsonify({
            'response': "It sounds like you are in serious distress. It's important to talk to someone who can help right now. 🙏",
            'is_crisis': True,
            'helpline': 'Tele-MANAS: 14416',
            'mood': 'sad' 
        })

    # Hyper-Local Adaptation
    local_system_prompt = SYSTEM_PROMPT
    if location:
        local_system_prompt = (
            f"**User's Context:** The user is a student in or near {location}. Be extra mindful of this context.\n\n"
            f"{SYSTEM_PROMPT}"
        )

    # Gemini API Call
    try:
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=local_system_prompt 
        )
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(
            user_message,
            generation_config=generation_config
        )
        
        response_data_str = response.text
        parsed_data = json.loads(response_data_str)

        response_text = parsed_data.get('responseText', 'I am here for you. 😊')
        mood = parsed_data.get('mood', 'neutral')

        # Research Module
        if consent_given:
            try:
                log_entry = ResearchLog(
                    user_message=user_message,
                    bot_response=response_text,
                    mood=mood
                )
                db.session.add(log_entry)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to save research log: {e}")
                db.session.rollback()

    except (genai.types.generation_types.StopCandidateException, json.JSONDecodeError, Exception) as e:
        current_app.logger.error(f"Gemini API request or JSON parsing failed: {e}")
        response_text = "I'm having a little trouble thinking right now. Please try again in a moment. 😥"
        mood = "neutral"
        return jsonify({'response': response_text, 'mood': mood, 'is_crisis': False}), 500

    # Send the response and the mood back to the frontend
    return jsonify({'response': response_text, 'mood': mood, 'is_crisis': False})