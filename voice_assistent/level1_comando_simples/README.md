# NERO - Voice Assistant with Claude Agent SDK

A fully voice-controlled AI assistant using Claude Agent SDK, featuring wake word detection, speech-to-text, and text-to-speech in Brazilian Portuguese.

## Features

- 🎙️ **Wake Word Detection** - Always-on listening for "NERO OUVIR" (offline, zero cost)
- 📝 **High-Quality Transcription** - Deepgram API for accurate Portuguese speech recognition
- 🤖 **Claude Agent SDK** - Process requests with Claude's powerful AI
- 🔊 **Brazilian Portuguese TTS** - Cartesia API with natural female voice ("Ana")
- ✋ **Stop Word Detection** - Say "NERO ENVIAR" to submit your prompt
- ⏱️ **Auto Timeout** - 10-minute maximum recording time
- 🎨 **Rich Terminal Output** - Color-coded logs for easy debugging

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Main Loop (asyncio)                                            │
│                                                                  │
│  State Machine:                                                  │
│    DESCANSO → AGUARDANDO → GRAVANDO →                          │
│    PROCESSANDO → RESPONDENDO → DESCANSO                         │
│                                                                  │
│  Modules:                                                       │
│    ├─ stt_fraco.py     - Wake/stop word detection (offline)    │
│    ├─ stt_forte.py     - Deepgram transcription (online)       │
│    ├─ agent_handler.py - Claude Agent SDK integration           │
│    ├─ tts.py            - Cartesia text-to-speech              │
│    └─ logger.py         - Rich terminal logging                │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.10 or higher
- Microphone access
- API keys for Deepgram and Cartesia
- Claude Agent SDK installed (via CLI or pip)

## Installation

### 1. Clone or navigate to project

```bash
cd voice_assistent/level1_comando_simples
```

### 2. Install dependencies

#### Option A: Using uv (recommended)

```bash
uv sync
```

#### Option B: Using pip

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install claude-agent-sdk>=0.1.0
pip install rich>=13.0.0
pip install SpeechRecognition>=3.10.0
pip install pyaudio>=0.2.14
pip install pocketsphinx>=5.0.0
pip install httpx>=0.27.0
pip install python-dotenv>=1.0.0
```

### 3. Configure API keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
CARTESIA_API_KEY=your_cartesia_api_key_here
```

#### Getting API Keys

**Deepgram:**
1. Visit https://console.deepgram.com/
2. Sign up for free account
3. Create API key
4. Copy to `.env` file

**Cartesia:**
1. Visit https://cartesia.ai/
2. Sign up for beta access
3. Create API key
4. Copy to `.env` file

### 4. Test microphone

```bash
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

Should display your available microphones.

## Usage

### Basic Usage

Run NERO:

```bash
# Using uv
uv run nero_assistant.py

# Or directly with Python
python nero_assistant.py
```

NERO will start and display:

```
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ██╗████████╗██████╗ ███████╗██████╗ ██╗   ██╗     ║
║   ████╗  ██║╚══██╔══╝██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝     ║
║   ██╔██╗ ██║   ██║   ██████╔╝█████╗  ██████╔╝ ╚████╔╝      ║
║   ██║╚██╗██║   ██║   ██╔══██╗██╔══╝  ██╔══██╗  ╚██╔╝       ║
║   ██║ ╚████║   ██║   ██║  ██║███████╗██║  ██║   ██║        ║
║   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝        ║
║                                                              ║
║              Voice Assistant v1.0 - Claude Agent SDK           ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝

ℹ️  Initializing NERO voice assistant...
ℹ️  Press Ctrl+C at any time to exit gracefully
ℹ️  NERO is ready! Say 'NERO OUVIR' to begin.
```

### Voice Commands

1. **Wake Word**: Say **"NERO OUVIR"** to activate
   - NERO enters listening state (yellow)
   - You have 10 minutes to speak

2. **Your Prompt**: Speak your request naturally
   - Example: "Qual a temperatura em São Paulo?"
   - Example: "Crie um arquivo Python com uma função de soma"
   - Example: "Explique o que é machine learning"

3. **Stop Word**: Say **"NERO ENVIAR"** to submit
   - NERO processes your request
   - You'll hear the response in Brazilian Portuguese

### Verbose Mode

Enable detailed debug logging:

```bash
python nero_assistant.py --verbose
# or
python nero_assistant.py -v
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key for speech-to-text |
| `CARTESIA_API_KEY` | Yes | Cartesia API key for text-to-speech |
| `CLAUDE_API_KEY` | Optional | Claude API key (uses installed CLI if not set) |

## Troubleshooting

### Microphone not working

**Symptoms:** "Failed to initialize microphone" error

**Solutions:**

1. Check microphone permissions
2. List available microphones:
   ```bash
   python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
   ```
3. Specify device index in code (modify `modules/stt_fraco.py`)

### PyAudio installation fails (Windows)

**Symptoms:** "error: Microsoft Visual C++ 14.0 is required"

**Solutions:**

1. Install Visual Studio Build Tools
2. Or use pre-built wheel:
   ```bash
   pip pipwin
   pipwin install pyaudio
   ```

### Wake word not detected

**Symptoms:** NERO doesn't respond to "NERO OUVIR"

**Solutions:**

1. Speak clearly and close to microphone
2. Reduce background noise
3. Try alternative wake word: just "NERO"
4. Calibrate ambient noise (automatic on first use)

### API key errors

**Symptoms:** "Invalid API key" or "401 Unauthorized"

**Solutions:**

1. Verify `.env` file is in project root
2. Check API keys are correct (no extra spaces)
3. Ensure keys are active in respective dashboards
4. Regenerate keys if necessary

### Transcription returns empty

**Symptoms:** Deepgram returns empty transcript

**Solutions:**

1. Speak louder and closer to microphone
2. Check Deepgram API quota
3. Test with shorter phrases
4. Verify Portuguese language support

### TTS audio doesn't play

**Symptoms:** No audio response from NERO

**Solutions:**

1. Check system volume
2. Verify audio output device
3. Check Cartesia API quota
4. Run in verbose mode for detailed logs

## Development

### Project Structure

```
level1_comando_simples/
├── modules/
│   ├── __init__.py           # Package initialization
│   ├── logger.py             # Rich terminal logging
│   ├── stt_fraco.py          # Offline wake/stop word detection
│   ├── stt_forte.py          # Deepgram transcription
│   ├── tts.py                # Cartesia text-to-speech
│   └── agent_handler.py      # Claude Agent SDK integration
├── nero_assistant.py         # Main orchestration script
├── .env.example              # Environment template
├── .env                      # Your API keys (don't commit!)
├── README.md                 # This file
├── ideia.md                  # Original specification (read-only)
└── requirements.txt          # Python dependencies
```

### Adding Custom Commands

Edit `modules/agent_handler.py` to customize the system prompt:

```python
system_prompt = (
    "Você é NERO, um assistente de voz especializado em Python. "
    "Você responde sempre em português brasileiro e fornece "
    "exemplos de código quando relevante."
)
```

### Testing Individual Modules

Test wake word detection:

```python
from modules.stt_fraco import STTFraco
from modules.logger import NeroLogger

logger = NeroLogger(verbose=True)
stt = STTFraco(logger)
result = stt.detectar_wake_word(["NERO OUVIR"])
print(result)
```

Test TTS:

```python
from modules.tts import TTS
from modules.logger import NeroLogger
import asyncio

async def test():
    logger = NeroLogger(verbose=True)
    tts = TTS("your_api_key", logger)
    await tts.falar("Olá, eu sou o NERO!", voz="ana")

asyncio.run(test())
```

## Architecture Details

### State Machine

NERO operates on a state machine with 5 states:

1. **DESCANSO** (Idle) - Waiting for wake word
2. **AGUARDANDO** (Waiting) - Wake word detected, preparing to record
3. **GRAVANDO** (Recording) - Capturing and transcribing user prompt
4. **PROCESSANDO** (Processing) - Sending to Claude Agent SDK
5. **RESPONDENDO** (Responding) - Playing TTS response

### Hybrid STT Approach

NERO uses a hybrid speech recognition strategy:

| Component | Technology | Purpose | Cost |
|-----------|-----------|---------|------|
| Wake Word | PocketSphinx (offline) | Detect "NERO OUVIR" | Free |
| Stop Word | PocketSphinx (offline) | Detect "NERO ENVIAR" | Free |
| Transcription | Deepgram (online) | Accurate Portuguese STT | Paid API |

### Claude Agent SDK Hooks

NERO uses Stop hooks to automatically trigger TTS when Claude completes processing:

```python
hooks=[self._criar_hook_finalizacao_tts()]
```

This ensures voice responses play automatically without manual intervention.

## Performance

- **Memory Usage:** <250MB at idle, <500MB during processing
- **Wake Word Latency:** <500ms from phrase end
- **Transcription Latency:** <2s for first chunk (Deepgram streaming)
- **TTS Generation:** <5s for typical responses (10 words)
- **Max Recording Time:** 10 minutes (configurable)

## Security

- **Never commit `.env` file** - Contains real API keys
- **Use `.env.example`** - Template only, no real keys
- **Sanitize transcriptions** - Remove PII before sending to agent
- **Rate limiting** - Monitor API usage to avoid billing surprises

## Contributing

This is Level 1 of the NERO voice assistant. Future enhancements:

- [ ] Multi-language support (English/Spanish)
- [ ] Custom wake word configuration
- [ ] Voice activity detection (VAD)
- [ ] Conversation history/memory
- [ ] Web interface for configuration
- [ ] Integration with N8N workflows

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check Troubleshooting section
2. Run with `--verbose` flag for detailed logs
3. Review API dashboards for quota/status
4. Check microphone and audio device settings

---

**NERO Voice Assistant v1.0** - Powered by Claude Agent SDK

Made with ❤️ in Brazil
