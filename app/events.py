from flask_socketio import emit
from .extensions import socketio # Changed from ". import socketio"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_send_message(json):
    print('Received message: ' + str(json))
    emit('receive_message', json, broadcast=True)