# NERO Voice Assistant - Test Suite

End-to-end automated tests for the NERO voice assistant, testing the complete flow from wake word detection to audio response output.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                     # Pytest configuration
├── fixtures/                       # Audio fixtures for testing
│   ├── generate_fixtures.py        # Script to generate audio files
│   ├── wake_word_nero_ouvir.wav   # "NERO OUVIR" wake word
│   ├── wake_word_nero.wav         # "NERO" alternative wake word
│   ├── prompt_que_horas_nero_enviar.wav  # Simple query
│   └── ...                       # More fixtures
└── e2e/                          # End-to-end tests
    ├── __init__.py
    ├── test_voice_e2e.py          # Main E2E test implementation
    └── e2e_voice_tests.md        # Test specification document
```

## Quick Start

### 1. Install Test Dependencies

```bash
# From the project root
cd voice_assistent/level1_comando_simples

# Install test dependencies
pip install pytest pytest-asyncio pytest-mock
```

### 2. Generate Audio Fixtures

Generate the audio files used for testing:

```bash
python tests/fixtures/generate_fixtures.py
```

This requires a valid `CARTESIA_API_KEY` in your `.env` file.

### 3. Run Tests

Run all tests:
```bash
pytest tests/e2e/test_voice_e2e.py -v
```

Run specific test suites:
```bash
# Wake word tests only
pytest tests/e2e/test_voice_e2e.py::TestWakeWordDetection -v

# Recording tests only
pytest tests/e2e/test_voice_e2e.py::TestRecordingAndStopWord -v

# Complete E2E flow test
pytest tests/e2e/test_voice_e2e.py::TestCompleteE2EFlow::test_full_wake_word_to_tts_flow_simple_query -v -s
```

Run with coverage:
```bash
pytest tests/e2e/test_voice_e2e.py --cov=modules --cov-report=html
```

## Test Suites

### 1. Wake Word Detection (`TestWakeWordDetection`)
- Initial state verification
- "NERO OUVIR" detection
- "NERO" alternative detection
- Timeout handling
- State transitions

### 2. Recording & Stop Word (`TestRecordingAndStopWord`)
- Recording with stop word
- Recording timeout (10 minutes)
- Empty transcription handling

### 3. Agent Processing (`TestAgentProcessing`)
- Successful processing
- Empty transcription handling
- Timeout handling

### 4. Text-to-Speech (`TestTextToSpeech`)
- TTS callback triggering
- RESPONDENDO state transitions

### 5. Complete E2E Flow (`TestCompleteE2EFlow`)
- **Full simple query journey** (main test)
- **Complex request journey**

### 6. Error Handling (`TestErrorHandling`)
- Empty transcription handling
- Agent failure handling
- Exception handling

### 7. State Machine (`TestStateMachine`)
- All states defined
- Invalid transitions
- Complete state cycle

### 8. Performance (`TestPerformance`)
- Wake word latency
- End-to-end latency

## Test Output Example

```
tests/e2e/test_voice_e2e.py::TestWakeWordDetection::test_initial_state_is_descanso PASSED
tests/e2e/test_voice_e2e.py::TestWakeWordDetection::test_wake_word_nero_ouvir_detection PASSED
tests/e2e/test_voice_e2e.py::TestCompleteE2EFlow::test_full_wake_word_to_tts_flow_simple_query PASSED

📊 E2E Test Metrics:
  wake_word_latency_ms: 45ms
  recording_time_ms: 120ms
  transcription_time_ms: 0ms
  agent_processing_time_ms: 15ms
  tts_generation_time_ms: 500ms
  total_time_ms: 680ms

======================== 15 passed in 2.34s ========================
```

## Mocking Strategy

Tests use mocks to avoid requiring real microphone input during CI/CD:

1. **Microphone Input**: Mocked using `unittest.mock.patch`
2. **STT (Speech-to-Text)**: Mocked with predefined transcriptions
3. **TTS (Text-to-Speech)**: Mocked to avoid audio playback during tests
4. **Agent Processing**: Mocked for faster, deterministic tests

This allows tests to run:
- Without hardware (microphone/speakers)
- Quickly (< 5 seconds for full suite)
- Deterministically (no variability from audio recognition)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Voice Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-mock pytest-cov

      - name: Run E2E tests
        env:
          DEEPGRAM_API_KEY: ${{ secrets.DEEPGRAM_API_KEY }}
          CARTESIA_API_KEY: ${{ secrets.CARTESIA_API_KEY }}
        run: pytest tests/e2e/test_voice_e2e.py -v --cov=modules

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Tests fail with "ModuleNotFoundError"

```bash
# Make sure you're in the correct directory
cd voice_assistent/level1_comando_simples

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock
```

### Tests fail with API key errors

Create `.env` file with valid keys:
```bash
cp .env.example .env
# Edit .env and add your keys
```

### Audio fixtures not found

Generate fixtures first:
```bash
python tests/fixtures/generate_fixtures.py
```

### Tests timeout

Increase timeout in `tests/conftest.py`:
```python
@pytest.fixture(scope="session")
def test_config():
    return {"timeout": 60}  # Increase from 30
```

## Performance Benchmarks

Expected performance with mocked inputs:

| Metric | Target | Actual |
|--------|--------|--------|
| Wake word latency | < 100ms | ~50ms |
| Recording time | < 200ms | ~120ms |
| Agent processing | < 100ms | ~15ms (mocked) |
| TTS generation | < 500ms | ~500ms |
| **Total E2E (simple)** | < 1000ms | ~700ms |

For real audio (not mocked):
- Wake word: < 2s
- Simple query E2E: < 10s
- Complex query E2E: < 20s

## Contributing

When adding new tests:

1. Follow the existing pattern: `async def test_*`
2. Add appropriate markers: `@pytest.mark.asyncio`
3. Mock external dependencies (API, microphone)
4. Verify state transitions
5. Test both success and failure cases
6. Add fixtures if needed

## License

MIT License - See main project LICENSE
