from .extensions import db
from datetime import datetime

class ResearchLog(db.Model):
    __tablename__ = 'research_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(1000), nullable=True)
    bot_response = db.Column(db.String(1000), nullable=True)
    mood = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ResearchLog {self.id} - Mood: {self.mood}>'

# --- NEW: Therapist Model (Feature 6) ---
class Therapist(db.Model):
    __tablename__ = 'therapist'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(150))
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Therapist {self.name}>'

# --- NEW: Product Model (Feature 6) ---
class Product(db.Model):
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Product {self.name}>'