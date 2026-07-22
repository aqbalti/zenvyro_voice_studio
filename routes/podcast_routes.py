"""Podcast routes - multi-voice podcast generation and voice management."""

import os
import shutil
import logging
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from services.podcast_generator import PodcastGenerator

podcast_bp = Blueprint("podcast", __name__)
logger = logging.getLogger(__name__)


def _voices_dir():
    return current_app.config["SAVED_VOICES_DIR"]


@podcast_bp.route("/api/voices", methods=["GET"])
def list_voices():
    """List all saved voice profiles."""
    vdir = _voices_dir()
    voices = []
    try:
        for name in sorted(os.listdir(vdir)):
            dp = os.path.join(vdir, name)
            if os.path.isdir(dp):
                has_audio = os.path.exists(os.path.join(dp, "audio.wav"))
                text_path = os.path.join(dp, "text.txt")
                ref_text = ""
                if os.path.exists(text_path):
                    with open(text_path, encoding="utf-8") as f:
                        ref_text = f.read().strip()
                voices.append({"name": name, "has_audio": has_audio, "ref_text": ref_text})
    except Exception as e:
        logger.error("Error listing voices: %s", e)
    return jsonify({"voices": voices})


@podcast_bp.route("/api/voices", methods=["POST"])
def save_voice():
    """Save a new voice profile with audio + reference text."""
    name = (request.form.get("name") or "").strip().replace(" ", "_")
    ref_text = request.form.get("ref_text", "")
    if not name:
        return jsonify({"error": "Voice name is required"}), 400

    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "Audio file is required"}), 400

    voice_dir = os.path.join(_voices_dir(), name)
    os.makedirs(voice_dir, exist_ok=True)
    audio_file.save(os.path.join(voice_dir, "audio.wav"))
    with open(os.path.join(voice_dir, "text.txt"), "w", encoding="utf-8") as f:
        f.write(ref_text)

    logger.info("Saved voice: %s", name)
    return jsonify({"status": "saved", "name": name})


@podcast_bp.route("/api/voices/<name>", methods=["DELETE"])
def delete_voice(name):
    """Delete a saved voice profile."""
    safe = secure_filename(name)
    voice_dir = os.path.join(_voices_dir(), safe)
    if os.path.exists(voice_dir):
        shutil.rmtree(voice_dir)
        return jsonify({"status": "deleted", "name": safe})
    return jsonify({"error": "Voice not found"}), 404


@podcast_bp.route("/api/generate", methods=["POST"])
def generate_podcast():
    """Generate a multi-voice podcast from a script."""
    data = request.get_json() or {}
    script = data.get("script", "").strip()
    pause_ms = int(data.get("pause_ms", 500))
    language = data.get("language", "en")

    if not script:
        return jsonify({"error": "Script is required"}), 400

    generator = PodcastGenerator(
        voices_dir=_voices_dir(),
        output_dir=current_app.config["OUTPUT_FOLDER"],
    )
    output_path, logs = generator.generate(script, pause_ms=pause_ms, language=language)

    if output_path:
        return jsonify({
            "status": "success",
            "output": os.path.basename(output_path),
            "logs": logs,
        })
    return jsonify({"status": "error", "logs": logs}), 500


@podcast_bp.route("/api/output/<filename>")
def serve_output(filename):
    """Stream a generated audio file."""
    safe = secure_filename(filename)
    folder = current_app.config["OUTPUT_FOLDER"]
    fp = os.path.join(folder, safe)
    if os.path.exists(fp):
        return send_from_directory(folder, safe)
    return jsonify({"error": "File not found"}), 404
