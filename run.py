from app import create_app
from app.extensions import socketio # Import from the new file

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)