# Plan: NERO - Voice Assistant with Claude Agent SDK (Level 1)

## Task Description
Build a complete voice-controlled AI assistant system called NERO using Claude Agent SDK. The system will feature:
- **Always-on wake word detection** ("NERO OUVIR") using offline speech recognition
- **High-quality transcription** using Deepgram API for user prompts
- **Stop word detection** ("NERO ENVIAR") to trigger prompt submission
- **Claude Agent SDK integration** for processing requests and executing tasks
- **Text-to-Speech responses** using Cartesia API with Brazilian Portuguese voice
- **Comprehensive logging** with rich terminal output for troubleshooting

The system must be 100% voice-controlled from wake word to audio response, with a 10-minute timeout between wake and stop words.

## Objective

Create a fully functional voice assistant pipeline that:
1. Listens for wake word "NERO OUVIR" using lightweight offline STT
2. Activates Deepgram transcription when wake word is detected
3. Records user prompt until stop word "NERO ENVIAR" or 10-minute timeout
4. Sends transcribed prompt to Claude Agent SDK for processing
5. Generates audio response via Cartesia TTS when agent completes
6. Returns to wake word listening state
7. Logs all stages with color-coded rich terminal output

## Problem Statement

Current voice assistants require:
- Complex setup with multiple tools
- Online-only wake word detection (costly and latency)
- Manual transcription/TTS integration
- Poor visibility into pipeline stages

NERO solves these by providing:
- **Zero-cost wake word detection** using offline speech_recognition with PocketSphinx
- **Hybrid STT approach**: Lightweight offline for wake/stop words, high-quality online for prompts
- **Seamless agent integration** using Claude Agent SDK hooks
- **Rich logging** for development and troubleshooting

## Solution Approach

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Main Loop (asyncio)                                      │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ State Machine: IDLE → LISTENING → RECORDING →     │    │
│  │                   PROCESSING → RESPONDING → IDLE     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                               │
│  Modules:                                                    │
│  ├─ stt_fraco.py     - Wake/stop word detection    │
│  ├─ stt_forte.py     - Deepgram transcription          │
│  ├─ agent_handler.py   - Claude SDK orchestration     │
│  ├─ tts.py            - Cartesia text-to-speech       │
│  └─ logger.py         - Rich terminal output         │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Choices

| Component | Technology | Justification |
|-----------|------------|----------------|
| Wake Word Detection | `speech_recognition` + `pyaudio` + `pocketsphinx` | Zero-cost, offline, Portuguese support, <50MB RAM |
| Prompt Transcription | Deepgram REST API | High accuracy, streaming support, simple REST (no heavy SDK) |
| Agent Processing | Claude Agent SDK `query()` | Native integration, hooks support, Portuguese responses |
| Audio Response | Cartesia REST API | Brazilian Portuguese, simple REST (no heavy SDK) |
| Logging | `rich` terminal library | Color-coded output, progress bars, structured logs |

### State Machine

```python
# States: IDLE → LISTENING → RECORDING → PROCESSING → RESPONDING → IDLE
# Events: wake_word_detected, stop_word_detected, timeout, agent_complete, tts_complete
# Timeouts: 600 seconds (10 min) for recording state
```

## Relevant Files

### Existing Files (Read Only)
- `ideia.md` - **DO NOT MODIFY** - Original specification document
- `.env` - Contains API keys (DEEPGRAM_API_KEY, CARTESIA_API_KEY)

### New Files to Create

#### modules/ Directory
- `modules/__init__.py` - Module package initialization
- `modules/logger.py` - Rich terminal logging with color-coded states
- `modules/stt_fraco.py` - Offline wake/stop word detection using speech_recognition
- `modules/stt_forte.py` - Deepgram API streaming transcription
- `modules/tts.py` - Cartesia API text-to-speech conversion
- `modules/agent_handler.py` - Claude Agent SDK orchestration with hooks

#### Root Files
- `nero_assistant.py` - Main script with uv inline script metadata
- `README.md` - User guide with installation and usage instructions
- `requirements.txt` - Python dependencies (if needed beyond uv script)

### Configuration Files
- `.env.example` - Template for required environment variables (security: don't commit actual keys)

## Implementation Phases

### Phase 1: Foundation (Module Infrastructure)
**Goal:** Set up project structure and base utilities

1. Create `modules/` directory structure with `__init__.py`
2. Implement `modules/logger.py` with rich console output
3. Create `.env.example` template file
4. Set up uv script metadata structure in `nero_assistant.py`

### Phase 2: Core Implementation (STT & TTS)
**Goal:** Implement speech input/output pipeline

5. Implement `modules/stt_fraco.py` - Wake/stop word detection with speech_recognition
6. Implement `modules/stt_forte.py` - Deepgram streaming transcription
7. Implement `modules/tts.py` - Cartesia TTS integration
8. Test STT modules independently (mock API calls)

### Phase 3: Agent Integration (Claude SDK)
**Goal:** Connect voice pipeline to Claude Agent SDK

9. Implement `modules/agent_handler.py` with Claude Agent SDK query()
10. Implement Stop hook to trigger TTS on agent completion
11. Create main orchestration loop in `nero_assistant.py`
12. Integrate all modules with state machine

### Phase 4: Integration & Polish
**Goal:** End-to-end testing and documentation

13. Add comprehensive error handling and recovery
14. Implement graceful shutdown (Ctrl+C handling)
15. Create README.md with installation/usage instructions
16. Test full pipeline end-to-end

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### 1. Create Project Structure
- Create `modules/` directory
- Create `modules/__init__.py` with package initialization
- Create `.env.example` template with DEEPGRAM_API_KEY and CARTESIA_API_KEY placeholders
- Add `modules/` to `.gitignore` if not already present

### 2. Implement Logger Module
- Create `modules/logger.py`
- Define `NeroLogger` class with rich console output
- Implement state-based color coding:
  - `[INFO]` (blue) for system messages
  - `[LISTENING]` (yellow) for wake word detection
  - `[RECORDING]` (red) for audio capture
  - `[TRANSCRIBING]` (cyan) for Deepgram processing
  - `[TRANSCRIPT]` (white) for transcribed text output
  - `[STOP WORD]` (green) for stop word detection
  - `[AGENT]` (magenta) for Claude SDK processing
  - `[TOOL]` (cyan) for individual tool calls
  - `[COMPLETE]` (green) for task completion
  - `[TTS]` (purple) for audio generation
  - `[DONE]` (green) for return to idle
  - `[ERROR]` (red) for exceptions
- Implement emoji indicators for each state (🔊, 🎙️, 📝, etc.)
- Add timestamp formatting to all log messages

### 3. Implement Weak STT Module (Wake/Stop Words)
- Create `modules/stt_fraco.py`
- Import `speech_recognition`, `pyaudio`, `wave`
- Define `STTFraco` class with methods:
  - `__init__(audio_config)` - Configure microphone (default device, sample rate 16000, chunk 1024)
  - `detectar_palavra_chave(wake_words, stop_words, timeout_segundos)` - Listen continuously for wake word
    - Use `sr.Recognizer()` and `sr.Microphone()`
    - Set `language='pt-BR'` for Portuguese
    - Implement timeout loop (default 600s / 10 min)
    - Return: `{'detected': True/False, 'palavra': str, 'audio_data': bytes}`
  - `aguardar_palavra_parada(stop_words, callback)` - Run in background while wake word active
    - Listen for "NERO ENVIAR" phrase
    - Call callback when detected
    - Return control flow to main loop
- Handle `sr.WaitTimeoutError` for no speech detected
- Add error handling for microphone access issues
- Log state transitions via NeroLogger

### 4. Implement Strong STT Module (Deepgram)
- Create `modules/stt_forte.py`
- Import `httpx` or `aiohttp` for async HTTP requests
- Define `STTForte` class with methods:
  - `__init__(api_key)` - Store Deepgram API key
  - `transcrever_em_tempo_real(audio_stream, callback)` - Stream audio to Deepgram
    - Use Deepgram REST API: `https://api.deepgram.com/v1/listen`
    - Headers: `{'Authorization': f'Token {api_key}'}`
    - Set `model='nova-2', 'language='pt-BR'` for Brazilian Portuguese
    - Smart formatting: Enable punctuation, paragraphs, numerals
    - Stream results via callback as they arrive
    - Return: full transcript text when complete
- Implement proper timeout handling (10 minute max)
- Add error handling for API failures
- Log transcription progress via NeroLogger

### 5. Implement TTS Module (Cartesia)
- Create `modules/tts.py`
- Import `httpx` or `aiohttp` for async HTTP requests
- Define `TTS` class with methods:
  - `__init__(api_key)` - Store Cartesia API key
  - `gerar_audio(texto, voz='ana', estilo='simplified')` - Convert text to speech
    - Use Cartesia REST API: `https://api.cartesia.ai/v1/audio`
    - Headers: `{'Authorization': f'Token {api_key}', 'Content-Type': 'application/json'}`
    - Body: `{'transcript': texto, 'voice_id': voz, 'output_format': 'mp3'}`
    - Download audio bytes from response
    - Save to temporary file or play directly
    - Return: `{'sucesso': True/False, 'caminho_arquivo': str, 'duracao_segundos': float}`
  - `reproduzir_audio(caminho_arquivo)` - Play audio using platform-specific method
    - Windows: `winsound.PlaySound` or `subprocess.call(['powershell', ...])`
    - Linux: `aplay` via subprocess
    - macOS: `afplay` via subprocess
    - Block until playback complete
- Implement async playback to allow logging during audio
- Handle voice selection: 'ana' (female), 'lucas' (male)
- Add error handling for API failures
- Log TTS progress via NeroLogger

### 6. Implement Agent Handler with Claude SDK Hooks
- Create `modules/agent_handler.py`
- Import from `claude_agent_sdk`: `query`, `ClaudeAgentOptions`, `HookMatcher`
- Define `AgentHandler` class with methods:
  - `__init__(api_key_claude=None)` - Initialize (uses installed Claude Code CLI by default)
  - `processar_prompt(transcricao)` - Send transcript to Claude Agent
    - Configure `ClaudeAgentOptions`:
      - `system_prompt`: "Você é NERO, um assistente de voz em português brasileiro."
      - `locale`: "pt-BR" for Portuguese responses
      - `permission_mode`: "acceptEdits" for auto-approval
      - `hooks`: Add Stop hook for TTS trigger
    - Call `query(prompt=transcricao, options=options)`
    - Collect tool usage from messages (tool_name, tool_input)
    - Extract final result text from AssistantMessage
    - Return: `{'resultado': str, 'ferramentas_usadas': list, 'custo_usd': float}`
  - `_criar_hook_finalizacao_tts()` - Private method for Stop hook
    - Hook type: "Stop"
    - Extract final assistant message text
    - Generate minimal summary: "Arquivo criado", "Tarefa concluída", etc.
    - Make TTS call via callback
    - Return empty dict (no blocking)
- Implement Portuguese language prompts in system prompt
- Add comprehensive error handling for SDK failures
- Log agent processing stages via NeroLogger

### 7. Implement Main Orchestration Script
- Create `nero_assistant.py` with uv script metadata:
  ```python
  # /// script
  # requires-python = ">=3.10"
  # dependencies = [
  #   "claude-agent-sdk>=0.1.0",
  #   "rich>=13.0.0",
  #   "speechrecognition>=3.10.0",
  #   " "pyaudio>=0.2.14",
  #   "pocketsphinx>=5.0.0",
  #   "httpx>=0.27.0",
  # ]
  # ///
  ```
- Implement state machine class `MaquinaEstadosNero`:
  - States: `DESCANSO`, `AGUARDANDO`, `GRAVANDO`, `PROCESSANDO`, `RESPONDENDO`
  - `transitar(estado_novo)` method with validation
  - `estado_atual` property
- Implement main async function `main()`:
  - Load API keys from `.env` using `os.getenv()` or `python-dotenv`
  - Initialize all modules (STT fraco, STT forte, TTS, Agent, Logger)
  - Set up signal handler for SIGINT (Ctrl+C)
  - Enter main loop:
    1. State DESCANSO: Call `stt_fraco.detectar_palavra_chave()`
    2. State AGUARDANDO: Start `stt_fraco.aguardar_palavra_parada()` in background thread
    3. State GRAVANDO: Call `stt_forte.transcrever_em_tempo_real()` with callback
       - Accumulate transcript chunks
       - Check for stop word via background STT fraco thread
       - On "NERO ENVIAR" or timeout: stop recording, call `agent.processar_prompt()`
    4. State PROCESSANDO: Wait for `agent.processar_prompt()` to complete
       - Log tool usage as messages arrive
       - Extract final result message
    5. State RESPONDENDO: Call `tts.gerar_audio()` with result summary
       - Play audio using `tts.reproduzir_audio()`
       - Wait for playback complete
       - Return to DESCANSO state
- Handle exceptions in all states with recovery attempts
- Implement graceful shutdown on keyboard interrupt
- Log all state transitions with NeroLogger

### 8. Add Error Handling and Recovery
- Add try/except blocks in all async functions
- Implement retry logic for API failures (Deepgram, Cartesia)
  - Max 3 retries with exponential backoff (1s, 2s, 4s)
- Handle microphone access errors (permission denied, device not found)
- Handle network errors for API calls
- Implement state recovery on failures:
  - Return to DESCANSO state on error
  - Log error and suggest troubleshooting steps
- Add circuit breaker for repeated failures (5 consecutive failures = shutdown)

### 9. Create User Documentation
- Create `README.md` with sections:
  - **Overview**: What is NERO voice assistant
  - **Features**: Wake word, STT, TTS, Claude Agent integration
  - **Installation**:
    - `uv sync` or install dependencies manually
    - Copy `.env.example` to `.env` and add API keys
    - Test microphone: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
  - **Usage**: `uv run nero_assistant.py`
  - **Environment Variables**: DEEPGRAM_API_KEY, CARTESIA_API_KEY
  - **Troubleshooting**: Common issues and solutions
    - Microphone not working
    - API key errors
    - Portuguese language issues
  - **Architecture Diagram**: Visual pipeline representation
- Add code examples for common workflows
- Include expected log output examples
- Document Claude Agent SDK hooks usage

### 10. Final Testing and Validation
- Test wake word detection in silent room
- Test stop word detection during recording
- Test Deepgram transcription with sample Portuguese phrases
- Test Cartesia TTS with Portuguese text
- Test Claude Agent SDK integration with simple prompts
- Test 10-minute timeout mechanism
- Test error recovery (disconnect microphone during recording, etc.)
- Test graceful shutdown (Ctrl+C during each state)
- Validate memory usage (should stay <200MB RAM at idle)
- Test on target platform (Windows 10/11 expected)

### 11. Create Validation Test Script
- Create `tests/validacao_modulos.py`:
  - Test STT fraco independently
  - Test TTS with sample Portuguese text
  - Mock API calls if keys not available
  - Validate module imports
  - Return pass/fail for each component

### 12. Code Review and Optimization
- Review all async/await usage for proper concurrency
- Check for resource leaks (unclosed audio streams, HTTP connections)
- Optimize log output for readability
- Add type hints throughout (optional but recommended)
- Ensure consistent error handling patterns
- Validate Portuguese language support in all APIs

### 13. Final Polish
- Add startup banner with NERO ASCII art
- Add version information to logger
- Implement --verbose flag for detailed logs
- Implement --test-wake flag for wake word testing
- Add configuration file support (nero_config.json) for optional settings
- Clean up temporary audio files on exit
- Add gitignore for `.env` and `*.mp3` files

## Testing Strategy

### Unit Tests
- Mock `speech_recognition` for wake word detection without microphone
- Mock HTTP responses for Deepgram and Cartesia APIs
- Test state machine transitions
- Validate error handling paths
- Test timeout mechanisms

### Integration Tests
- End-to-end test: wake word → prompt → stop word → agent → TTS → idle
- Test with actual microphone in quiet environment
- Test with 10-second prompts, 5-minute prompts, timeout scenarios
- Test Portuguese language accuracy
- Test API failure recovery

### Edge Cases to Test
1. **No wake word detected for 2 minutes** - Should continue listening, log "aguardando..."
2. **Wake word detected but no speech follows** - Timeout after 10s, return to idle
3. **Stop word never spoken** - Trigger timeout at 10 minutes, submit whatever was transcribed
4. **Microphone disconnects during recording** - Handle gracefully, log error, return to idle
5. **API rate limits hit** - Implement retry with backoff, suggest user check quota
6. **Claude Agent returns empty response** - TTS: "Não entendi. Pode repetir?"
7. **User speaks mixed Portuguese/English** - Agent should still process, reply in Portuguese
8. **Multiple wake word detections (false positives)** - Implement 2s debounce between detections
9. **TTS audio playback fails** - Log error, print text fallback to console
10. **Ctrl+C during different states** - Clean shutdown from any state

### Performance Validation
- Memory usage should stay below 250MB during operation
- Wake word detection latency <500ms from phrase end
- Deepgram streaming latency <2s for first transcript chunk
- TTS generation latency <5s for typical responses (10 words)
- State transitions should be instant (<50ms)

## Acceptance Criteria

- [ ] Wake word "NERO OUVIR" detected reliably in Portuguese (≥90% accuracy in quiet room)
- [ ] Stop word "NERO ENVIAR" detected within 2s of phrase completion
- [ ] Deepgram transcribes Portuguese speech with punctuation and paragraph formatting
- [ ] Claude Agent SDK processes prompts and returns Portuguese responses
- [ ] Cartesia generates Brazilian Portuguese audio (female 'ana' voice)
- [ ] TTS audio plays automatically after agent completion
- [ ] System returns to idle state after response playback
- [ ] 10-minute timeout enforced between wake and stop word
- [ ] All stages logged with color-coded rich terminal output
- [ ] Graceful shutdown on Ctrl+C from any state
- [ ] Error recovery implemented for API failures and microphone issues
- [ ] README.md with complete installation and usage instructions
- [ ] `.env.example` template provided for security
- [ ] uv script metadata works with `uv run nero_assistant.py`
- [ ] System uses <250MB RAM at idle, <500MB during processing

## Validation Commands

Execute these commands to validate the task is complete:

```bash
# 1. Check project structure exists
ls -la voice_assistent/level1_comando_simples/

# Expected output:
# modules/
# nero_assistant.py
# README.md
# .env.example

# 2. Verify no syntax errors in Python modules
python -m py_compile modules/*.py nero_assistant.py

# Expected: No output (successful compilation)

# 3. Check all required dependencies are listed
grep "# \[" nero_assistant.py | grep -E "speechrecognition|pyaudio|pocketsphinx|httpx|rich|claude-agent-sdk"

# Expected: All dependencies present in script metadata

# 4. Test imports work correctly
python -c "from modules.logger import NeroLogger; from modules.stt_fraco import STTFraco; print('Imports OK')"

# Expected: "Imports OK"

# 5. Validate .env.example has all required variables
grep -E "DEEPGRAM_API_KEY|CARTESIA_API_KEY" .env.example

# Expected: Both API key placeholders present

# 6. Check README completeness
grep -E "Instalação|Uso|Troubleshooting|Requisitos" README.md

# Expected: All sections present (Portuguese or English)

# 7. Verify uv script metadata
head -n 20 nero_assistant.py | grep "script"

# Expected: "# /// script" comment block present

# 8. Test wake word detection (requires microphone)
# Run manual test: python -c "from modules.stt_fraco import STTFraco; print('STT fraco OK')"

# 9. Test agent handler can be imported
python -c "from modules.agent_handler import AgentHandler; print('Agent handler OK')"

# 10. Check for common security issues
grep -r "api_key|API_KEY|password|secret" modules/*.py nero_assistant.py | grep -v "\.env\|getenv"

# Expected: No hardcoded API keys, only environment variable access
```

## Notes

### Dependencies (install via `uv add` or manual pip):
- `claude-agent-sdk>=0.1.0` - Claude Agent SDK for Python
- `rich>=13.0.0` - Terminal formatting and colors
- `speechrecognition>=3.10.0` - Wake word detection
- `pyaudio>=0.2.14` - Microphone access (may require PortAudio on Windows)
- `pocketsphinx>=5.0.0` - Offline STT engine
- `httpx>=0.27.0` - Async HTTP client for Deepgram/Cartesia
- `python-dotenv>=1.0.0` - Environment variable loading

### API Keys Required:
```env
DEEPGRAM_API_KEY=xxxxxxxxxxxxx  # Get from: https://console.deepgram.com/
CARTESIA_API_KEY=xxxxxxxxxxxxx  # Get from: https://cartesia.ai/
```

### Platform-Specific Notes:
- **Windows**: PyAudio installation may fail without Visual Studio Build Tools. Alternative: Use `speech_recognition` with default system microphone.
- **Linux**: Install `portaudio19-dev` via system package manager for PyAudio
- **macOS**: PyAudio usually works out of the box with Homebrew

### Deepgram API:
- Endpoint: `POST https://api.deepgram.com/v1/listen`
- Headers: Authorization: Token {DEEPGRAM_API_KEY}
- Model: `nova-2` (latest, supports Portuguese)
- Language: `pt-BR` for Brazilian Portuguese
- Smart format enabled: punctuation, paragraphs, numerals

### Cartesia API:
- Endpoint: `POST https://api.cartesia.ai/v1/audio`
- Headers: Authorization: Token {CARTESIA_API_KEY}
- Voice: `ana` (female Brazilian Portuguese), `lucas` (male)
- Output format: MP3 for compatibility
- Style: `simplified` for minimal words, faster generation

### Portuguese Language Support:
- All APIs support pt-BR natively
- Claude Agent SDK: Use `locale="pt-BR"` in options
- Wake word accuracy: Train with 10+ samples in quiet environment

### Future Enhancements (Out of Scope for Level 1):
- Multi-language support (English/Spanish)
- Custom wake word configuration
- Voice activity detection (VAD) to reduce false positives
- Audio file recording and playback (save conversations)
- Web interface for configuration
- Integration with N8N workflows (from MEMORY.md context)

### Security Considerations:
- Never commit `.env` file with real API keys
- Use `.env.example` template with placeholder values
- Validate API keys format before use (length, prefix check)
- Sanitize transcribed text before sending to agent (remove PII if detected)
- Implement rate limiting for API calls to avoid billing surprises

---

**Plan Version:** 1.0
**Created:** 2026-02-12
**Complexity:** Complex (Feature)
**Estimated Implementation Time:** 8-12 hours for developer familiar with Python/Claude SDK
**Dependencies:** Claude Agent SDK docs (sdk-python.md), UV Scripts (uv-scripts.md), Hooks (sdk-hooks.md)
