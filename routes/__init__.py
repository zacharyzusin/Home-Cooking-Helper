from .main_routes import main_bp
from .auth_routes import auth_bp
from .recipe_routes import recipe_bp
from .user_routes import user_bp

def register_routes(app):
    """Register all route blueprints with the Flask app"""
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(user_bp)