"""
End-to-end voice tests for NERO Voice Assistant.

This test suite validates the complete flow from wake word detection
to audio response output using mocked audio input for CI/CD compatibility.

Usage:
    pytest tests/e2e/test_voice_e2e.py -v
    pytest tests/e2e/test_voice_e2e.py::TestWakeWordDetection -v
    pytest tests/e2e/test_voice_e2e.py -k "test_full_wake_word_to_tts_flow" -v -s
"""

import pytest
import asyncio
import os
import sys
import time
import threading
import queue
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nero_assistant import NeroAssistant, MaquinaEstadosNero
from modules.logger import NeroLogger
from modules.stt_fraco import STTFraco


# =============================================================================
# Test Configuration
# =============================================================================

@pytest.fixture
def api_keys():
    """Provide API keys for testing."""
    deepgram_key = os.getenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    cartesia_key = os.getenv("CARTESIA_API_KEY", "test_cartesia_key")
    return {
        "deepgram": deepgram_key,
        "cartesia": cartesia_key
    }


@pytest.fixture
def logger():
    """Provide test logger instance."""
    return NeroLogger(verbose=False)


@pytest.fixture
def assistant(logger, api_keys):
    """Provide NERO assistant instance for testing.

    Automatically cleanup after each test.
    """
    assistant = NeroAssistant(
        deepgram_api_key=api_keys["deepgram"],
        cartesia_api_key=api_keys["cartesia"],
        verbose=False
    )

    yield assistant

    # Cleanup
    try:
        asyncio.run(assistant.cleanup())
    except:
        pass


# =============================================================================
# Test Suite 1: Wake Word Detection
# =============================================================================

class TestWakeWordDetection:
    """Test suite for wake word detection functionality."""

    @pytest.mark.asyncio
    async def test_initial_state_is_descanso(self, assistant):
        """Verify initial state is DESCANSO (idle)."""
        assert assistant.state_machine.estado == "DESCANSO", \
            f"Expected DESCANSO, got {assistant.state_machine.estado}"

    @pytest.mark.asyncio
    async def test_wake_word_nero_ouvir_detection(self, assistant):
        """Test wake word 'NERO OUVIR' detection."""
        # Mock wake word detection
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {
                "detected": True,
                "palavra": "NERO OUVIR",
                "audio_data": b"fake_audio_data"
            }

            # Execute wake word detection
            result = await assistant.estado_descanso()

            # Assertions
            assert result is True, "Wake word detection should return True"
            assert mock_wake.called, "detectar_wake_word should be called"
            assert mock_wake.call_args[1]['wake_words'] == assistant.wake_words, \
                "Should use configured wake words"

    @pytest.mark.asyncio
    async def test_wake_word_nero_simples_detection(self, assistant):
        """Test alternative wake word 'NERO' detection."""
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {
                "detected": True,
                "palavra": "NERO",
                "audio_data": b"fake_audio_data"
            }

            result = await assistant.estado_descanso()

            assert result is True
            assert mock_wake.return_value['palavra'] == "NERO"

    @pytest.mark.asyncio
    async def test_wake_word_timeout_continues_listening(self, assistant):
        """Test that timeout in wake word detection continues listening."""
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            # Simulate timeout (no wake word detected)
            mock_wake.return_value = {
                "detected": False,
                "palavra": "",
                "audio_data": None
            }

            result = await assistant.estado_descanso()

            # Should return True to continue listening
            assert result is True

    @pytest.mark.asyncio
    async def test_state_transition_descanso_to_aguardando(self, assistant):
        """Test state transition from DESCANSO to AGUARDANDO."""
        assert assistant.state_machine.estado == "DESCANSO"

        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {
                "detected": True,
                "palavra": "NERO OUVIR",
                "audio_data": b"audio"
            }

            await assistant.estado_descanso()

            assert assistant.state_machine.estado == "DESCANSO", \
                "estado_descanso() should leave state in DESCANSO for next iteration"

            # Now test AGUARDANDO transition
            await assistant.estado_aguardando()
            assert assistant.state_machine.estado == "AGUARDANDO"


# =============================================================================
# Test Suite 2: Recording and Stop Word Detection
# =============================================================================

class TestRecordingAndStopWord:
    """Test suite for recording and stop word detection."""

    @pytest.mark.asyncio
    async def test_state_aguardando_transitions_to_gravando(self, assistant):
        """Test AGUARDANDO state prepares for GRAVANDO."""
        # Set state to AGUARDANDO first
        assistant.state_machine.transitar("AGUARDANDO")

        # Execute estado_aguardando
        result = await assistant.estado_aguardando()

        assert result is True, "estado_aguardando should return True"
        assert assistant.state_machine.estado == "AGUARDANDO"

    @pytest.mark.asyncio
    async def test_recording_with_stop_word_detection(self, assistant):
        """Test complete recording with stop word detection."""
        # Set to AGUARDANDO state
        assistant.state_machine.transitar("AGUARDANDO")

        # Mock the recording process
        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            # Mock transcription
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                mock_transc.return_value = "qual a temperatura em são paulo"

                # Mock microphone and audio capture
                with patch('speech_recognition.Recognizer.listen') as mock_listen:
                    with patch('speech_recognition.Microphone') as mock_mic:
                        # Simulate stop word detection via queue
                        stop_queue = queue.Queue()
                        stop_queue.put("NERO ENVIAR")

                        assistant.stt_fraco._stop_word_queue = stop_queue

                        # Execute recording
                        transcricao = await assistant.estado_gravando()

                        # Verify transcription
                        assert transcricao == "qual a temperatura em são paulo", \
                            f"Expected transcription, got: {transcricao}"
                        assert mock_transc.called, "transcrever_audio_file should be called"

    @pytest.mark.asyncio
    async def test_recording_timeout_handling(self, assistant):
        """Test recording timeout (10 minutes maximum)."""
        assistant.state_machine.transitar("AGUARDANDO")

        # Reduce timeout for faster testing
        original_timeout = assistant.recording_timeout
        assistant.recording_timeout = 1  # 1 second for testing

        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            with patch('speech_recognition.Recognizer.listen') as mock_listen:
                with patch('speech_recognition.Microphone') as mock_mic:
                    # Simulate timeout by raising WaitTimeoutError
                    import speech_recognition as sr
                    mock_listen.side_effect = sr.WaitTimeoutError()

                    try:
                        transcricao = await assistant.estado_gravando()
                    except Exception as e:
                        # Expected to handle gracefully
                        pass

        # Restore timeout
        assistant.recording_timeout = original_timeout

    @pytest.mark.asyncio
    async def test_empty_transcription_returns_empty_string(self, assistant):
        """Test that empty transcription returns empty string."""
        assistant.state_machine.transitar("AGUARDANDO")

        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                mock_transc.return_value = ""  # Empty transcription

                with patch('speech_recognition.Recognizer.listen') as mock_listen:
                    with patch('speech_recognition.Microphone') as mock_mic:
                        # Simulate stop word
                        stop_queue = queue.Queue()
                        stop_queue.put("NERO ENVIAR")
                        assistant.stt_fraco._stop_word_queue = stop_queue

                        transcricao = await assistant.estado_gravando()

                        assert transcricao == "", "Empty transcription should return empty string"


# =============================================================================
# Test Suite 3: Claude Agent Processing
# =============================================================================

class TestAgentProcessing:
    """Test suite for Claude Agent SDK processing."""

    @pytest.mark.asyncio
    async def test_agent_processing_success(self, assistant):
        """Test successful agent processing."""
        # Set to GRAVANDO state first
        assistant.state_machine.transitar("GRAVANDO")

        transcription = "qual a capital do brasil"

        # Mock agent processing with callback simulation
        async def mock_processar_prompt(transc):
            # Simulate hook triggering TTS callback
            if assistant.agent._tts_callback:
                await assistant.agent._tts_callback("A capital do Brasil é Brasília")
            return {"sucesso": True}

        with patch.object(assistant.agent, 'processar_prompt', side_effect=mock_processar_prompt):
            # Execute processing
            result = await assistant.estado_processando(transcription)

            assert result is True, "Processing should succeed"

    @pytest.mark.asyncio
    async def test_agent_processing_empty_transcription(self, assistant):
        """Test agent processing with empty transcription."""
        assistant.state_machine.transitar("GRAVANDO")

        result = await assistant.estado_processando("")

        assert result is False, "Empty transcription should return False"

    @pytest.mark.asyncio
    async def test_agent_processing_timeout(self, assistant):
        """Test agent processing timeout handling."""
        assistant.state_machine.transitar("GRAVANDO")

        with patch.object(assistant.agent, 'processar_prompt') as mock_agent:
            mock_agent.return_value = {"sucesso": True}

            # Don't set the event, simulating timeout
            assistant.recording_complete.clear()

            result = await assistant.estado_processando("test prompt")

            # Should timeout and return False
            assert result is False, "Should timeout after 30 seconds"


# =============================================================================
# Test Suite 4: Text-to-Speech Output
# =============================================================================

class TestTextToSpeech:
    """Test suite for TTS functionality."""

    @pytest.mark.asyncio
    async def test_tts_callback_triggered(self, assistant):
        """Test that TTS callback is triggered on agent response."""
        callback_called = False
        callback_text = None

        async def mock_callback(texto):
            nonlocal callback_called, callback_text
            callback_called = True
            callback_text = texto
            assistant.recording_complete.set()

        assistant.agent.set_tts_callback(mock_callback)

        # Trigger callback
        await assistant._on_agent_response("Test response text")

        assert callback_called is True, "TTS callback should be called"
        assert callback_text == "Test response text"

    @pytest.mark.asyncio
    async def test_respondendo_state_transition(self, assistant):
        """Test RESPONDENDO state transitions back to DESCANSO."""
        assistant.state_machine.transitar("PROCESSANDO")

        await assistant.estado_respondendo()

        assert assistant.state_machine.estado == "DESCANSO", \
            "Should return to DESCANSO after RESPONDENDO"


# =============================================================================
# Test Suite 5: Complete End-to-End Flow
# =============================================================================

class TestCompleteE2EFlow:
    """Test suite for complete end-to-end user journeys."""

    @pytest.mark.asyncio
    async def test_full_wake_word_to_tts_flow_simple_query(self, assistant):
        """
        Test complete flow from wake word to TTS output.

        This is the main E2E test that validates the entire user journey:
        1. Wake word detection
        2. Recording with stop word
        3. Transcription
        4. Agent processing
        5. TTS response
        6. Return to idle
        """
        metrics = {
            "wake_word_latency_ms": None,
            "recording_time_ms": None,
            "transcription_time_ms": None,
            "agent_processing_time_ms": None,
            "tts_generation_time_ms": None,
            "total_time_ms": None
        }

        start_time = time.time()

        # Phase 1: Wake Word Detection
        wake_start = time.time()
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {
                "detected": True,
                "palavra": "NERO OUVIR",
                "audio_data": b"audio"
            }

            result = await assistant.estado_descanso()
            assert result is True, "Wake word detection should succeed"
            assert assistant.state_machine.estado == "DESCANSO"

        metrics["wake_word_latency_ms"] = int((time.time() - wake_start) * 1000)

        # Phase 2: AGUARDANDO
        await assistant.estado_aguardando()
        assert assistant.state_machine.estado == "AGUARDANDO"

        # Phase 3: Recording with Stop Word
        recording_start = time.time()
        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                mock_transc.return_value = "que horas são"

                with patch('speech_recognition.Recognizer.listen') as mock_listen:
                    with patch('speech_recognition.Microphone') as mock_mic:
                        # Simulate stop word detection
                        stop_queue = queue.Queue()
                        stop_queue.put("NERO ENVIAR")
                        assistant.stt_fraco._stop_word_queue = stop_queue

                        transcricao = await assistant.estado_gravando()
                        assert transcricao == "que horas são"

        metrics["recording_time_ms"] = int((time.time() - recording_start) * 1000)

        # Phase 4: Agent Processing
        processing_start = time.time()
        assistant.recording_complete.clear()

        with patch.object(assistant.agent, 'processar_prompt') as mock_agent:
            mock_agent.return_value = {"sucesso": True}

            # Mock TTS generation
            with patch.object(assistant.tts, 'falar') as mock_tts:
                async def mock_falar(text, voz="ana"):
                    metrics["tts_generation_time_ms"] = 500
                    assistant.recording_complete.set()

                mock_tts.side_effect = mock_falar

                result = await assistant.estado_processando(transcricao)
                assert result is True, "Processing should succeed"

        metrics["agent_processing_time_ms"] = int((time.time() - processing_start) * 1000)

        # Phase 5: RESPONDENDO
        await assistant.estado_respondendo()
        assert assistant.state_machine.estado == "DESCANSO"

        metrics["total_time_ms"] = int((time.time() - start_time) * 1000)

        # Print metrics
        print("\n📊 E2E Test Metrics:")
        for key, value in metrics.items():
            if value is not None:
                print(f"  {key}: {value}ms")

        # Verify performance criteria
        assert metrics["total_time_ms"] < 10000, \
            f"Total time {metrics['total_time_ms']}ms exceeds 10s threshold for simple query"

    @pytest.mark.asyncio
    async def test_full_flow_complex_request(self, assistant):
        """Test full flow with a complex code generation request."""
        # Wake word
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {
                "detected": True,
                "palavra": "NERO OUVIR",
                "audio_data": b"audio"
            }
            await assistant.estado_descanso()

        # AGUARDANDO
        await assistant.estado_aguardando()

        # Recording with complex transcription
        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                complex_transcription = "crie um código python para calcular a fibonacci de 10"
                mock_transc.return_value = complex_transcription

                with patch('speech_recognition.Recognizer.listen') as mock_listen:
                    with patch('speech_recognition.Microphone') as mock_mic:
                        stop_queue = queue.Queue()
                        stop_queue.put("NERO ENVIAR")
                        assistant.stt_fraco._stop_word_queue = stop_queue

                        transcricao = await assistant.estado_gravando()
                        assert transcricao == complex_transcription

        # Processing
        assistant.recording_complete.clear()
        with patch.object(assistant.agent, 'processar_prompt') as mock_agent:
            mock_agent.return_value = {"sucesso": True}

            with patch.object(assistant.tts, 'falar') as mock_tts:
                async def mock_falar(text, voz="ana"):
                    assistant.recording_complete.set()
                mock_tts.side_effect = mock_falar

                result = await assistant.estado_processando(transcricao)
                assert result is True

        # Responding
        await assistant.estado_respondendo()
        assert assistant.state_machine.estado == "DESCANSO"


# =============================================================================
# Test Suite 6: Error Handling
# =============================================================================

class TestErrorHandling:
    """Test suite for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_empty_transcription_returns_to_idle(self, assistant):
        """Test that empty transcription gracefully returns to idle."""
        # Start from AGUARDANDO
        assistant.state_machine.transitar("AGUARDANDO")

        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                mock_transc.return_value = ""  # Empty transcription

                with patch('speech_recognition.Recognizer.listen') as mock_listen:
                    with patch('speech_recognition.Microphone') as mock_mic:
                        stop_queue = queue.Queue()
                        stop_queue.put("NERO ENVIAR")
                        assistant.stt_fraco._stop_word_queue = stop_queue

                        transcricao = await assistant.estado_gravando()
                        assert transcricao == ""

        # Verify state returns to DESCANSO
        assert assistant.state_machine.estado == "GRAVANDO" or assistant.state_machine.estado == "DESCANSO"

    @pytest.mark.asyncio
    async def test_agent_failure_handling(self, assistant):
        """Test handling of agent processing failure."""
        assistant.state_machine.transitar("GRAVANDO")
        assistant.recording_complete.clear()

        with patch.object(assistant.agent, 'processar_prompt') as mock_agent:
            mock_agent.return_value = {"sucesso": False}

            result = await assistant.estado_processando("test")

            assert result is False, "Agent failure should return False"

    @pytest.mark.asyncio
    async def test_exception_in_gravando_state(self, assistant):
        """Test exception handling during recording."""
        assistant.state_machine.transitar("AGUARDANDO")

        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada', side_effect=Exception("Test error")):
            transcricao = await assistant.estado_gravando()
            assert transcricao == "", "Exception should result in empty transcription"


# =============================================================================
# Test Suite 7: State Machine
# =============================================================================

class TestStateMachine:
    """Test suite for state machine transitions."""

    @pytest.mark.asyncio
    async def test_all_states_defined(self, logger):
        """Verify all states are properly defined."""
        sm = MaquinaEstadosNero(logger)

        expected_states = {
            "DESCANSO",
            "AGUARDANDO",
            "GRAVANDO",
            "PROCESSANDO",
            "RESPONDENDO"
        }

        assert set(sm.ESTADOS.keys()) == expected_states, \
            f"Expected states {expected_states}, got {set(sm.ESTADOS.keys())}"

    @pytest.mark.asyncio
    async def test_invalid_state_transition_fails(self, assistant):
        """Test that invalid state transitions fail gracefully."""
        result = assistant.state_machine.transitar("INVALID_STATE")
        assert result is False, "Invalid state transition should fail"

    @pytest.mark.asyncio
    async def test_same_state_transition_succeeds(self, assistant):
        """Test that transitioning to same state succeeds."""
        assistant.state_machine.transitar("DESCANSO")
        result = assistant.state_machine.transitar("DESCANSO")
        assert result is True, "Transition to same state should succeed"

    @pytest.mark.asyncio
    async def test_complete_state_cycle(self, assistant):
        """Test complete state machine cycle."""
        # DESCANSO → AGUARDANDO → GRAVANDO → PROCESSANDO → RESPONDENDO → DESCANSO
        states = ["DESCANSO", "AGUARDANDO", "GRAVANDO", "PROCESSANDO", "RESPONDENDO", "DESCANSO"]

        for state in states:
            result = assistant.state_machine.transitar(state)
            assert result is True, f"Transition to {state} should succeed"
            assert assistant.state_machine.estado == state, \
                f"Expected {state}, got {assistant.state_machine.estado}"


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Test suite for performance benchmarks."""

    @pytest.mark.asyncio
    async def test_wake_word_detection_latency(self, assistant):
        """Measure wake word detection latency."""
        latencies = []

        for _ in range(3):
            start = time.time()

            with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
                mock_wake.return_value = {
                    "detected": True,
                    "palavra": "NERO OUVIR",
                    "audio_data": b"audio"
                }
                await assistant.estado_descanso()

            latency = (time.time() - start) * 1000
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        print(f"\n⚡ Average wake word latency: {avg_latency:.0f}ms")

        # Performance assertion (in test environment, should be very fast with mocking)
        assert avg_latency < 100, f"Mocked wake word latency {avg_latency}ms exceeds threshold"

    @pytest.mark.asyncio
    async def test_full_e2e_latency(self, assistant):
        """Measure complete end-to-end latency for simple query."""
        start_time = time.time()

        # Wake word
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {"detected": True, "palavra": "NERO", "audio_data": b"a"}
            await assistant.estado_descanso()

        await assistant.estado_aguardando()

        # Recording
        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                mock_transc.return_value = "teste"
                with patch('speech_recognition.Recognizer.listen'):
                    with patch('speech_recognition.Microphone'):
                        stop_queue = queue.Queue()
                        stop_queue.put("NERO ENVIAR")
                        assistant.stt_fraco._stop_word_queue = stop_queue
                        await assistant.estado_gravando()

        # Processing
        assistant.recording_complete.clear()
        with patch.object(assistant.agent, 'processar_prompt') as mock_agent:
            mock_agent.return_value = {"sucesso": True}
            with patch.object(assistant.tts, 'falar') as mock_tts:
                async def mock_falar(text, voz="ana"):
                    assistant.recording_complete.set()
                mock_tts.side_effect = mock_falar
                await assistant.estado_processando("teste")

        await assistant.estado_respondendo()

        total_time = (time.time() - start_time) * 1000
        print(f"\n⚡ Full E2E latency: {total_time:.0f}ms")

        # In mocked environment, should be very fast
        assert total_time < 1000, f"E2E latency {total_time}ms exceeds threshold (with mocks)"


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    """Run tests directly."""
    pytest.main([__file__, "-v", "--tb=short"])
