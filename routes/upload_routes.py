"""Upload routes - handles audio file uploads and validation."""

import os
import uuid
import logging
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from services.audio_cleaner import AudioCleaner
from services.silence_remover import SilenceRemover

upload_bp = Blueprint("upload", __name__)
logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_AUDIO_EXTENSIONS"]


@upload_bp.route("/api/upload", methods=["POST"])
def upload_audio():
    """Upload one or more audio files."""
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    results = []

    for file in files:
        if not file or file.filename == "":
            continue
        if not allowed_file(file.filename):
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Unsupported format. Allowed: {', '.join(current_app.config['ALLOWED_AUDIO_EXTENSIONS'])}"
            })
            continue

        safe_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        dest = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        file.save(dest)
        size_kb = round(os.path.getsize(dest) / 1024, 1)
        logger.info("Uploaded: %s (%.1f KB)", unique_name, size_kb)
        results.append({
            "filename": safe_name,
            "saved_as": unique_name,
            "status": "success",
            "size_kb": size_kb,
        })

    return jsonify({"results": results})


@upload_bp.route("/api/files", methods=["GET"])
def list_files():
    """List all uploaded audio files."""
    folder = current_app.config["UPLOAD_FOLDER"]
    files = []
    try:
        for f in sorted(os.listdir(folder)):
            fp = os.path.join(folder, f)
            if os.path.isfile(fp):
                files.append({
                    "name": f,
                    "size_kb": round(os.path.getsize(fp) / 1024, 1),
                    "modified": os.path.getmtime(fp),
                })
    except Exception as e:
        logger.error("Error listing files: %s", e)
    return jsonify({"files": files})


@upload_bp.route("/api/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    """Delete an uploaded file."""
    safe = secure_filename(filename)
    fp = os.path.join(current_app.config["UPLOAD_FOLDER"], safe)
    if os.path.exists(fp):
        os.remove(fp)
        return jsonify({"status": "deleted", "filename": safe})
    return jsonify({"error": "File not found"}), 404


@upload_bp.route("/api/clean-audio", methods=["POST"])
def clean_audio():
    """Run noise reduction on an uploaded file."""
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "filename required"}), 400
    fp = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(filename))
    if not os.path.exists(fp):
        return jsonify({"error": "File not found"}), 404

    cleaner = AudioCleaner()
    logs = []
    out_path, logs = cleaner.clean(fp, logs)
    out_name = os.path.basename(out_path) if out_path else None
    return jsonify({"status": "success" if out_path else "error", "output": out_name, "logs": logs})


@upload_bp.route("/api/remove-silence", methods=["POST"])
def remove_silence():
    """Remove silence from an uploaded file."""
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "filename required"}), 400
    fp = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(filename))
    if not os.path.exists(fp):
        return jsonify({"error": "File not found"}), 404

    remover = SilenceRemover()
    logs = []
    out_path, logs = remover.remove(fp, logs)
    out_name = os.path.basename(out_path) if out_path else None
    return jsonify({"status": "success" if out_path else "error", "output": out_name, "logs": logs})


@upload_bp.route("/api/download/<filename>")
def download_file(filename):
    """Serve a processed audio file for download."""
    safe = secure_filename(filename)
    # Search in output and upload folders
    for folder in [current_app.config["OUTPUT_FOLDER"], current_app.config["UPLOAD_FOLDER"]]:
        fp = os.path.join(folder, safe)
        if os.path.exists(fp):
            return send_from_directory(folder, safe, as_attachment=True)
    return jsonify({"error": "File not found"}), 404
