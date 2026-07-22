"""
ml/train.py — Placeholder for future RVC/F5-TTS fine-tuning pipeline.
This module is the entry point for model training once a dataset is prepared.
"""
import logging

logger = logging.getLogger(__name__)


def train_voice_model(session_dir: str, model_name: str, epochs: int = 100):
    """
    Placeholder training loop.
    Replace with actual RVC / VITS / F5-TTS training code.

    Args:
        session_dir: Directory containing preprocessed WAV chunks.
        model_name: Name for the output model.
        epochs: Number of training epochs.
    """
    logger.info("Training placeholder: session=%s, model=%s, epochs=%d",
                session_dir, model_name, epochs)
    # TODO: integrate RVC training pipeline here
    raise NotImplementedError(
        "Full model training requires RVC or F5-TTS installed. "
        "Use the preprocessing pipeline to prepare your dataset first, "
        "then point your preferred training framework at the session directory."
    )
