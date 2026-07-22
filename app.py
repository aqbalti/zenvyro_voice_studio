"""
Zenvyrolabs Voice Studio - Main Application Entry Point
Production-ready Flask application for AI voice cloning and podcast generation.
"""

import os
import logging
from flask import Flask
from config import Config

from routes.upload_routes import upload_bp
from routes.training_routes import training_bp
from routes.podcast_routes import podcast_bp
from routes.dashboard_routes import dashboard_bp


def create_app(config_class=Config) -> Flask:
    """Application factory pattern for Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    for directory in [
        app.config["UPLOAD_FOLDER"],
        app.config["DATASET_FOLDER"],
        app.config["OUTPUT_FOLDER"],
        app.config["LOG_FOLDER"],
        app.config["SAVED_VOICES_DIR"],
        app.config["TRAINING_DIR"],
    ]:
        os.makedirs(directory, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                os.path.join(app.config["LOG_FOLDER"], "app.log"), encoding="utf-8"
            ),
        ],
    )

    app.register_blueprint(upload_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(podcast_bp)
    app.register_blueprint(dashboard_bp)

    app.logger.info("Zenvyrolabs Voice Studio initialized successfully.")
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )
