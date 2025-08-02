from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('DEBUG', True)
    
    # Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app

app = create_app()

@app.route("/")
def home():
    return "Hospital Bed Management System is running!"

if __name__ == "__main__":
    app.run(debug=True)
