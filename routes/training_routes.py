"""Training routes - handles voice model training pipeline."""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.trainer import VoiceTrainer

training_bp = Blueprint("training", __name__)
logger = logging.getLogger(__name__)


@training_bp.route("/api/train", methods=["POST"])
def train_model():
    """Preprocess audio dataset for training."""
    data = request.get_json() or {}
    filename = data.get("filename")
    chunk_seconds = float(data.get("chunk_seconds", 10))
    normalize_db = float(data.get("normalize_db", -20.0))

    if not filename:
        return jsonify({"error": "filename required"}), 400

    fp = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(filename))
    if not os.path.exists(fp):
        return jsonify({"error": "File not found"}), 404

    trainer = VoiceTrainer(
        training_dir=current_app.config["TRAINING_DIR"],
        sample_rate=current_app.config["DEFAULT_SAMPLE_RATE"],
    )
    result, logs = trainer.preprocess(fp, chunk_seconds=chunk_seconds, normalize_db=normalize_db)

    if result:
        return jsonify({"status": "success", "session_dir": result, "logs": logs})
    return jsonify({"status": "error", "logs": logs}), 500


@training_bp.route("/api/training/sessions", methods=["GET"])
def list_sessions():
    """List all training sessions."""
    training_dir = current_app.config["TRAINING_DIR"]
    sessions = []
    try:
        for name in sorted(os.listdir(training_dir)):
            path = os.path.join(training_dir, name)
            if os.path.isdir(path):
                chunks = [f for f in os.listdir(path) if f.endswith(".wav")]
                sessions.append({"name": name, "chunks": len(chunks), "path": path})
    except Exception as e:
        logger.error("Error listing sessions: %s", e)
    return jsonify({"sessions": sessions})
