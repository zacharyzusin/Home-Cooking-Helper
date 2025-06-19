from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from flask import g
import traceback

engine = None

def init_db(app):
    """Initialize database connection"""
    global engine
    engine = create_engine(app.config['DATABASE_URI'], poolclass=NullPool)
    app.before_request(before_request)
    app.teardown_request(teardown_request)

def before_request():
    """
    This function is run at the beginning of every web request.
    Sets up a database connection that can be used throughout the request.
    """
    try:
        g.conn = engine.connect()
    except Exception as e:
        print("Problem connecting to database:")
        traceback.print_exc()
        g.conn = None

def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    """
    try:
        if hasattr(g, 'conn') and g.conn:
            g.conn.close()
    except Exception as e:
        pass

def get_db_connection():
    """Get a new database connection"""
    return engine.connect()