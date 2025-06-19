import os
import uuid

class Config:
    """Application configuration class"""
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid1())
    DATABASE_URI = "postgresql://postgres@localhost:5432/homecookinghelper"
    MIN_PASSWORD_LENGTH = 8
    MAX_SEARCH_RESULTS = 20
    MAX_REVIEWS_DISPLAY = 20
    CUISINE_TYPES = [
        'American', 'Chinese', 'Cuban', 'Greek', 'Indian', 
        'Italian', 'Japanese', 'Korean', 'Mexican', 'Thai', 'Vietnamese'
    ]
    COMPLEXITY_LEVELS = ('Beginner', 'Aspiring Chef', 'Master Chef')