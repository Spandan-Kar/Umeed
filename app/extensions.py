from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# This is now the central place where extensions are defined
socketio = SocketIO(async_mode="threading")
db = SQLAlchemy() # --- NEW ---