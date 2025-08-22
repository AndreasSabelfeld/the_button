from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO
from supabase import create_client, Client
import os

load_dotenv()  # Load environment variables from .env file

socketio = SocketIO(cors_allowed_origins="*")

# Supabase Client
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_app():
    app = Flask(__name__)

    # Blueprints registrieren
    from .routes import routes
    app.register_blueprint(routes)

    # SocketIO mit App verbinden
    socketio.init_app(app)

    return app
