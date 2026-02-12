"""
NERO Voice Assistant - TTS Module (Cartesia Text-to-Speech)

Text-to-speech conversion using Cartesia API with Brazilian Portuguese voices.
"""

import httpx
import asyncio
import os
import tempfile
import platform
from typing import Dict, Optional
from .logger import NeroLogger


class TTS:
    """Text-to-speech conversion using Cartesia API."""

    # Available Brazilian Portuguese voices
    VOICES = {
        "ana": "79a125e8-cd45-4c13-8a67-a188a65c6d09",  # Female voice
        "lucas": "d6b6e68a-407c-45b0-9330-b96511922666",  # Male voice
    }

    def __init__(self, api_key: str, logger: NeroLogger):
        """Initialize TTS module.

        Args:
            api_key: Cartesia API key
            logger: NeroLogger instance
        """
        self.api_key = api_key
        self.logger = logger
        self.base_url = "https://api.cartesia.ai/v1/audio"
        self.client: Optional[httpx.AsyncClient] = None
        self.temp_dir = tempfile.gettempdir()

        self.logger.debug("TTS initialized with Cartesia")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client.

        Returns:
            Async HTTP client instance
        """
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(30.0),
            )
        return self.client

    async def close(self) -> None:
        """Close HTTP client connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            self.logger.debug("Cartesia HTTP client closed")

    def _get_voice_id(self, voice: str) -> str:
        """Get Cartesia voice ID from voice name.

        Args:
            voice: Voice name ('ana' or 'lucas')

        Returns:
            Cartesia voice ID
        """
        return self.VOICES.get(voice.lower(), self.VOICES["ana"])

    async def gerar_audio(
        self,
        texto: str,
        voz: str = "ana",
        estilo: str = "simplified",
        output_format: str = "mp3",
    ) -> Dict:
        """Generate audio from text using Cartesia API.

        Args:
            texto: Text to convert to speech
            voz: Voice name ('ana' for female, 'lucas' for male)
            estilo: Speaking style ('simplified', 'narrative', etc.)
            output_format: Audio format ('mp3', 'wav', 'pcm')

        Returns:
            Result dict:
                {
                    'sucesso': bool,
                    'caminho_arquivo': str,
                    'duracao_segundos': float,
                    'texto': str,
                }
        """
        if not texto or not texto.strip():
            self.logger.warning("Empty text provided for TTS")
            return {
                "sucesso": False,
                "caminho_arquivo": "",
                "duracao_segundos": 0,
                "texto": "",
            }

        if not self.api_key or self.api_key.startswith("your_"):
            error_msg = "Invalid Cartesia API key. Please set CARTESIA_API_KEY in .env file"
            self.logger.error(error_msg)
            return {
                "sucesso": False,
                "caminho_arquivo": "",
                "duracao_segundos": 0,
                "texto": texto,
            }

        self.logger.tts(f"Generating audio for: '{texto[:50]}...'")

        try:
            client = await self._get_client()
            voice_id = self._get_voice_id(voz)

            # Prepare request
            payload = {
                "transcript": texto,
                "voice_id": voice_id,
                "output_format": {
                    "container": output_format,
                    "sample_rate": 24000,
                    "bit_depth": 16,
                },
                "language": "pt-BR",
                "style": estilo,
            }

            # Send request
            response = await client.post(self.base_url, json=payload)

            if response.status_code != 200:
                error_text = response.text
                self.logger.error(f"Cartesia API error: {response.status_code} - {error_text}")
                return {
                    "sucesso": False,
                    "caminho_arquivo": "",
                    "duracao_segundos": 0,
                    "texto": texto,
                }

            # Get audio content
            audio_data = response.content

            # Save to temporary file
            timestamp = asyncio.get_event_loop().time()
            filename = f"nero_tts_{timestamp}.{output_format}"
            filepath = os.path.join(self.temp_dir, filename)

            with open(filepath, "wb") as f:
                f.write(audio_data)

            # Get file size for duration estimation
            file_size = len(audio_data)
            # Rough estimate: MP3 at 128 kbps = 16 KB/s
            duracao_estimada = file_size / (128 * 1024 / 8)

            self.logger.complete(f"Audio generated: {filepath} ({duracao_estimada:.1f}s)")

            return {
                "sucesso": True,
                "caminho_arquivo": filepath,
                "duracao_segundos": duracao_estimada,
                "texto": texto,
            }

        except httpx.TimeoutException as e:
            self.logger.error("Cartesia API timeout", e)
            return {
                "sucesso": False,
                "caminho_arquivo": "",
                "duracao_segundos": 0,
                "texto": texto,
            }
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Cartesia HTTP error: {e.response.status_code}", e)
            return {
                "sucesso": False,
                "caminho_arquivo": "",
                "duracao_segundos": 0,
                "texto": texto,
            }
        except Exception as e:
            self.logger.error("Failed to generate audio", e)
            return {
                "sucesso": False,
                "caminho_arquivo": "",
                "duracao_segundos": 0,
                "texto": texto,
            }

    async def reproduzir_audio(self, caminho_arquivo: str) -> bool:
        """Play audio file using platform-specific method.

        Args:
            caminho_arquivo: Path to audio file

        Returns:
            True if playback successful, False otherwise
        """
        if not os.path.exists(caminho_arquivo):
            self.logger.error(f"Audio file not found: {caminho_arquivo}")
            return False

        self.logger.tts(f"Playing audio: {caminho_arquivo}")

        try:
            system = platform.system()

            if system == "Windows":
                # Windows: use powershell or winsound
                import subprocess
                subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{caminho_arquivo}').PlaySync()"],
                    check=True,
                )
            elif system == "Linux":
                # Linux: use aplay
                import subprocess
                subprocess.run(["aplay", caminho_arquivo], check=True)
            elif system == "Darwin":
                # macOS: use afplay
                import subprocess
                subprocess.run(["afplay", caminho_arquivo], check=True)
            else:
                self.logger.warning(f"Unknown platform: {system}")
                return False

            self.logger.complete("Audio playback complete")
            return True

        except Exception as e:
            self.logger.error(f"Failed to play audio: {e}", e)
            # Fallback: print text
            self.logger.info("Audio playback failed, showing text instead")
            return False

    def limpar_arquivos_temporarios(self) -> None:
        """Clean up temporary audio files."""
        try:
            import glob
            pattern = os.path.join(self.temp_dir, "nero_tts_*")
            files = glob.glob(pattern)

            for filepath in files:
                try:
                    os.remove(filepath)
                    self.logger.debug(f"Removed temporary file: {filepath}")
                except Exception as e:
                    self.logger.debug(f"Failed to remove {filepath}: {e}")

            if files:
                self.logger.info(f"Cleaned up {len(files)} temporary audio files")

        except Exception as e:
            self.logger.debug(f"Cleanup error: {e}")

    async def falar(
        self,
        texto: str,
        voz: str = "ana",
        estilo: str = "simplified",
        tocar_automatically: bool = True,
    ) -> Dict:
        """Generate and optionally play audio from text.

        Args:
            texto: Text to speak
            voz: Voice name ('ana' or 'lucas')
            estilo: Speaking style
            tocar_automatically: If True, play audio automatically

        Returns:
            Result dict from gerar_audio
        """
        result = await self.gerar_audio(texto, voz, estilo)

        if result["sucesso"] and tocar_automatically:
            await self.reproduzir_audio(result["caminho_arquivo"])

        return result
