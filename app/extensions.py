from flask_socketio import SocketIO

# This is now the central place where socketio is defined
socketio = SocketIO(async_mode="threading")