import os
import click
from flask import Flask
from config import Config
from database import init_db
from routes import register_routes

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    init_db(app)
    register_routes(app)
    
    return app

if __name__ == "__main__":
    @click.command()
    @click.option('--debug', is_flag=True, help='Enable debug mode')
    @click.option('--threaded', is_flag=True, help='Enable threaded mode')
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """Run the Flask application"""
        app = create_app()
        print(f"Running on {host}:{port}")
        app.run(host=host, port=port, debug=debug, threaded=threaded)
    
    run()