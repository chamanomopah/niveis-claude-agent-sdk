# E2E Voice Tests for NERO Voice Assistant

> **End-to-end automated tests for the NERO voice assistant**
> Tests the complete flow from wake word detection to audio response output

## Test Environment

### Prerequisites
- Python 3.10+ installed
- All dependencies installed (`pip install -r requirements.txt`)
- Valid `.env` file with API keys
- Virtual audio device configured (for CI/CD testing)

### Setup
```bash
# Install test dependencies
pip install pytest-asyncio pytest-mock pydub

# Install virtual audio device (Linux)
sudo apt-get install pulseaudio-utils

# Or use sounddevice for cross-platform testing
pip install sounddevice
```

---

## Test Suite 1: Wake Word Detection

### Test 1.1: Basic Wake Word Detection "NERO OUVIR"

**User Story**: As a user, I want to activate NERO by saying "NERO OUVIR" so I can start giving voice commands.

**Preconditions**:
- NERO assistant is running
- System is in DESCANSO (idle) state
- Microphone is available

**Test Steps**:

1. **Initialize** NERO assistant in test mode
   ```python
   assistant = NeroAssistant(
       deepgram_api_key=os.getenv("DEEPGRAM_API_KEY"),
       cartesia_api_key=os.getenv("CARTESIA_API_KEY"),
       verbose=False
   )
   ```

2. **Verify initial state** is DESCANSO
   - Check `assistant.state_machine.estado == "DESCANSO"`
   - **Verify**: State is "DESCANSO"

3. **Inject audio** containing "NERO OUVIR" wake word
   - Use pre-recorded audio file: `tests/fixtures/wake_word_nero_ouvir.wav`
   - Inject directly into recognizer (bypassing microphone)

4. **Wait for state transition** (max 5 seconds)
   - Monitor state changes
   - **Verify**: State transitions to "AGUARDANDO"

5. **Verify wake word detection**
   - Check logger output for "Wake word detected: NERO OUVIR"
   - **Verify**: Wake word detection logged

**Success Criteria**:
- [x] Initial state is DESCANSO
- [x] Wake word "NERO OUVIR" is detected
- [x] State transitions to AGUARDANDO within 5 seconds
- [x] Detection is logged correctly

**Expected Output**:
```
[DESCANSO] State transition: DESCANSO → AGUARDANDO
[COMPLETE] ✅ Wake word detected: NERO OUVIR
```

---

### Test 1.2: Alternative Wake Word "NERO"

**User Story**: As a user, I want to activate NERO by simply saying "NERO" as a shorter alternative.

**Test Steps**:

1. **Initialize** NERO assistant (reset state to DESCANSO)

2. **Inject audio** containing "NERO" wake word
   - Use audio file: `tests/fixtures/wake_word_nero.wav`

3. **Wait for state transition**
   - **Verify**: State transitions to "AGUARDANDO"

**Success Criteria**:
- [x] Wake word "NERO" is detected
- [x] State transitions to AGUARDANDO

---

## Test Suite 2: Recording and Stop Word Detection

### Test 2.1: Complete Recording with Stop Word

**User Story**: As a user, I want to speak my prompt naturally and say "NERO ENVIAR" to submit it.

**Preconditions**:
- NERO is in AGUARDANDO state (wake word just detected)

**Test Steps**:

1. **Verify state** is AGUARDANDO
   - **Verify**: `assistant.state_machine.estado == "AGUARDANDO"`

2. **Inject audio** with user prompt + stop word
   - Use audio: `tests/fixtures/prompt_qual_temperatura_nero_enviar.wav`
   - Audio contains: "Qual a temperatura em São Paulo? NERO ENVIAR"

3. **Monitor state transitions**:
   - AGUARDANDO → GRAVANDO (recording starts)
   - **Verify**: State becomes "GRAVANDO"

4. **Wait for stop word detection** (max 15 seconds)
   - **Verify**: Stop word "NERO ENVIAR" is detected
   - **Verify**: State transitions to "PROCESSANDO"

5. **Verify transcription**
   - Check logger for transcript output
   - **Verify**: Transcript contains "temperatura" or "São Paulo"

**Success Criteria**:
- [x] Recording state (GRAVANDO) is entered
- [x] Stop word "NERO ENVIAR" is detected
- [x] Transcription is produced
- [x] State transitions to PROCESSANDO

**Expected Output**:
```
[GRAVANDO] 🎙️ Listening for your prompt...
[STOP_WORD] ✋ Stop word detected: 'NERO ENVIAR'
[TRANSCRIBING] 📝 Transcribing audio chunks...
[TRANSCRIPT] 💬 'qual a temperatura em são paulo'
```

---

### Test 2.2: Recording Timeout (10 minutes)

**User Story**: As a system, I want to automatically stop recording after 10 minutes if no stop word is detected.

**Test Steps**:

1. **Mock recording timeout** to 5 seconds (for faster testing)

2. **Inject audio** with prompt but NO stop word
   - Use audio: `tests/fixtures/prompt_sem_stop_word.wav`

3. **Wait for timeout**
   - **Verify**: Recording stops after timeout
   - **Verify**: Warning message logged

**Success Criteria**:
- [x] Recording stops automatically after timeout
- [x] Transcription is attempted with captured audio
- [x] Timeout is logged

---

## Test Suite 3: Claude Agent Processing

### Test 3.1: Simple Query Processing

**User Story**: As a user, I want to ask simple questions and receive answers from Claude.

**Preconditions**:
- NERO is in PROCESSANDO state
- Transcription: "Qual a capital do Brasil?"

**Test Steps**:

1. **Verify state** is PROCESSANDO
   - **Verify**: `assistant.state_machine.estado == "PROCESSANDO"`

2. **Wait for agent response** (max 30 seconds)
   - Monitor agent callback invocation
   - **Verify**: Agent processing completes successfully

3. **Verify response content**
   - Check TTS callback was triggered
   - **Verify**: Response contains "Brasília" or similar

**Success Criteria**:
- [x] Agent processing completes without errors
- [x] Response is generated
- [x] Response is contextually relevant

**Expected Output**:
```
[AGENT] 🤖 Sending to Claude Agent SDK...
[COMPLETE] ✅ Agent processing completed
[TTS] 🔈 Generating audio for response...
```

---

### Test 3.2: Code Generation Request

**User Story**: As a user, I want to request code examples and receive them via voice.

**Test Steps**:

1. **Inject audio**: "Crie uma função de soma em Python" + stop word

2. **Wait for processing**
   - **Verify**: Agent processes the request

3. **Verify response includes code**
   - Check TTS callback content
   - **Verify**: Response mentions code, Python, or function

**Success Criteria**:
- [x] Agent processes code generation request
- [x] Response includes relevant technical information

---

## Test Suite 4: Text-to-Speech Output

### Test 4.1: Portuguese TTS Generation

**User Story**: As a user, I want to hear Claude's responses spoken in natural Brazilian Portuguese.

**Preconditions**:
- Agent has completed processing
- Response text is available

**Test Steps**:

1. **Verify TTS callback is triggered**
   - Monitor `assistant._on_agent_response()` invocation
   - **Verify**: Callback receives response text

2. **Wait for TTS audio generation** (max 10 seconds)
   - Check TTS module completion
   - **Verify**: Audio file is generated

3. **Verify audio playback**
   - Check if audio was played (or would be played in non-test mode)
   - **Verify**: No playback errors

4. **Verify state transition** to RESPONDENDO → DESCANSO
   - **Verify**: Final state is "DESCANSO"

**Success Criteria**:
- [x] TTS is called with response text
- [x] Audio is generated successfully
- [x] No TTS errors
- [x] System returns to idle state

**Expected Output**:
```
[TTS] 🔈 Generating audio for response: 'A capital do Brasil é Brasília...'
[RESPONDENDO] ✅ Response complete
[DONE] 🏁 Ready for next command
```

---

## Test Suite 5: Complete End-to-End Flow

### Test 5.1: Full User Journey - Simple Query

**User Story**: As a user, I want to have a complete conversation: activate NERO, ask a question, and hear the response.

**Test Steps**:

**Phase 1: Wake Word**
1. Start NERO assistant
2. **Verify**: State is DESCANSO
3. Inject audio: "NERO OUVIR"
4. **Verify**: State → AGUARDANDO

**Phase 2: Recording**
5. Inject audio: "Que horas são?" + "NERO ENVIAR"
6. **Verify**: State → GRAVANDO → PROCESSANDO

**Phase 3: Processing**
7. Wait for agent response
8. **Verify**: Agent processes successfully

**Phase 4: Response**
9. **Verify**: TTS generates audio
10. **Verify**: State → RESPONDENDO → DESCANSO

**Success Criteria**:
- [x] All state transitions complete successfully
- [x] Transcription is accurate
- [x] Agent response is relevant
- [x] TTS audio is generated
- [x] System returns to idle state
- [x] No errors in logs

**Expected Full Flow**:
```
[DESCANSO] 🔊 Say 'NERO OUVIR' to activate...
[COMPLETE] ✅ Wake word detected: NERO OUVIR
[AGUARDANDO] 🎙️ Starting recording session...
[GRAVANDO] 🎙️ Listening for your prompt...
[STOP_WORD] ✋ Stop word detected: 'NERO ENVIAR'
[TRANSCRIBING] 📝 Transcribing 1 audio chunks...
[TRANSCRIPT] 💬 'que horas são'
[PROCESSANDO] 🤖 Sending to Claude Agent SDK...
[COMPLETE] ✅ Agent processing completed
[TTS] 🔈 Generating audio for response...
[RESPONDENDO] ✅ Response complete
[DONE] 🏁 Ready for next command
```

---

### Test 5.2: Full User Journey - Complex Request

**User Story**: As a user, I want to make a complex request (code generation) and receive a detailed response.

**Test Steps**:

1. Wake word: "NERO OUVIR"
2. Prompt: "Crie um código Python para calcular a fibonacci de 10" + "NERO ENVIAR"
3. **Verify**: Complete flow executes
4. **Verify**: Response contains Fibonacci-related content

**Success Criteria**:
- [x] Long transcription handled correctly
- [x] Complex query processed
- [x] Detailed response generated

---

## Test Suite 6: Error Handling

### Test 6.1: Empty Transcription Handling

**User Story**: As a system, I want to handle cases where transcription fails gracefully.

**Test Steps**:

1. Inject audio with silence only
2. **Verify**: Empty transcription is detected
3. **Verify**: System returns to DESCANSO state
4. **Verify**: No crash or error

**Success Criteria**:
- [x] Empty transcription handled gracefully
- [x] System returns to idle
- [x] Appropriate warning logged

---

### Test 6.2: API Error Handling

**User Story**: As a system, I want to handle API failures (Deepgram/Cartesia) gracefully.

**Test Steps**:

1. Mock API failure in Deepgram
2. Attempt transcription
3. **Verify**: Error is caught and logged
4. **Verify**: System continues running (no crash)

**Success Criteria**:
- [x] API errors are caught
- [x] Error messages are clear
- [x] System remains operational

---

## Test Suite 7: Performance Tests

### Test 7.1: Wake Word Latency

**User Story**: As a user, I want NERO to respond quickly to the wake word.

**Test Steps**:

1. Measure time from audio injection to wake word detection
2. Run 10 iterations
3. Calculate average latency

**Success Criteria**:
- [x] Average wake word detection < 2 seconds
- [x] 95th percentile < 3 seconds

---

### Test 7.2: End-to-End Response Time

**User Story**: As a user, I want to receive complete responses within a reasonable time.

**Test Steps**:

1. Measure time from wake word to TTS completion
2. Run 5 iterations with different queries
3. Calculate average response time

**Success Criteria**:
- [x] Simple queries: < 10 seconds total
- [x] Complex queries: < 20 seconds total

---

## Test Fixtures

### Audio Files Required

Create these audio files in `tests/fixtures/`:

1. `wake_word_nero_ouvir.wav` - Clear "NERO OUVIR" phrase
2. `wake_word_nero.wav` - Clear "NERO" phrase
3. `prompt_qual_temperatura_nero_enviar.wav` - "Qual a temperatura? NERO ENVIAR"
4. `prompt_sem_stop_word.wav` - Prompt without stop word
5. `prompt_codigo_fibonacci.wav` - "Crie código fibonacci NERO ENVIAR"

### Fixture Generation Script

```python
# tests/fixtures/generate_fixtures.py
"""Generate audio test fixtures using TTS APIs."""
import asyncio
from modules.tts import TTS
from modules.logger import NeroLogger

async def generate_fixtures():
    """Generate all required audio fixtures."""
    logger = NeroLogger(verbose=True)
    tts = TTS(os.getenv("CARTESIA_API_KEY"), logger)

    fixtures = {
        "wake_word_nero_ouvir.wav": "NERO OUVIR",
        "wake_word_nero.wav": "NERO",
        "prompt_qual_temperatura_nero_enviar.wav": "Qual a temperatura em São Paulo? NERO ENVIAR",
        "prompt_sem_stop_word.wav": "Como está o tempo hoje",
        "prompt_codigo_fibonacci.wav": "Crie um código Python para calcular fibonacci de 10. NERO ENVIAR",
    }

    for filename, text in fixtures.items():
        await tts.falar(text, voz="ana", output_file=f"tests/fixtures/{filename}")
        logger.complete(f"Generated: {filename}")

asyncio.run(generate_fixtures())
```

---

## Test Implementation

### Test Automation Framework

```python
# tests/e2e/test_voice_e2e.py
"""End-to-end voice tests for NERO assistant."""
import pytest
import asyncio
import os
import time
from unittest.mock import Mock, patch, MagicMock
from nero_assistant import NeroAssistant, MaquinaEstadosNero
from modules.logger import NeroLogger

@pytest.mark.asyncio
class TestE2EVoiceFlow:
    """End-to-end tests for complete voice flow."""

    async def test_full_wake_word_to_tts_flow(self):
        """Test complete flow from wake word to TTS output."""
        # Setup
        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        cartesia_key = os.getenv("CARTESIA_API_KEY")

        assistant = NeroAssistant(
            deepgram_api_key=deepgram_key,
            cartesia_api_key=cartesia_key,
            verbose=False
        )

        # Test: Full flow
        # 1. Initial state
        assert assistant.state_machine.estado == "DESCANSO"

        # 2. Simulate wake word (mock the microphone input)
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {
                "detected": True,
                "palavra": "NERO OUVIR",
                "audio_data": b"fake_audio"
            }

            # Execute wake word detection
            result = await assistant.estado_descanso()
            assert result is True
            assert assistant.state_machine.estado == "AGUARDANDO"

        # 3. Simulate recording with stop word
        with patch.object(assistant.stt_fraco, 'aguardar_palavra_parada'):
            # Mock transcription
            with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
                mock_transc.return_value = "qual a capital do brasil"

                # Mock agent processing
                with patch.object(assistant.agent, 'processar_prompt') as mock_agent:
                    mock_agent.return_value = {"sucesso": True}

                    # Run recording state
                    transcricao = await assistant.estado_gravando()
                    assert transcricao == "qual a capital do brasil"

        # 4. Process with agent
        assistant.recording_complete.clear()
        success = await assistant.estado_processando("qual a capital do brasil")
        assert success is True

        # 5. Verify final state
        await assistant.estado_respondendo()
        assert assistant.state_machine.estado == "DESCANSO"

        # Cleanup
        await assistant.cleanup()

    async def test_wake_word_detection_timeout(self):
        """Test wake word detection with timeout."""
        assistant = NeroAssistant(
            deepgram_api_key=os.getenv("DEEPGRAM_API_KEY"),
            cartesia_api_key=os.getenv("CARTESIA_API_KEY"),
            verbose=False
        )

        # Mock timeout scenario
        with patch.object(assistant.stt_fraco, 'detectar_wake_word') as mock_wake:
            mock_wake.return_value = {"detected": False, "palavra": "", "audio_data": None}

            result = await assistant.estado_descanso()
            assert result is True  # Should continue listening

        await assistant.cleanup()

    async def test_empty_transcription_handling(self):
        """Test handling of empty transcription."""
        assistant = NeroAssistant(
            deepgram_api_key=os.getenv("DEEPGRAM_API_KEY"),
            cartesia_api_key=os.getenv("CARTESIA_API_KEY"),
            verbose=False
        )

        # Mock empty transcription
        with patch.object(assistant.stt_forte, 'transcrever_audio_file') as mock_transc:
            mock_transc.return_value = ""

            transcricao = await assistant.estado_gravando()
            assert transcricao == ""

        # Verify system returns to idle
        assert assistant.state_machine.estado == "DESCANSO"

        await assistant.cleanup()

    async def test_state_transitions(self):
        """Test all state transitions work correctly."""
        assistant = NeroAssistant(
            deepgram_api_key=os.getenv("DEEPGRAM_API_KEY"),
            cartesia_api_key=os.getenv("CARTESIA_API_KEY"),
            verbose=False
        )

        # Test state machine
        assert assistant.state_machine.estado == "DESCANSO"
        assistant.state_machine.transitar("AGUARDANDO")
        assert assistant.state_machine.estado == "AGUARDANDO"
        assistant.state_machine.transitar("GRAVANDO")
        assert assistant.state_machine.estado == "GRAVANDO"
        assistant.state_machine.transitar("PROCESSANDO")
        assert assistant.state_machine.estado == "PROCESSANDO"
        assistant.state_machine.transitar("RESPONDENDO")
        assert assistant.state_machine.estado == "RESPONDENDO"
        assistant.state_machine.transitar("DESCANSO")
        assert assistant.state_machine.estado == "DESCANSO"

        await assistant.cleanup()
```

---

## Running the Tests

### Run All Tests
```bash
cd voice_assistent/level1_comando_simples
pytest tests/e2e/test_voice_e2e.py -v
```

### Run Specific Test Suite
```bash
pytest tests/e2e/test_voice_e2e.py::TestE2EVoiceFlow::test_full_wake_word_to_tts_flow -v
```

### Run with Coverage
```bash
pytest tests/e2e/test_voice_e2e.py --cov=modules --cov-report=html
```

### Run in Verbose Mode
```bash
pytest tests/e2e/test_voice_e2e.py -v -s
```

---

## Test Output Format

### Success Output
```json
{
  "test_name": "Full E2E Voice Flow - Wake Word to TTS",
  "status": "passed",
  "screenshots": [],
  "error": null,
  "metrics": {
    "wake_word_latency_ms": 1250,
    "transcription_time_ms": 1800,
    "agent_processing_time_ms": 3500,
    "tts_generation_time_ms": 4200,
    "total_time_ms": 10750
  }
}
```

### Failure Output
```json
{
  "test_name": "Full E2E Voice Flow - Wake Word to TTS",
  "status": "failed",
  "screenshots": [],
  "error": "Step 4 failed: State transition to PROCESSANDO did not occur within 30 seconds",
  "metrics": {
    "wake_word_latency_ms": 1250,
    "transcription_time_ms": null,
    "agent_processing_time_ms": null,
    "tts_generation_time_ms": null,
    "total_time_ms": null
  }
}
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/e2e-voice-tests.yml
name: E2E Voice Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          cd voice_assistent/level1_comando_simples
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-mock

      - name: Configure API keys
        env:
          DEEPGRAM_API_KEY: ${{ secrets.DEEPGRAM_API_KEY }}
          CARTESIA_API_KEY: ${{ secrets.CARTESIA_API_KEY }}
        run: |
          cd voice_assistent/level1_comando_simples
          echo "DEEPGRAM_API_KEY=$DEEPGRAM_API_KEY" > .env
          echo "CARTESIA_API_KEY=$CARTESIA_API_KEY" >> .env

      - name: Run E2E tests
        run: |
          cd voice_assistent/level1_comando_simples
          pytest tests/e2e/test_voice_e2e.py -v --tb=short

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: voice_assistent/level1_comando_simples/test-results/
```

---

## Success Metrics

### Test Coverage Goals
- Wake word detection: 100%
- Stop word detection: 100%
- State transitions: 100%
- Error handling: 95%+
- API integration: 90%+

### Performance Benchmarks
- Wake word latency: < 2s (p95)
- End-to-end simple query: < 10s
- End-to-end complex query: < 20s
- Memory usage: < 500MB during processing

---

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "Microphone not found"
**Solution**: Tests should mock microphone input. Ensure mocks are properly configured.

**Issue**: API timeout errors
**Solution**: Check API keys are valid and have sufficient quota.

**Issue**: State transition failures
**Solution**: Check state machine logic and ensure all states are properly defined.

---

## Changelog

- **2024-02-12**: Initial E2E test specification created
- Future: Add audio injection tests
- Future: Add performance benchmarks
- Future: Add multi-language tests
