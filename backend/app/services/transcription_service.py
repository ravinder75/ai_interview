import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TranscriptionService:
    """
    Speech-to-text service interface.
    Initially handles browser Web Speech API transcripts,
    structured with an abstraction enabling server-side Whisper API integration.
    """
    async def process_transcript(self, raw_transcript: str) -> str:
        """Sanitize and format raw real-time speech transcription."""
        if not raw_transcript:
            return ""
        # Clean up double spaces or vocal fillers if needed
        cleaned = " ".join(raw_transcript.split())
        return cleaned

    async def transcribe_audio_file(self, audio_bytes: bytes, filename: str) -> str:
        """
        Placeholder for Whisper-compatible audio file transcription.
        Will connect to Whisper API / whisper-cpp endpoints when configured.
        """
        logger.info(f"Received audio file {filename} ({len(audio_bytes)} bytes) for transcription.")
        return "Transcribed audio response content placeholder."

transcription_service = TranscriptionService()
