import io
import logging
import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import RecognitionResponse
from pydub import AudioSegment
from services.bdd_client import BddClient
from services.command_parser import CommandParser, Intent
from services.music_matcher import MusicMatcher
from services.speech_to_text import SpeechToTextService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Service Vocal - Music Voice App",
    description="API pour la reconnaissance vocale et le traitement des commandes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
stt_service = None
command_parser = CommandParser()
music_matcher = MusicMatcher()
bdd_client = BddClient()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global stt_service
    try:
        stt_service = SpeechToTextService()
        logger.info("Speech-to-text service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize STT service: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    bdd_healthy = await bdd_client.health_check()
    return {
        "status": "healthy" if stt_service else "degraded",
        "stt_service": "ready" if stt_service else "not ready",
        "bdd_service": "connected" if bdd_healthy else "disconnected",
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {"service": "service-vocal", "version": "1.0.0", "endpoints": ["/health", "/recognize"]}


@app.post("/recognize", response_model=RecognitionResponse)
async def recognize_audio(audio: UploadFile = File(...)):
    """
    Process audio file and return recognized command.

    Accepts WAV or other audio formats (will be converted to WAV 16kHz mono).
    """
    if not stt_service:
        raise HTTPException(status_code=503, detail="STT service not available")

    try:
        # Read uploaded file
        audio_content = await audio.read()
        logger.info(f"Received audio file: {audio.filename}, size: {len(audio_content)} bytes")

        # Convert to WAV 16kHz mono if needed
        wav_path = await convert_to_wav(audio_content, audio.filename)

        try:
            # Transcribe audio
            transcript = stt_service.transcribe(wav_path)

            if not transcript:
                return RecognitionResponse(
                    success=False,
                    transcript=None,
                    intent=Intent.UNKNOWN.value,
                    error="No speech detected",
                )

            # Parse command
            intent, music_query = command_parser.parse(transcript)

            # If PLAY intent with query, find matching music
            musique = None
            if intent == Intent.PLAY and music_query:
                musiques = await bdd_client.get_all_musiques()
                musique = music_matcher.find_best_match(music_query, musiques)

                if not musique:
                    return RecognitionResponse(
                        success=True,
                        transcript=transcript,
                        intent=intent.value,
                        musique=None,
                        error=f"Aucune musique trouvée pour '{music_query}'",
                    )

            return RecognitionResponse(
                success=True, transcript=transcript, intent=intent.value, musique=musique
            )

        finally:
            # Clean up temp file
            if os.path.exists(wav_path):
                os.remove(wav_path)

    except Exception as e:
        logger.error(f"Recognition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe")
async def transcribe_only(audio: UploadFile = File(...)):
    """Transcribe audio without parsing commands."""
    if not stt_service:
        raise HTTPException(status_code=503, detail="STT service not available")

    try:
        audio_content = await audio.read()
        wav_path = await convert_to_wav(audio_content, audio.filename)

        try:
            transcript = stt_service.transcribe(wav_path)
            return {"transcript": transcript}
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def convert_to_wav(audio_content: bytes, filename: str) -> str:
    """Convert audio to WAV 16kHz mono format."""
    # Create temp file for output
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name

    try:
        # Detect format from filename or try common formats
        file_ext = os.path.splitext(filename)[1].lower() if filename else ""

        # Load audio with pydub
        if file_ext == ".wav":
            audio = AudioSegment.from_wav(io.BytesIO(audio_content))
        elif file_ext == ".mp3":
            audio = AudioSegment.from_mp3(io.BytesIO(audio_content))
        elif file_ext in [".ogg", ".opus"]:
            audio = AudioSegment.from_ogg(io.BytesIO(audio_content))
        elif file_ext == ".m4a":
            audio = AudioSegment.from_file(io.BytesIO(audio_content), format="m4a")
        else:
            # Try to detect format
            audio = AudioSegment.from_file(io.BytesIO(audio_content))

        # Convert to 16kHz mono
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export as WAV
        audio.export(wav_path, format="wav")

        logger.info(f"Converted audio to WAV: {wav_path}")
        return wav_path

    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        if os.path.exists(wav_path):
            os.remove(wav_path)
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)
