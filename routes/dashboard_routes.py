"""Dashboard routes - serves the main UI pages."""

import os
import json
from flask import Blueprint, render_template, jsonify, current_app

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("index.html")


@dashboard_bp.route("/upload")
def upload_page():
    return render_template("upload.html")


@dashboard_bp.route("/training")
def training_page():
    return render_template("training.html")


@dashboard_bp.route("/podcast")
def podcast_page():
    return render_template("podcast.html")


@dashboard_bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@dashboard_bp.route("/settings")
def settings_page():
    return render_template("settings.html")


@dashboard_bp.route("/api/dashboard")
def api_dashboard():
    """Return dashboard statistics as JSON."""
    cfg = current_app.config
    try:
        upload_count = len([
            f for f in os.listdir(cfg["UPLOAD_FOLDER"])
            if os.path.isfile(os.path.join(cfg["UPLOAD_FOLDER"], f))
        ])
    except Exception:
        upload_count = 0

    try:
        voices = [
            d for d in os.listdir(cfg["SAVED_VOICES_DIR"])
            if os.path.isdir(os.path.join(cfg["SAVED_VOICES_DIR"], d))
        ]
        voice_count = len(voices)
    except Exception:
        voices = []
        voice_count = 0

    try:
        dataset_count = len([
            d for d in os.listdir(cfg["TRAINING_DIR"])
            if os.path.isdir(os.path.join(cfg["TRAINING_DIR"], d))
        ])
    except Exception:
        dataset_count = 0

    try:
        output_files = [
            f for f in os.listdir(cfg["OUTPUT_FOLDER"])
            if f.endswith(".wav") or f.endswith(".mp3")
        ]
        podcast_count = len(output_files)
    except Exception:
        podcast_count = 0

    # Storage usage
    def folder_size_mb(path):
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
        except Exception:
            pass
        return round(total / (1024 * 1024), 1)

    return jsonify({
        "uploads": upload_count,
        "voices": voice_count,
        "voice_list": voices,
        "datasets": dataset_count,
        "podcasts": podcast_count,
        "storage": {
            "uploads_mb": folder_size_mb(cfg["UPLOAD_FOLDER"]),
            "output_mb": folder_size_mb(cfg["OUTPUT_FOLDER"]),
            "training_mb": folder_size_mb(cfg["TRAINING_DIR"]),
        },
        "system": {
            "status": "healthy",
            "gpu": _check_gpu(),
        }
    })


def _check_gpu():
    try:
        import torch
        if torch.cuda.is_available():
            return {"available": True, "name": torch.cuda.get_device_name(0)}
    except Exception:
        pass
    return {"available": False, "name": "CPU only"}


@dashboard_bp.route("/api/status")
def api_status():
    return jsonify({"status": "ok", "service": "Zenvyrolabs Voice Studio"})
