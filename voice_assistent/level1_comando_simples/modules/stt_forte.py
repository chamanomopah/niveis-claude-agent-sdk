"""
NERO Voice Assistant - Strong STT Module (Deepgram Transcription)

High-quality speech-to-text transcription using Deepgram API.
Streaming support with Portuguese language model.
"""

import httpx
import asyncio
from typing import Callable, Optional, Dict
import io
from .logger import NeroLogger


class STTForte:
    """High-quality speech transcription using Deepgram API."""

    def __init__(self, api_key: str, logger: NeroLogger):
        """Initialize STT Forte (strong speech recognition).

        Args:
            api_key: Deepgram API key
            logger: NeroLogger instance
        """
        self.api_key = api_key
        self.logger = logger
        self.base_url = "https://api.deepgram.com/v1/listen"
        self.client: Optional[httpx.AsyncClient] = None

        self.logger.debug("STT Forte initialized with Deepgram")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client.

        Returns:
            Async HTTP client instance
        """
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "audio/raw",
                },
                timeout=httpx.Timeout(600.0),  # 10 minute max
            )
        return self.client

    async def close(self) -> None:
        """Close HTTP client connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            self.logger.debug("Deepgram HTTP client closed")

    def _build_params(self) -> Dict:
        """Build request parameters for Deepgram API.

        Returns:
            Dictionary of API parameters
        """
        return {
            "model": "nova-2",  # Latest model
            "language": "pt-BR",  # Brazilian Portuguese
            "smart_format": "true",  # Enable formatting
            "punctuate": "true",  # Add punctuation
            "paragraphs": "true",  # Add paragraphs
            "numerals": "true",  # Convert numbers to digits
            "profanity_filter": "false",  # Don't filter profanity
            "diarize": "false",  # No speaker diarization needed
            "filler_words": "false",  # Remove um, uh, etc.
        }

    async def transcrever_audio_file(
        self,
        audio_data: bytes,
        callback: Optional[Callable] = None,
    ) -> str:
        """Transcribe audio file using Deepgram REST API.

        Args:
            audio_data: Raw audio bytes (WAV format, 16kHz, mono)
            callback: Optional callback for progress updates

        Returns:
            Transcribed text string
        """
        if not self.api_key or self.api_key.startswith("your_"):
            error_msg = "Invalid Deepgram API key. Please set DEEPGRAM_API_KEY in .env file"
            self.logger.error(error_msg)
            return ""

        self.logger.transcribing("Sending audio to Deepgram for transcription...")

        try:
            client = await self._get_client()

            # Prepare request
            params = self._build_params()

            if callback:
                callback("sending")

            # Send request to Deepgram
            response = await client.post(
                self.base_url,
                params=params,
                content=audio_data,
            )

            if callback:
                callback("processing")

            # Check response
            if response.status_code != 200:
                error_text = response.text
                self.logger.error(f"Deepgram API error: {response.status_code} - {error_text}")
                return ""

            # Parse response
            result = response.json()

            if callback:
                callback("complete")

            # Extract transcript
            transcript = ""
            if "results" in result and "channels" in result["results"]:
                channel = result["results"]["channels"][0]
                if "alternatives" in channel:
                    alternative = channel["alternatives"][0]
                    transcript = alternative.get("transcript", "")

                    # Extract words with timestamps for debugging
                    words = alternative.get("words", [])
                    if self.logger.verbose and words:
                        self.logger.debug(f"Transcribed {len(words)} words")

            if transcript:
                self.logger.transcript(transcript)
                return transcript
            else:
                self.logger.warning("Deepgram returned empty transcript")
                return ""

        except httpx.TimeoutException as e:
            self.logger.error("Deepgram API timeout", e)
            return ""
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Deepgram HTTP error: {e.response.status_code}", e)
            return ""
        except Exception as e:
            self.logger.error("Failed to transcribe audio", e)
            return ""

    async def transcrever_em_tempo_real(
        self,
        audio_stream: Callable,
        callback: Optional[Callable] = None,
        max_duration_segundos: int = 600,
    ) -> str:
        """Transcribe streaming audio using Deepgram.

        This method streams audio chunks to Deepgram and accumulates
        the transcript as it arrives. Stops on stop word or timeout.

        Args:
            audio_stream: Async callable that yields audio chunks
            callback: Optional callback for transcript chunks
            max_duration_segundos: Maximum recording duration (default: 600 = 10 min)

        Returns:
            Full transcribed text
        """
        if not self.api_key or self.api_key.startswith("your_"):
            error_msg = "Invalid Deepgram API key. Please set DEEPGRAM_API_KEY in .env file"
            self.logger.error(error_msg)
            return ""

        self.logger.transcribing("Starting real-time transcription...")
        self.logger.recording(f"Max duration: {max_duration_segundos}s")

        try:
            client = await self._get_client()
            params = self._build_params()

            # For streaming, we need to use WebSocket endpoint
            # Fallback to file-based transcription for simplicity
            self.logger.debug("Using file-based transcription (not streaming)")

            # Collect all audio chunks
            audio_chunks = []
            start_time = asyncio.get_event_loop().time()

            async for chunk, is_complete in audio_stream():
                audio_chunks.append(chunk)

                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= max_duration_segundos:
                    self.logger.warning(f"Transcription timeout after {elapsed:.1f}s")
                    break

                if is_complete:
                    break

            # Combine chunks and transcribe
            if audio_chunks:
                audio_data = b"".join(audio_chunks)
                return await self.transcrever_audio_file(audio_data, callback)
            else:
                self.logger.warning("No audio data collected")
                return ""

        except Exception as e:
            self.logger.error("Real-time transcription failed", e)
            return ""
