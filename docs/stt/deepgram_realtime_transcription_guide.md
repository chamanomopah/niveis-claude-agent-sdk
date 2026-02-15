# Deepgram SDK - Transcrição de Fala em Tempo Real
## Guia Completo para Agentes de Voz com Detecção de Término de Fala

Documentação oficial baseada em: https://developers.deepgram.com

---

## Índice
1. [Visão Geral](#visão-geral)
2. [Conceitos Principais](#conceitos-principais)
3. [Instalação](#instalação)
4. [Listen V1 - Transcrição em Tempo Real](#listen-v1---transcrição-em-tempo-real)
5. [Listen V2 - Voice Agent API](#listen-v2---voice-agent-api)
6. [Detecção de Término de Fala](#detecção-de-término-de-fala)
7. [Exemplos Completos](#exemplos-completos)
8. [Parâmetros Importantes](#parâmetros-importantes)
9. [Eventos WebSocket](#eventos-websocket)

---

## Visão Geral

O Deepgram SDK Python fornece duas APIs principais para transcrição de fala em tempo real:

### **Listen V1** (`/v1/listen`)
- API de transcrição WebSocket em tempo real
- Ideal para transcrição contínua de áudio
- Controle granular sobre parâmetros de transcrição

### **Listen V2** (`/v2/listen`)
- Nova API otimizada para Voice Agents
- Detecção automática de turnos de conversação
- Melhor para aplicações de assistente de voz conversacional

---

## Conceitos Principais

### **VAD (Voice Activity Detection)**
Detecta quando o usuário está ou não falando. É fundamental para:
- Iniciar a transcrição apenas quando há fala
- Detectar pausas na fala
- Identificar quando o usuário terminou de falar

### **Endpointing**
Configura o tempo de silêncio necessário para considerar que o usuário terminou uma utterance (enunciado).

### **UtteranceEnd**
Evento que confirma o final de uma utterance completa, usado em conjunto com VAD e endpointing.

### **speech_final**
Flag que indica quando uma transcrição está finalizada devido à detecção de uma pausa.

---

## Instalação

```bash
pip install deepgram-sdk
```

Ou com Poetry/uv:
```bash
poetry add deepgram-sdk
# ou
uv add deepgram-sdk
```

---

## Listen V1 - Transcrição em Tempo Real

### Conexão Básica (Síncrona)

```python
from deepgram import DeepgramClient, LiveOptions
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1SocketClientResponse

# Inicializar cliente
API_KEY = "sua_chave_api_aqui"
client = DeepgramClient(API_KEY)

# Conectar ao WebSocket
with client.listen.v1.connect(
    model="nova-3",
    language="en-US",  # ou "pt-BR" para português
    smart_format=True,
    encoding="linear16",
    channels=1,
    sample_rate=16000,
) as connection:
    def on_message(message: ListenV1SocketClientResponse) -> None:
        if hasattr(message, 'channel') and message.channel:
            transcript = message.channel.alternatives[0].transcript
            if len(transcript) > 0:
                print(f"Transcrição: {transcript}")

    # Registrar event handlers
    connection.on(EventType.OPEN, lambda _: print("Conexão aberta"))
    connection.on(EventType.MESSAGE, on_message)
    connection.on(EventType.CLOSE, lambda _: print("Conexão fechada"))
    connection.on(EventType.ERROR, lambda error: print(f"Erro: {error}"))

    # Iniciar listening
    connection.start_listening()

    # Enviar áudio
    from deepgram.extensions.types.sockets import ListenV1MediaMessage
    with open("audio.wav", "rb") as audio_file:
        while data := audio_file.read(1024):
            connection.send_media(ListenV1MediaMessage(data))
```

### Conexão Básica (Assíncrona)

```python
import asyncio
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1SocketClientResponse

API_KEY = "sua_chave_api_aqui"
client = AsyncDeepgramClient(API_KEY)

async def transcribe_audio():
    async with client.listen.v1.connect(
        model="nova-3",
        language="pt-BR",
        smart_format=True,
        encoding="linear16",
        sample_rate=16000,
    ) as connection:
        def on_message(message: ListenV1SocketClientResponse) -> None:
            if hasattr(message, 'channel') and message.channel:
                transcript = message.channel.alternatives[0].transcript
                if len(transcript) > 0:
                    print(f"Transcrição: {transcript}")

        connection.on(EventType.OPEN, lambda _: print("Conexão aberta"))
        connection.on(EventType.MESSAGE, on_message)
        connection.on(EventType.CLOSE, lambda _: print("Conexão fechada"))

        await connection.start_listening()

        # Enviar áudio em chunks
        from deepgram.extensions.types.sockets import ListenV1MediaMessage
        with open("audio.wav", "rb") as audio_file:
            while data := audio_file.read(1024):
                await connection.send_media(ListenV1MediaMessage(data))

        # Aguardar processamento
        await asyncio.sleep(2)

asyncio.run(transcribe_audio())
```

---

## Listen V2 - Voice Agent API

**Listen V2** é a API recomendada para Voice Agents, pois inclui:
- Detecção automática de turnos (End-of-Turn Detection)
- Melhor latência
- Configurações otimizadas para conversação

### Conexão V2 (Síncrona)

```python
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse

API_KEY = "sua_chave_api_aqui"
client = DeepgramClient(API_KEY)

with client.listen.v2.connect(
    model="flux-general-en",  # ou "pt-BR" para português
    encoding="linear16",
    sample_rate="16000",
    # Parâmetros de detecção de turno
    eager_eot_threshold="0.5",  # Threshold para eager end-of-turn
    eot_threshold="0.7",  # Threshold para end-of-turn
    eot_timeout_ms="1000",  # Timeout em milliseconds
) as connection:
    def on_message(message: ListenV2SocketClientResponse) -> None:
        msg_type = getattr(message, "type", "Unknown")

        if msg_type == "Welcome":
            print("Conectado ao Deepgram Voice Agent API")

        elif msg_type == "ConversationText":
            # Texto da conversa recebido
            if hasattr(message, 'content'):
                print(f"Usuário disse: {message.content}")

        elif msg_type == "UserStartedSpeaking":
            print("🗣️ Usuário começou a falar")

        elif msg_type == "AgentThinking":
            print("🤔 Agente está pensando...")

        elif msg_type == "AgentStartedSpeaking":
            print("🔊 Agente começou a falar")

        elif msg_type == "AgentAudioDone":
            print("✅ Áudio do agente finalizado")

    # Registrar event handlers
    connection.on(EventType.OPEN, lambda _: print("Conexão aberta"))
    connection.on(EventType.MESSAGE, on_message)
    connection.on(EventType.CLOSE, lambda _: print("Conexão fechada"))
    connection.on(EventType.ERROR, lambda error: print(f"Erro: {error}"))

    connection.start_listening()

    # Enviar áudio
    from deepgram.extensions.types.sockets import ListenV2MediaMessage
    with open("microphone_audio.wav", "rb") as audio_file:
        while data := audio_file.read(1024):
            connection.send_media(ListenV2MediaMessage(data=data))
```

### Conexão V2 (Assíncrona)

```python
import asyncio
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse

API_KEY = "sua_chave_api_aqui"
client = AsyncDeepgramClient(API_KEY)

async def voice_agent():
    async with client.listen.v2.connect(
        model="flux-general-en",
        encoding="linear16",
        sample_rate="16000",
    ) as connection:
        def on_message(message: ListenV2SocketClientResponse) -> None:
            msg_type = getattr(message, "type", "Unknown")

            if msg_type == "ConversationText":
                if hasattr(message, 'content'):
                    print(f"Transcrição: {message.content}")

        connection.on(EventType.OPEN, lambda _: print("Conexão aberta"))
        connection.on(EventType.MESSAGE, on_message)

        await connection.start_listening()

        # Enviar áudio do microfone
        from deepgram.extensions.types.sockets import ListenV2MediaMessage
        # Aqui você usaria uma biblioteca para capturar áudio do microfone
        # Exemplo com pyaudio:
        # import pyaudio
        # audio = pyaudio.PyAudio()
        # stream = audio.open(format=pyaudio.paInt16, channels=1,
        #                     rate=16000, input=True, frames_per_buffer=1024)
        #
        # while True:
        #     data = stream.read(1024)
        #     await connection.send_media(ListenV2MediaMessage(data=data))

asyncio.run(voice_agent())
```

---

## Detecção de Término de Fala

### Método 1: Endpointing (Listen V1)

O `endpointing` define quanto tempo de silêncio (em ms) é necessário para considerar que o usuário terminou.

```python
with client.listen.v1.connect(
    model="nova-3",
    language="pt-BR",
    endpointing=500,  # 500ms de silêncio para finalizar
    interim_results=True,  # Necessário para resultados parciais
    smart_format=True,
) as connection:
    def on_message(message: ListenV1SocketClientResponse) -> None:
        if hasattr(message, 'channel') and message.channel:
            transcript = message.channel.alternatives[0].transcript

            # Verificar se é resultado final
            is_final = getattr(message, 'is_final', False)
            speech_final = getattr(message, 'speech_final', False)

            if len(transcript) > 0:
                print(f"[{'FINAL' if speech_final else 'PARCIAL'}] {transcript}")

                if speech_final:
                    print("✅ Usuário terminou de falar!")
                    # Aqui você pode processar o comando

    connection.on(EventType.MESSAGE, on_message)
    connection.start_listening()
```

### Método 2: UtteranceEnd Events (Listen V1)

Mais preciso que endpointing, o `utterance_end_ms` define quanto tempo aguardar após a última palavra antes de emitir evento `UtteranceEnd`.

```python
with client.listen.v1.connect(
    model="nova-3",
    language="pt-BR",
    # Configurações para UtteranceEnd
    interim_results=True,
    utterance_end_ms="1000",  # 1 segundo após a última palavra
    vad_events=True,  # Necessário para eventos VAD
    endpointing=300,
) as connection:
    def on_message(message: ListenV1SocketClientResponse) -> None:
        msg_type = getattr(message, "type", "Unknown")

        if msg_type == "SpeechStarted":
            print("🗣️ Usuário começou a falar")

        elif msg_type == "UtteranceEnd":
            # UtteranceEnd é emitido quando a utterance está realmente finalizada
            print("✅ UTTERANCE FINALIZADA - Usuário terminou de falar!")
            # Processar comando completo aqui

        elif hasattr(message, 'channel') and message.channel:
            transcript = message.channel.alternatives[0].transcript
            if len(transcript) > 0:
                speech_final = getattr(message, 'speech_final', False)
                print(f"[{'F' if speech_final else 'P'}] {transcript}")

    connection.on(EventType.MESSAGE, on_message)
    connection.start_listening()
```

### Método 3: Voice Agent API EOT Detection (Listen V2)

**Recomendado para Voice Agents** - Detecção automática de turnos conversacionais.

```python
with client.listen.v2.connect(
    model="flux-general-en",
    encoding="linear16",
    sample_rate="16000",
    # Controle de detecção de fim de turno
    eager_eot_threshold="0.5",  # 0.0 a 1.0 - mais agressivo
    eot_threshold="0.7",  # 0.0 a 1.0 - mais conservador
    eot_timeout_ms="1000",  # Timeout máximo em ms
) as connection:
    def on_message(message: ListenV2SocketClientResponse) -> None:
        msg_type = getattr(message, "type", "Unknown")

        if msg_type == "UserStartedSpeaking":
            print("🗣️ Usuário começou a falar")

        elif msg_type == "ConversationText":
            if hasattr(message, 'content'):
                print(f"📝 Transcrição: {message.content}")
                # Este evento é emitido quando há texto da conversa

        elif msg_type == "AgentThinking":
            print("🤔 Usuário parou de falar, agente processando...")

        elif msg_type == "AgentStartedSpeaking":
            print("🔊 Agente respondendo...")

        # Nota: Listen V2 gerencia automaticamente a detecção de fim de turno

    connection.on(EventType.MESSAGE, on_message)
    connection.start_listening()
```

---

## Exemplos Completos

### Exemplo 1: Assistente de Voz com Microfone (V1 + Endpointing)

```python
import pyaudio
from deepgram import DeepgramClient, LiveOptions
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1SocketClientResponse, ListenV1MediaMessage

API_KEY = "sua_chave_api_aqui"

class VoiceAssistant:
    def __init__(self):
        self.client = DeepgramClient(API_KEY)
        self.connection = None
        self.is_listening = False
        self.current_transcript = ""

    def on_message(self, message: ListenV1SocketClientResponse) -> None:
        if hasattr(message, 'channel') and message.channel:
            transcript = message.channel.alternatives[0].transcript
            is_final = getattr(message, 'is_final', False)
            speech_final = getattr(message, 'speech_final', False)

            if len(transcript) > 0:
                if not is_final:
                    # Resultado parcial
                    print(f"\r🎤 {transcript}", end="")
                else:
                    # Resultado final
                    print(f"\r✅ {transcript}")
                    self.current_transcript = transcript

                if speech_final:
                    print("\n🎯 Usuário terminou! Processando comando...")
                    self.process_command(self.current_transcript)
                    self.current_transcript = ""

    def process_command(self, text: str):
        """Processar o comando do usuário"""
        # Aqui você integra com seu agente
        print(f"📝 Comando recebido: {text}")
        # TODO: Enviar para agente, processar, etc.

    def start(self):
        """Iniciar escuta do microfone"""
        # Configurar áudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        # Conectar ao Deepgram
        self.connection = self.client.listen.v1.connect(
            model="nova-3",
            language="pt-BR",
            endpointing=600,  # 600ms de silêncio
            interim_results=True,
            smart_format=True,
            punctuate=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
        )

        self.connection.on(EventType.MESSAGE, self.on_message)
        self.connection.on(EventType.OPEN, lambda _: print("🎤 Escutando..."))
        self.connection.on(EventType.ERROR, lambda e: print(f"Erro: {e}"))

        self.connection.start_listening()
        self.is_listening = True

        print("🎤 Assistente de voz ativo! Pressione Ctrl+C para parar.")

        try:
            while self.is_listening:
                # Ler áudio do microfone e enviar para Deepgram
                data = self.stream.read(1024, exception_on_overflow=False)
                self.connection.send_media(ListenV1MediaMessage(data))
        except KeyboardInterrupt:
            print("\n⏹️ Parando assistente...")
            self.stop()

    def stop(self):
        """Parar escuta"""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        if self.connection:
            self.connection.finish()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.start()
```

### Exemplo 2: Voice Agent com V2 (Assíncrono)

```python
import asyncio
import pyaudio
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse, ListenV2MediaMessage

API_KEY = "sua_chave_api_aqui"

class AsyncVoiceAgent:
    def __init__(self):
        self.client = AsyncDeepgramClient(API_KEY)
        self.connection = None
        self.is_running = False

    def on_message(self, message: ListenV2SocketClientResponse) -> None:
        msg_type = getattr(message, "type", "Unknown")

        if msg_type == "Welcome":
            print("✅ Conectado ao Deepgram Voice Agent API")

        elif msg_type == "UserStartedSpeaking":
            print("🗣️ ")

        elif msg_type == "ConversationText":
            if hasattr(message, 'content'):
                print(f"📝 Você disse: {message.content}")
                self.handle_user_input(message.content)

        elif msg_type == "AgentThinking":
            print("🤔 Processando...")

        elif msg_type == "AgentStartedSpeaking":
            print("🔊 Agente: ", end="")

        elif msg_type == "AgentAudioDone":
            print()  # Nova linha após resposta

    def handle_user_input(self, text: str):
        """Processar entrada do usuário"""
        # Aqui você integra com seu agente Claude/LLM
        print(f"💭 Processando: {text}")
        # TODO: Implementar lógica do agente

    async def stream_microphone(self):
        """Capturar e streaming áudio do microfone"""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        print("🎤 Voice Agent ativo! Fale algo...")

        try:
            while self.is_running:
                data = stream.read(1024, exception_on_overflow=False)
                await self.connection.send_media(ListenV2MediaMessage(data=data))
                await asyncio.sleep(0.001)  # Pequeno delay
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    async def start(self):
        """Iniciar voice agent"""
        self.connection = self.client.listen.v2.connect(
            model="flux-general-en",
            encoding="linear16",
            sample_rate="16000",
            eager_eot_threshold="0.5",
            eot_threshold="0.7",
            eot_timeout_ms="1000",
        )

        self.connection.on(EventType.OPEN, lambda _: print("🔌 Conectando..."))
        self.connection.on(EventType.MESSAGE, self.on_message)
        self.connection.on(EventType.CLOSE, lambda _: print("🔌 Desconectado"))
        self.connection.on(EventType.ERROR, lambda e: print(f"❌ Erro: {e}"))

        await self.connection.start_listening()
        self.is_running = True

        # Iniciar streaming de microfone
        await self.stream_microphone()

    async def stop(self):
        """Parar voice agent"""
        self.is_running = False
        if self.connection:
            await self.connection.send_control(
                ListenV2ControlMessage(type="CloseStream")
            )

if __name__ == "__main__":
    agent = AsyncVoiceAgent()
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        print("\n⏹️ Parando...")
        asyncio.run(agent.stop())
```

---

## Parâmetros Importantes

### Parâmetros de Transcrição

| Parâmetro | Tipo | Descrição | Valor Padrão |
|-----------|------|-----------|--------------|
| `model` | string | Modelo de IA a usar | `"nova-3"` |
| `language` | string | Idioma (BCP-47) | `"en-US"` |
| `smart_format` | bool | Formatação inteligente | `false` |
| `punctuate` | bool | Adicionar pontuação | `false` |
| `profanity_filter` | bool | Filtrar profanidade | `false` |
| `diarize` | bool | Reconhecer falantes | `false` |
| `numerals` | bool | Converter números | `false` |

### Parâmetros de Áudio

| Parâmetro | Tipo | Descrição | Valor Padrão |
|-----------|------|-----------|--------------|
| `encoding` | string | Formato de áudio | Opcional |
| `sample_rate` | int | Taxa de amostragem (Hz) | Opcional |
| `channels` | int | Número de canais | `1` |

### Parâmetros de Endpointing (V1)

| Parâmetro | Tipo | Descrição | Valor Padrão |
|-----------|------|-----------|--------------|
| `endpointing` | int/bool | Tempo de silêncio (ms) | `10` |
| `interim_results` | bool | Resultados parciais | `false` |
| `utterance_end_ms` | int | Tempo para utterance end | N/A |
| `vad_events` | bool | Eventos VAD | `false` |

### Parâmetros de EOT Detection (V2)

| Parâmetro | Tipo | Descrição | Valor Padrão |
|-----------|------|-----------|--------------|
| `eager_eot_threshold` | float | Threshold eager EOT (0-1) | N/A |
| `eot_threshold` | float | Threshold EOT (0-1) | N/A |
| `eot_timeout_ms` | int | Timeout EOT (ms) | N/A |

---

## Eventos WebSocket

### Listen V1 Events

| Evento | Descrição |
|--------|-----------|
| `Metadata` | Informações de metadados da conexão |
| `Results` | Resultados de transcrição |
| `SpeechStarted` | Usuário começou a falar |
| `UtteranceEnd` | Utterance finalizada |
| `error` | Erro na conexão |

### Listen V2 Events

| Evento | Descrição |
|--------|-----------|
| `Welcome` | Mensagem de boas-vindas |
| `ConversationText` | Texto da conversa |
| `UserStartedSpeaking` | Usuário começou a falar |
| `AgentThinking` | Agente processando |
| `AgentStartedSpeaking` | Agente começou a falar |
| `AgentAudioDone` | Áudio do agente finalizado |
| `SettingsApplied` | Configurações aplicadas |
| `Warning` | Aviso |
| `Error` | Erro |

---

## Modelos Disponíveis

### Nova Series (Recomendado)
- **nova-3**: Modelo mais avançado, melhor precisão
- **nova-2**: Balanceado entre performance e custo

### Flux Series (V2 / Voice Agents)
- **flux-general-en**: Inglês geral para voice agents
- **flux-pt**: Português para voice agents

### Idiomas Suportados
- `en-US`: Inglês (EUA)
- `pt-BR`: Português (Brasil)
- `es`: Espanhol
- `fr`: Francês
- `de`: Alemão
- `it`: Italiano
- E muitos mais...

---

## Melhores Práticas

### 1. Escolha da API
- **Use Listen V1** para transcrição contínua e controle granular
- **Use Listen V2** para voice agents e conversação natural

### 2. Configuração de Endpointing
```python
# Para comandos curtos (assistente pessoal)
endpointing=400-600

# Para conversação natural
endpointing=800-1200

# Para ditado (pausas mais longas)
endpointing=1500-2000
```

### 3. Uso de UtteranceEnd vs speech_final
```python
# speech_final: Mais rápido, menos preciso
# Use para: feedback visual em tempo real

# UtteranceEnd: Mais lento, mais preciso
# Use para: processamento de comandos, ações definitivas
```

### 4. Tratamento de Erros
```python
def on_message(self, message):
    try:
        # Processar mensagem
        pass
    except Exception as e:
        print(f"Erro processando mensagem: {e}")
        # Reconectar se necessário
```

### 5. Gerenciamento de Conexão
```python
# Sempre fechar a conexão
try:
    connection.start_listening()
    # ... usar conexão
finally:
    connection.finish()
```

---

## Links Úteis

- **Documentação Oficial**: https://developers.deepgram.com
- **GitHub Python SDK**: https://github.com/deepgram/deepgram-python-sdk
- **API Reference**: https://developers.deepgram.com/reference
- **Exemplos**: https://github.com/deepgram/deepgram-python-sdk/tree/main/examples

---

## Conclusão

O Deepgram SDK oferece duas abordagens poderosas para transcrição em tempo real:

1. **Listen V1** com `endpointing` e `utterance_end_ms` para detecção precisa de quando o usuário termina de falar
2. **Listen V2** com detecção automática de turnos conversacionais para voice agents

Para **assistentes de voz**, recomenda-se:
- **V1 + UtteranceEnd** para máximo controle
- **V2** para implementação mais simples e conversação natural

Lembre-se de configurar adequadamente os tempos de silêncio (`endpointing`, `utterance_end_ms`, `eot_timeout_ms`) conforme o uso pretendido.

---

**Última atualização**: 2025-02-15
**Versão do SDK**: 3.x+
**API Listen**: V1 e V2
