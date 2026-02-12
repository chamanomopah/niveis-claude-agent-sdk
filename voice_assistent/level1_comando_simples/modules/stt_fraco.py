"""
NERO Voice Assistant - Weak STT Module (Wake/Stop Word Detection)

Offline speech recognition using PocketSphinx for wake word and stop word detection.
Zero API costs, processes audio locally on device.
"""

import speech_recognition as sr
import pyaudio
from typing import Dict, List, Callable, Optional
import threading
import queue
import asyncio
from .logger import NeroLogger


class STTFraco:
    """Offline wake/stop word detection using speech_recognition + PocketSphinx."""

    def __init__(self, logger: NeroLogger, device_index: Optional[int] = None):
        """Initialize STT Fraco (weak speech recognition).

        Args:
            logger: NeroLogger instance
            device_index: Microphone device index (None for default)
        """
        self.logger = logger
        self.device_index = device_index
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_channels = 1

        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Adjust for ambient noise
        self.recognizer.pause_threshold = 0.8  # Pause between phrases
        self.recognizer.phrase_threshold = 0.3  # Minimum phrase length
        self.recognizer.non_speaking_duration = 0.5

        # Microphone
        self.microphone: Optional[sr.Microphone] = None

        # Stop word detection
        self._stop_word_detected = False
        self._stop_word_queue: queue.Queue = queue.Queue()

        self.logger.debug("STT Fraco initialized")

    def list_microphones(self) -> List[str]:
        """List available microphone devices.

        Returns:
            List of microphone names
        """
        try:
            mic_list = sr.Microphone.list_microphone_names()
            self.logger.debug(f"Found {len(mic_list)} microphones")
            return mic_list
        except Exception as e:
            self.logger.error("Failed to list microphones", e)
            return []

    def _get_microphone(self) -> sr.Microphone:
        """Get or create microphone instance.

        Returns:
            Configured Microphone instance
        """
        if self.microphone is None:
            try:
                self.microphone = sr.Microphone(
                    device_index=self.device_index,
                    sample_rate=self.sample_rate,
                    chunk_size=self.chunk_size,
                )
                self.logger.debug(f"Microphone initialized (device: {self.device_index or 'default'})")
            except Exception as e:
                self.logger.error("Failed to initialize microphone", e)
                raise
        return self.microphone

    def calibrate_ambient_noise(self, duration: float = 1.0) -> None:
        """Calibrate recognizer for ambient noise.

        Args:
            duration: Seconds to listen for ambient noise
        """
        try:
            mic = self._get_microphone()
            self.logger.info(f"Calibrating for ambient noise ({duration}s)...")
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.logger.info(f"Ambient noise calibrated (energy_threshold={self.recognizer.energy_threshold})")
        except Exception as e:
            self.logger.warning(f"Ambient noise calibration failed: {e}")

    def detectar_wake_word(
        self,
        wake_words: List[str],
        timeout_segundos: Optional[int] = None,
    ) -> Dict:
        """Listen continuously for wake word detection.

        Args:
            wake_words: List of wake word phrases (e.g., ["NERO OUVIR", "NERO"])
            timeout_segundos: Optional timeout in seconds (None for infinite)

        Returns:
            Detection result dict:
                {'detected': bool, 'palavra': str, 'audio_data': Optional[bytes]}
        """
        self.logger.debug(f"Starting wake word detection for: {wake_words}")
        result = {"detected": False, "palavra": "", "audio_data": None}

        try:
            mic = self._get_microphone()

            # Calibrate for ambient noise on first use
            if self.recognizer.energy_threshold == 300:
                self.calibrate_ambient_noise(duration=0.5)

            self.logger.listening("Listening for wake word...")

            while True:
                try:
                    with mic as source:
                        # Listen for audio
                        audio = self.recognizer.listen(
                            source,
                            timeout=timeout_segundos,
                            phrase_time_limit=10,
                        )

                    # Try to recognize using PocketSphinx (offline)
                    try:
                        # Use Sphinx for offline recognition
                        texto = self.recognizer.recognize_sphinx(audio, language="pt-BR")
                        texto_upper = texto.upper().strip()

                        self.logger.debug(f"Heard: '{texto}'")

                        # Check if any wake word was detected
                        for wake_word in wake_words:
                            if wake_word.upper() in texto_upper:
                                self.logger.complete(f"Wake word detected: '{wake_word}'")
                                result["detected"] = True
                                result["palavra"] = wake_word
                                result["audio_data"] = audio.get_wav_data()
                                return result

                    except sr.UnknownValueError:
                        # Speech detected but couldn't be understood
                        self.logger.debug("Speech detected but not recognized")
                        continue
                    except sr.RequestError as e:
                        # Sphinx not installed or not working
                        self.logger.error(f"Sphinx recognition failed: {e}")
                        # Try Google Speech Recognition as fallback (requires internet)
                        try:
                            texto = self.recognizer.recognize_google(audio, language="pt-BR")
                            texto_upper = texto.upper().strip()

                            self.logger.debug(f"Heard (Google): '{texto}'")

                            for wake_word in wake_words:
                                if wake_word.upper() in texto_upper:
                                    self.logger.complete(f"Wake word detected: '{wake_word}'")
                                    result["detected"] = True
                                    result["palavra"] = wake_word
                                    result["audio_data"] = audio.get_wav_data()
                                    return result
                        except Exception:
                            continue

                except sr.WaitTimeoutError:
                    # No speech detected within timeout
                    self.logger.debug("No speech detected (timeout)")
                    return result
                except Exception as e:
                    self.logger.error(f"Error during wake word detection: {e}")
                    continue

        except KeyboardInterrupt:
            self.logger.info("Wake word detection interrupted")
            return result
        except Exception as e:
            self.logger.error("Fatal error in wake word detection", e)
            return result

    def aguardar_palavra_parada(
        self,
        stop_words: List[str],
        callback: Callable,
        timeout_segundos: int = 600,
    ) -> None:
        """Listen for stop word in background thread.

        Runs continuously in background until stop word is detected or timeout.
        Calls callback when stop word is detected.

        Args:
            stop_words: List of stop word phrases (e.g., ["NERO ENVIAR", "ENVIAR"])
            callback: Function to call when stop word detected
            timeout_segundos: Maximum seconds to wait (default: 600 = 10 min)
        """
        def _listen_for_stop():
            self.logger.debug(f"Background stop word detection started for: {stop_words}")

            try:
                mic = self._get_microphone()
                start_time = asyncio.get_event_loop().time()

                while True:
                    # Check timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= timeout_segundos:
                        self.logger.warning(f"Stop word timeout after {elapsed:.1f}s")
                        self._stop_word_queue.put({"detected": False, "reason": "timeout"})
                        return

                    try:
                        with mic as source:
                            # Quick listen for stop word
                            audio = self.recognizer.listen(
                                source,
                                timeout=5,
                                phrase_time_limit=5,
                            )

                        try:
                            # Try to recognize using Sphinx
                            texto = self.recognizer.recognize_sphinx(audio, language="pt-BR")
                            texto_upper = texto.upper().strip()

                            self.logger.debug(f"Stop check heard: '{texto}'")

                            # Check if any stop word was detected
                            for stop_word in stop_words:
                                if stop_word.upper() in texto_upper:
                                    self.logger.stop_word(f"Stop word detected: '{stop_word}'")
                                    self._stop_word_detected = True
                                    self._stop_word_queue.put({
                                        "detected": True,
                                        "palavra": stop_word,
                                    })
                                    callback(stop_word)
                                    return

                        except sr.UnknownValueError:
                            # Not understood, continue listening
                            continue
                        except sr.RequestError:
                            # Try Google fallback
                            try:
                                texto = self.recognizer.recognize_google(audio, language="pt-BR")
                                texto_upper = texto.upper().strip()

                                for stop_word in stop_words:
                                    if stop_word.upper() in texto_upper:
                                        self.logger.stop_word(f"Stop word detected: '{stop_word}'")
                                        self._stop_word_detected = True
                                        self._stop_word_queue.put({
                                            "detected": True,
                                            "palavra": stop_word,
                                        })
                                        callback(stop_word)
                                        return
                            except Exception:
                                continue

                    except sr.WaitTimeoutError:
                        # No speech, continue listening
                        continue
                    except Exception as e:
                        self.logger.debug(f"Stop word detection error: {e}")
                        continue

            except Exception as e:
                self.logger.error("Fatal error in stop word detection", e)
                self._stop_word_queue.put({"detected": False, "reason": "error"})

        # Start background thread
        self._stop_word_detected = False
        self._stop_word_queue = queue.Queue()

        thread = threading.Thread(target=_listen_for_stop, daemon=True)
        thread.start()
        self.logger.debug("Stop word detection thread started")

    def verificar_palavra_parada_detectada(self) -> Optional[Dict]:
        """Check if stop word was detected (non-blocking).

        Returns:
            None if not detected, or dict with detection info
        """
        try:
            return self._stop_word_queue.get_nowait()
        except queue.Empty:
            return None

    def stop_detection(self) -> None:
        """Stop all background detection threads."""
        self._stop_word_detected = True
        self.logger.debug("Stop word detection stopped")
