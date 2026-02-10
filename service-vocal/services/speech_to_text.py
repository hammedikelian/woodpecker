import json
import logging
import wave

from config import settings
from vosk import KaldiRecognizer, Model

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Service for converting speech to text using Vosk."""

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Vosk model."""
        try:
            logger.info(f"Loading Vosk model from {settings.vosk_model_path}")
            self.model = Model(settings.vosk_model_path)
            logger.info("Vosk model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to WAV file (16kHz mono)

        Returns:
            Transcribed text
        """
        if not self.model:
            raise RuntimeError("Vosk model not loaded")

        try:
            wf = wave.open(audio_path, "rb")

            # Verify audio format
            if wf.getnchannels() != 1:
                raise ValueError("Audio must be mono")
            if wf.getsampwidth() != 2:
                raise ValueError("Audio must be 16-bit")
            if wf.getframerate() not in [8000, 16000]:
                logger.warning(f"Sample rate is {wf.getframerate()}, expected 16000")

            recognizer = KaldiRecognizer(self.model, wf.getframerate())
            recognizer.SetWords(True)

            results = []

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get("text"):
                        results.append(result["text"])

            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            if final_result.get("text"):
                results.append(final_result["text"])

            wf.close()

            transcript = " ".join(results).strip()
            logger.info(f"Transcription: '{transcript}'")
            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def transcribe_bytes(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """
        Transcribe audio bytes to text.

        Args:
            audio_data: Raw audio bytes (16-bit PCM)
            sample_rate: Sample rate of audio

        Returns:
            Transcribed text
        """
        if not self.model:
            raise RuntimeError("Vosk model not loaded")

        try:
            recognizer = KaldiRecognizer(self.model, sample_rate)
            recognizer.SetWords(True)

            results = []

            # Process in chunks
            chunk_size = 8000
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                if recognizer.AcceptWaveform(chunk):
                    result = json.loads(recognizer.Result())
                    if result.get("text"):
                        results.append(result["text"])

            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            if final_result.get("text"):
                results.append(final_result["text"])

            transcript = " ".join(results).strip()
            logger.info(f"Transcription: '{transcript}'")
            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
