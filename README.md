# Zenvyrolabs Voice Studio

A production-ready, full-stack AI Voice Studio built with Python 3.11, Flask, and Docker.
Clone voices, clean audio datasets, train ML preprocessing pipelines, and generate multi-character podcasts — all from a sleek dark SaaS dashboard.

---

## Features

- **Drag & Drop Upload** — WAV, MP3, FLAC, OGG support with live progress bars
- **Noise Reduction** — Spectral noise gating via `noisereduce`
- **Silence Removal** — Intelligent silence stripping via `pydub`
- **ML Preprocessing Pipeline** — Resample → clean → normalize → chunk → export
- **Voice Profile Library** — Save reference audio + text for each character
- **Multi-Voice Podcast Generator** — Script parser → per-line TTS → stitched episode
- **Live Dashboard** — Storage usage charts, system health, voice profiles overview
- **Production Docker Setup** — One command to run the whole stack

---

## Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/zenvyrolabs/voice-studio
cd voice-studio
docker-compose up --build
```
Open http://localhost:5000

### Local Development
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## Project Structure
```
voice_studio/
├── app.py                  # Flask app factory
├── config.py               # All settings & environment vars
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── routes/                 # Flask blueprints
│   ├── upload_routes.py    # POST /api/upload, /api/clean-audio, /api/remove-silence
│   ├── training_routes.py  # POST /api/train, GET /api/training/sessions
│   ├── podcast_routes.py   # GET/POST /api/voices, POST /api/generate
│   └── dashboard_routes.py # GET /, /upload, /training, /podcast, /dashboard, /settings
│
├── services/               # Business logic layer
│   ├── audio_cleaner.py    # Noise reduction pipeline
│   ├── silence_remover.py  # Silence detection & removal
│   ├── trainer.py          # ML preprocessing pipeline
│   └── podcast_generator.py# Script parser + audio stitcher
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Sidebar + topbar + toasts + loading overlay
│   ├── index.html          # Hero + stats + quick actions + features
│   ├── upload.html         # Drop zone + file list + processing panel
│   ├── training.html       # Pipeline config + live log + sessions list
│   ├── podcast.html        # Voice library + script editor + audio player
│   ├── dashboard.html      # Charts + health grid + voice profiles
│   └── settings.html       # Audio defaults + platform info
│
└── static/
    ├── css/studio.css      # Full design system (dark theme + glassmorphism)
    └── js/studio.js        # Toast, loading overlay, sidebar toggle
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/upload` | Upload page |
| GET | `/training` | Training page |
| GET | `/podcast` | Podcast studio page |
| GET | `/dashboard` | Dashboard page |
| GET | `/settings` | Settings page |
| POST | `/api/upload` | Upload audio files (multipart) |
| GET | `/api/files` | List uploaded files |
| DELETE | `/api/files/<name>` | Delete an uploaded file |
| POST | `/api/clean-audio` | Run noise reduction on a file |
| POST | `/api/remove-silence` | Remove silence from a file |
| POST | `/api/train` | Run ML preprocessing pipeline |
| GET | `/api/training/sessions` | List training sessions |
| GET | `/api/voices` | List saved voice profiles |
| POST | `/api/voices` | Save a new voice profile |
| DELETE | `/api/voices/<name>` | Delete a voice profile |
| POST | `/api/generate` | Generate a podcast from script |
| GET | `/api/output/<filename>` | Stream generated audio |
| GET | `/api/download/<filename>` | Download processed audio |
| GET | `/api/dashboard` | Dashboard statistics JSON |
| GET | `/api/status` | Health check |

---

## Podcast Script Format

```
CHARACTER_NAME: Their dialogue goes here.
OTHER_CHARACTER: And their response here.
```

Character names must match saved voice profile names (case-insensitive). Example:

```
NARUTO: Hey Luffy, long time no see!
LUFFY: Nothing much, just ate the best meat ever!
NARUTO: That sounds amazing. Want to train together?
LUFFY: Yes! Let's gooo!
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `zenvyro-voice-studio-secret-2024` | Flask session secret |
| `FLASK_DEBUG` | `false` | Enable debug mode |

---

## License

MIT License — Zenvyrolabs 2024

---

## Future Improvements

- F5-TTS / XTTS-v2 integration for true zero-shot voice cloning
- RVC (Retrieval-based Voice Conversion) model training UI
- Real-time streaming podcast generation
- User authentication & multi-tenant workspaces
- Cloud storage (S3 / GCS) backend
- GPU-accelerated inference via CUDA containers
- Whisper-based transcript generation
- Export to MP3, AAC, Opus formats
