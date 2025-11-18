from flask import Flask
from .extensions import socketio, db
import google.generativeai as genai
import os

def create_app():
    app = Flask(__name__)
    
    # --- API KEY CONFIGURATION ---
    # I've used the key you provided.
    # WARNING: See my note at the end of this message.
    GEMINI_API_KEY = "AIzaSyCI2paI9Tege-5pqqAlgMWP8QBjBi7yv3o"
    
    # --- REMOVED OLLAMA CONFIG ---
    # app.config['OLLAMA_API_URL'] = "http://localhost:11434/api/generate"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///umeed.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- NEW: Configure Gemini API ---
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"ERROR: Failed to configure Gemini API: {e}")
        print(f"Please check your API key.")
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    # Initialize extensions
    socketio.init_app(app)
    db.init_app(app)

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Import events to register handlers
    from . import events
    
    # Import models and create tables
    from . import models
    from .routes import seed_data
    
    with app.app_context():
        db.create_all()
        seed_data()

    return app