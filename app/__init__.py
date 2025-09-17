from flask import Flask
from .extensions import socketio # Import from the new file

def create_app():
    app = Flask(__name__)
    app.config['OLLAMA_API_URL'] = "http://localhost:11434/api/generate"

    # Initialize extensions
    socketio.init_app(app)

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Import events to register handlers
    from . import events

    return app