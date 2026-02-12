# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "claude-agent-sdk>=0.1.0",
#   "rich>=13.0.0",
#   "speechrecognition>=3.10.0",
#   "pyaudio>=0.2.14",
#   "pocketsphinx>=5.0.0",
#   "httpx>=0.27.0",
#   "python-dotenv>=1.0.0",
# ]
# ///

"""
NERO Voice Assistant - Main Orchestration Script

A voice-controlled AI assistant using:
- Wake word detection (offline with PocketSphinx)
- High-quality STT (Deepgram API)
- Claude Agent SDK for processing
- Brazilian Portuguese TTS (Cartesia API)

Usage:
    uv run nero_assistant.py
    python nero_assistant.py
"""

import asyncio
import os
import sys
import signal
from typing import Optional
from dotenv import load_dotenv

# Import modules
from modules.logger import NeroLogger
from modules.stt_fraco import STTFraco
from modules.stt_forte import STTForte
from modules.tts import TTS
from modules.agent_handler import AgentHandler


class MaquinaEstadosNero:
    """State machine for NERO voice assistant."""

    # State definitions
    ESTADOS = {
        "DESCANSO": "Idle - Waiting for wake word",
        "AGUARDANDO": "Waiting - Wake word detected, listening for prompt",
        "GRAVANDO": "Recording - Capturing user prompt",
        "PROCESSANDO": "Processing - Sending to Claude Agent",
        "RESPONDENDO": "Responding - Playing TTS response",
    }

    def __init__(self, logger: NeroLogger):
        """Initialize state machine.

        Args:
            logger: NeroLogger instance
        """
        self.logger = logger
        self.estado_atual = "DESCANSO"

    def transitar(self, novo_estado: str) -> bool:
        """Transition to new state with logging.

        Args:
            novo_estado: New state to transition to

        Returns:
            True if transition successful, False otherwise
        """
        if novo_estado not in self.ESTADOS:
            self.logger.error(f"Invalid state: {novo_estado}")
            return False

        if novo_estado == self.estado_atual:
            return True  # Already in this state

        estado_anterior = self.estado_atual
        self.estado_atual = novo_estado

        self.logger.info(f"State transition: {estado_anterior} → {novo_estado}")
        self.logger.debug(f"State meaning: {self.ESTADOS[novo_estado]}")

        return True

    @property
    def estado(self) -> str:
        """Get current state."""
        return self.estado_atual


class NeroAssistant:
    """Main NERO voice assistant orchestrator."""

    def __init__(
        self,
        deepgram_api_key: str,
        cartesia_api_key: str,
        verbose: bool = False,
    ):
        """Initialize NERO assistant.

        Args:
            deepgram_api_key: Deepgram API key for STT
            cartesia_api_key: Cartesia API key for TTS
            verbose: Enable verbose logging
        """
        # Initialize logger
        self.logger = NeroLogger(verbose=verbose)

        # Initialize state machine
        self.state_machine = MaquinaEstadosNero(self.logger)

        # Initialize modules
        self.stt_fraco = STTFraco(self.logger)
        self.stt_forte = STTForte(deepgram_api_key, self.logger)
        self.tts = TTS(cartesia_api_key, self.logger)
        self.agent = AgentHandler(self.logger)

        # Configuration
        self.wake_words = ["NERO OUVIR", "NERO"]
        self.stop_words = ["NERO ENVIAR", "ENVIAR", "ENVIAR NERO"]
        self.recording_timeout = 600  # 10 minutes

        # Control flags
        self.running = True
        self.recording_complete = asyncio.Event()

        # Register TTS callback with agent
        self.agent.set_tts_callback(self._on_agent_response)

        self.logger.debug("NERO Assistant initialized")

    async def _on_agent_response(self, texto: str) -> None:
        """Callback triggered when agent completes processing.

        Args:
            texto: Response text for TTS
        """
        self.logger.debug(f"Agent response callback: '{texto[:50]}...'")

        # Generate and play audio
        await self.tts.falar(texto, voz="ana")

        # Signal that response is complete
        self.recording_complete.set()

    def _signal_handler(self, signum, frame) -> None:
        """Handle Ctrl+C gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info("Shutdown signal received")
        self.running = False

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        if sys.platform != "win32":
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

    async def estado_descanso(self) -> bool:
        """DESCANSO state: Listen for wake word.

        Returns:
            True if wake word detected, False if shutdown requested
        """
        self.state_machine.transitar("DESCANSO")
        self.logger.listening("Say 'NERO OUVIR' to activate...")

        try:
            # Listen for wake word (blocking)
            resultado = self.stt_fraco.detectar_wake_word(
                wake_words=self.wake_words,
                timeout_segundos=None,  # Infinite timeout
            )

            if resultado["detected"]:
                self.logger.complete(f"Wake word detected: {resultado['palavra']}")
                return True
            else:
                # Check if shutdown requested
                if not self.running:
                    return False
                # Continue listening
                return True

        except Exception as e:
            self.logger.error("Error in DESCANSO state", e)
            # Stay in DESCANSO state and retry
            await asyncio.sleep(2)
            return True

    async def estado_aguardando(self) -> bool:
        """AGUARDANDO state: Wake word detected, prepare for recording.

        Returns:
            True to proceed to recording, False to return to idle
        """
        self.state_machine.transitar("AGUARDANDO")
        self.logger.recording("Starting recording session...")
        self.logger.info("Speak your prompt. Say 'NERO ENVIAR' when done.")

        # Brief pause before recording
        await asyncio.sleep(0.5)

        return True

    async def estado_gravando(self) -> str:
        """GRAVANDO state: Record user prompt with transcription.

        Returns:
            Transcribed text
        """
        self.state_machine.transitar("GRAVANDO")
        self.logger.recording("Listening for your prompt...")

        # For simplicity, record audio for a fixed duration
        # In production, this would use streaming with stop word detection
        import speech_recognition as sr

        r = sr.Recognizer()
        mic = sr.Microphone()

        try:
            with mic as source:
                # Listen for prompt (with timeout)
                self.logger.info(f"Recording... (max {self.recording_timeout}s)")
                audio = r.listen(source, timeout=self.recording_timeout, phrase_time_limit=60)

            # Transcribe using Deepgram
            audio_data = audio.get_wav_data()
            transcricao = await self.stt_forte.transcrever_audio_file(audio_data)

            if transcricao:
                self.logger.transcript(f"'{transcricao}'")
                return transcricao
            else:
                self.logger.warning("Transcription failed or empty")
                return ""

        except sr.WaitTimeoutError:
            self.logger.warning("No speech detected (timeout)")
            return ""
        except Exception as e:
            self.logger.error("Recording failed", e)
            return ""

    async def estado_processando(self, transcricao: str) -> bool:
        """PROCESSANDO state: Send transcription to Claude Agent.

        Args:
            transcricao: User's transcribed prompt

        Returns:
            True if processing successful, False otherwise
        """
        self.state_machine.transitar("PROCESSANDO")
        self.logger.agent("Sending to Claude Agent SDK...")

        if not transcricao:
            self.logger.warning("Empty transcription, skipping processing")
            return False

        try:
            # Process with agent (TTS will be triggered via callback)
            resultado = await self.agent.processar_prompt(transcricao)

            if resultado["sucesso"]:
                self.logger.complete("Agent processing completed")

                # Wait for TTS to complete (via callback)
                self.logger.info("Waiting for audio response...")
                await asyncio.wait_for(self.recording_complete.wait(), timeout=30.0)

                return True
            else:
                self.logger.error("Agent processing failed")
                return False

        except asyncio.TimeoutError:
            self.logger.warning("TTS response timeout")
            return False
        except Exception as e:
            self.logger.error("Processing failed", e)
            return False

    async def estado_respondendo(self) -> None:
        """RESPONDENDO state: Audio playback complete, return to idle."""
        self.state_machine.transitar("RESPONDENDO")
        self.logger.complete("Response complete")

        # Brief pause before returning to idle
        await asyncio.sleep(1)

        # Return to idle
        self.state_machine.transitar("DESCANSO")
        self.logger.done("Ready for next command")

    async def run(self) -> None:
        """Main execution loop."""
        self.logger.print_banner()

        # Set up signal handlers
        self._setup_signal_handlers()

        self.logger.info("NERO is ready! Say 'NERO OUVIR' to begin.")
        self.logger.info("Press Ctrl+C to exit")

        try:
            while self.running:
                # State: DESCANSO (wait for wake word)
                if not await self.estado_descanso():
                    break  # Shutdown requested

                # State: AGUARDANDO (prepare for recording)
                if not await self.estado_aguardando():
                    continue  # Return to DESCANSO

                # State: GRAVANDO (record and transcribe)
                transcricao = await self.estado_gravando()

                if not transcricao:
                    self.logger.warning("No transcription, returning to idle")
                    self.state_machine.transitar("DESCANSO")
                    continue

                # State: PROCESSANDO (send to agent)
                self.recording_complete.clear()

                if not await self.estado_processando(transcricao):
                    self.logger.warning("Processing failed, returning to idle")
                    self.state_machine.transitar("DESCANSO")
                    continue

                # State: RESPONDENDO (return to idle)
                await self.estado_respondendo()

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error("Fatal error in main loop", e)
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up resources before shutdown."""
        self.logger.info("Shutting down NERO...")

        # Close HTTP clients
        await self.stt_forte.close()
        await self.tts.close()

        # Clean up temporary files
        self.tts.limpar_arquivos_temporarios()

        self.logger.complete("NERO shutdown complete")


async def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Load environment variables
    load_dotenv()

    # Get API keys
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY", "")
    cartesia_api_key = os.getenv("CARTESIA_API_KEY", "")

    # Validate API keys
    if not deepgram_api_key or deepgram_api_key.startswith("your_"):
        print("❌ Error: DEEPGRAM_API_KEY not set in .env file")
        print("Get your key from: https://console.deepgram.com/")
        return 1

    if not cartesia_api_key or cartesia_api_key.startswith("your_"):
        print("❌ Error: CARTESIA_API_KEY not set in .env file")
        print("Get your key from: https://cartesia.ai/")
        return 1

    # Check verbose flag
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Create and run assistant
    try:
        assistant = NeroAssistant(
            deepgram_api_key=deepgram_api_key,
            cartesia_api_key=cartesia_api_key,
            verbose=verbose,
        )

        await assistant.run()
        return 0

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
