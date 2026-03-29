"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import NutriScanner


def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)

    # Enable CORS for frontend access
    CORS(app)

    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = Path(__file__).parent.parent / 'outputs' / 'uploads'
    app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)

    # Initialize NutriScanner
    app.nutriscanner = NutriScanner()

    # Register routes
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Health check endpoint
    @app.route('/')
    def index():
        return {
            "message": "NutriScanner API is running!",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "scan_package": "/api/scan-package",
                "analyze_meal": "/api/analyze-meal",
                "compare": "/api/compare"
            }
        }

    @app.route('/health')
    def health():
        return {"status": "healthy"}

    return app