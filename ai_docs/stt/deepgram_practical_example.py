"""
Exemplo Prático: Assistente de Voz com Deepgram
===============================================

Este exemplo demonstra como criar um assistente de voz que:
1. Escuta o usuário em tempo real
2. Detecta quando o usuário terminou de falar
3. Envia o comando transcritivo para processamento

Requisitos:
    pip install deepgram-sdk pyaudio

Autor: Deepgram SDK Documentation
Data: 2025-02-15
"""

import pyaudio
import asyncio
from typing import Callable, Optional
from dataclasses import dataclass
from enum import Enum

from deepgram import DeepgramClient, AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import (
    ListenV1SocketClientResponse,
    ListenV1MediaMessage,
    ListenV2SocketClientResponse,
    ListenV2MediaMessage,
    ListenV2ControlMessage
)


class DetectionMethod(Enum):
    """Métodos de detecção de término de fala"""
    ENDPOINTING = "endpointing"  # Baseado em tempo de silêncio
    UTTERANCE_END = "utterance_end"  # Evento UtteranceEnd (mais preciso)
    VOICE_AGENT = "voice_agent"  # API V2 automática


@dataclass
class TranscriptionResult:
    """Resultado de uma transcrição completa"""
    text: str
    is_final: bool
    confidence: float
    duration: float


class DeepgramVoiceAssistant:
    """
    Assistente de voz usando Deepgram SDK.

    Suporta dois modos:
    - V1: Maior controle com endpointing/utterance_end
    - V2: Voice Agent API com detecção automática
    """

    def __init__(
        self,
        api_key: str,
        language: str = "pt-BR",
        detection_method: DetectionMethod = DetectionMethod.UTTERANCE_END,
        on_transcript: Optional[Callable[[TranscriptionResult], None]] = None
    ):
        """
        Inicializar assistente de voz.

        Args:
            api_key: Chave API do Deepgram
            language: Código do idioma (ex: "pt-BR", "en-US")
            detection_method: Método para detectar fim da fala
            on_transcript: Callback quando transcrição estiver completa
        """
        self.api_key = api_key
        self.language = language
        self.detection_method = detection_method
        self.on_transcript = on_transcript

        self.client = None
        self.connection = None
        self.audio = None
        self.stream = None
        self.is_listening = False

        self._current_transcript = ""
        self._transcript_start_time = None

    # ========================================================================
    # MODO V1: Transcrição com Endpointing/UtteranceEnd
    # ========================================================================

    def start_v1(self, silence_duration: int = 600):
        """
        Iniciar modo V1 (endpointing ou utterance_end).

        Args:
            silence_duration: Tempo de silêncio em ms para detectar fim
        """
        print(f"🎤 Iniciando Deepgram V1 ({self.detection_method.value})...")
        print(f"⏱️  Silêncio detectado após: {silence_duration}ms")

        self.client = DeepgramClient(self.api_key)

        # Configurar parâmetros baseados no método de detecção
        if self.detection_method == DetectionMethod.UTTERANCE_END:
            # Método mais preciso com eventos UtteranceEnd
            params = {
                "model": "nova-3",
                "language": self.language,
                "smart_format": True,
                "punctuate": True,
                "encoding": "linear16",
                "channels": 1,
                "sample_rate": 16000,
                # Parâmetros críticos para UtteranceEnd
                "interim_results": True,
                "utterance_end_ms": str(silence_duration),
                "vad_events": True,
                "endpointing": silence_duration // 2,  # Mais curto que utterance_end
            }
            print("✅ Método: UtteranceEnd (mais preciso)")
        else:
            # Método com endpointing apenas
            params = {
                "model": "nova-3",
                "language": self.language,
                "smart_format": True,
                "punctuate": True,
                "encoding": "linear16",
                "channels": 1,
                "sample_rate": 16000,
                "interim_results": True,
                "endpointing": silence_duration,
            }
            print("✅ Método: Endpointing (rápido)")

        # Conectar
        self.connection = self.client.listen.v1.connect(**params)
        self.connection.on(EventType.OPEN, self._on_open)
        self.connection.on(EventType.MESSAGE, self._on_message_v1)
        self.connection.on(EventType.CLOSE, self._on_close)
        self.connection.on(EventType.ERROR, self._on_error)

        self.connection.start_listening()
        self.is_listening = True

        # Iniciar captura de áudio
        self._start_microphone()

    def _on_message_v1(self, message: ListenV1SocketClientResponse):
        """Processar mensagens do modo V1"""
        msg_type = getattr(message, "type", "Unknown")

        # Evento SpeechStarted (VAD)
        if msg_type == "SpeechStarted":
            print("🗣️  [Falando...]", end="", flush=True)
            self._transcript_start_time = asyncio.get_event_loop().time()

        # Evento UtteranceEnd (apenas se habilitado)
        elif msg_type == "UtteranceEnd":
            print("\r✅ [Fim de fala detectado!]")
            if self._current_transcript:
                self._process_final_transcript()

        # Resultados de transcrição
        elif hasattr(message, 'channel') and message.channel:
            alternatives = message.channel.alternatives
            if not alternatives or not alternatives[0]:
                return

            transcript = alternatives[0].transcript
            if not transcript:
                return

            is_final = getattr(message, 'is_final', False)
            speech_final = getattr(message, 'speech_final', False)

            # Transcrição parcial
            if not is_final:
                print(f"\r🎤 [Parcial]: {transcript}", end="", flush=True)

            # Transcrição finalizada (speech_final)
            elif is_final and speech_final:
                print(f"\r📝 [Final]: {transcript}")
                self._current_transcript = transcript

                if self.detection_method == DetectionMethod.ENDPOINTING:
                    # No modo endpointing, speech_final indica fim
                    self._process_final_transcript()
            else:
                # is_final mas não speech_final
                self._current_transcript = transcript

    # ========================================================================
    # MODO V2: Voice Agent API
    # ========================================================================

    async def start_v2(
        self,
        eager_eot_threshold: float = 0.5,
        eot_threshold: float = 0.7,
        eot_timeout_ms: int = 1000
    ):
        """
        Iniciar modo V2 (Voice Agent API).

        Detecção automática de fim de turno conversacional.

        Args:
            eager_eot_threshold: Threshold para eager EOT (0.0-1.0)
            eot_threshold: Threshold para EOT (0.0-1.0)
            eot_timeout_ms: Timeout máximo em ms
        """
        print(f"🎤 Iniciando Deepgram V2 (Voice Agent)...")
        print(f"⚙️  Eager EOT: {eager_eot_threshold}, EOT: {eot_threshold}")

        self.client = AsyncDeepgramClient(self.api_key)

        # Conectar com parâmetros de detecção de turno
        self.connection = self.client.listen.v2.connect(
            model="flux-general-en" if self.language == "en-US" else "flux-pt",
            encoding="linear16",
            sample_rate="16000",
            eager_eot_threshold=str(eager_eot_threshold),
            eot_threshold=str(eot_threshold),
            eot_timeout_ms=str(eot_timeout_ms),
        )

        self.connection.on(EventType.OPEN, lambda _: print("✅ Conectado ao Voice Agent API"))
        self.connection.on(EventType.MESSAGE, self._on_message_v2)
        self.connection.on(EventType.CLOSE, lambda _: print("🔌 Desconectado"))
        self.connection.on(EventType.ERROR, lambda e: print(f"❌ Erro: {e}"))

        await self.connection.start_listening()
        self.is_listening = True

        # Iniciar captura de áudio
        await self._start_microphone_async()

    def _on_message_v2(self, message: ListenV2SocketClientResponse):
        """Processar mensagens do modo V2"""
        msg_type = getattr(message, "type", "Unknown")

        if msg_type == "Welcome":
            print("👋 Bem-vindo ao Voice Agent!")

        elif msg_type == "UserStartedSpeaking":
            print("🗣️  [Você está falando...]", end="", flush=True)

        elif msg_type == "ConversationText":
            # Texto completo da conversa
            if hasattr(message, 'content'):
                print(f"\r📝 [Transcrição]: {message.content}")
                self._current_transcript = message.content

        elif msg_type == "AgentThinking":
            # Agente está processando (usuário parou de falar)
            print("\r🤔 [Processando...]")
            if self._current_transcript:
                self._process_final_transcript()

        elif msg_type == "AgentStartedSpeaking":
            print("🔊 [Agente respondendo...]")

        elif msg_type == "AgentAudioDone":
            print("✅ [Resposta finalizada]")

    # ========================================================================
    # MÉTODOS UTILITÁRIOS
    # ========================================================================

    def _process_final_transcript(self):
        """Processar transcrição finalizada"""
        if not self._current_transcript:
            return

        result = TranscriptionResult(
            text=self._current_transcript.strip(),
            is_final=True,
            confidence=0.95,  # Deepgram não expõe facilmente
            duration=0.0
        )

        print(f"\n🎯 COMANDO FINALIZADO: {result.text}")

        # Callback se fornecido
        if self.on_transcript:
            self.on_transcript(result)

        # Limpar para próximo comando
        self._current_transcript = ""

    def _start_microphone(self):
        """Iniciar captura do microfone (síncrono)"""
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("🎤 Escutando... Pressione Ctrl+C para parar\n")

        try:
            while self.is_listening:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    self.connection.send_media(ListenV1MediaMessage(data))
                except Exception as e:
                    print(f"\n⚠️  Erro no áudio: {e}")
                    break
        except KeyboardInterrupt:
            print("\n⏹️  Parando...")
        finally:
            self.stop()

    async def _start_microphone_async(self):
        """Iniciar captura do microfone (assíncrono)"""
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("🎤 Escutando... Pressione Ctrl+C para parar\n")

        try:
            while self.is_listening:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    await self.connection.send_media(ListenV2MediaMessage(data=data))
                    await asyncio.sleep(0.001)
                except Exception as e:
                    print(f"\n⚠️  Erro no áudio: {e}")
                    break
        except KeyboardInterrupt:
            print("\n⏹️  Parando...")
        finally:
            await self.stop_async()

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _on_open(self, *args):
        """Conexão aberta"""
        print("✅ Conectado ao Deepgram")

    def _on_close(self, *args):
        """Conexão fechada"""
        print("🔌 Conexão fechada")

    def _on_error(self, error, *args):
        """Erro na conexão"""
        print(f"❌ Erro: {error}")

    # ========================================================================
    # CONTROLE PÚBLICO
    # ========================================================================

    def stop(self):
        """Parar assistente (síncrono)"""
        self.is_listening = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.audio:
            self.audio.terminate()

        if self.connection:
            self.connection.finish()

        print("✅ Assistente parado")

    async def stop_async(self):
        """Parar assistente (assíncrono)"""
        self.is_listening = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.audio:
            self.audio.terminate()

        if self.connection:
            from deepgram.extensions.types.sockets import ListenV2ControlMessage
            await self.connection.send_control(
                ListenV2ControlMessage(type="CloseStream")
            )

        print("✅ Assistente parado")


# ========================================================================
# EXEMPLOS DE USO
# ========================================================================

def exemplo_callback(resultado: TranscriptionResult):
    """
    Exemplo de callback para processar comando.

    Aqui você integraria com seu agente/LLM.
    """
    print(f"\n💭 Processando comando: '{resultado.text}'")

    # Exemplo simples de comandos
    texto_lower = resultado.text.lower()

    if "horas" in texto_lower:
        from datetime import datetime
        hora = datetime.now().strftime("%H:%M")
        print(f"🕐 Agora são {hora}")

    elif "nome" in texto_lower and "seu" in texto_lower:
        print("🤖 Meu nome é Nero, seu assistente de voz!")

    elif "para" in texto_lower:
        print("👋 Até logo!")
        assistant.stop()

    else:
        print("❓ Não entendi o comando")


def exemplo_v1_endpointing():
    """Exemplo: V1 com endpointing (mais rápido)"""
    print("\n" + "="*60)
    print("EXEMPLO 1: V1 com Endpointing")
    print("="*60 + "\n")

    assistant = DeepgramVoiceAssistant(
        api_key="SUA_CHAVE_API_AQUI",
        language="pt-BR",
        detection_method=DetectionMethod.ENDPOINTING,
        on_transcript=exemplo_callback
    )

    assistant.start_v1(silence_duration=600)


def exemplo_v1_utterance_end():
    """Exemplo: V1 com utterance_end (mais preciso)"""
    print("\n" + "="*60)
    print("EXEMPLO 2: V1 com UtteranceEnd")
    print("="*60 + "\n")

    assistant = DeepgramVoiceAssistant(
        api_key="SUA_CHAVE_API_AQUI",
        language="pt-BR",
        detection_method=DetectionMethod.UTTERANCE_END,
        on_transcript=exemplo_callback
    )

    assistant.start_v1(silence_duration=1000)


async def exemplo_v2_voice_agent():
    """Exemplo: V2 Voice Agent API"""
    print("\n" + "="*60)
    print("EXEMPLO 3: V2 Voice Agent API")
    print("="*60 + "\n")

    assistant = DeepgramVoiceAssistant(
        api_key="SUA_CHAVE_API_AQUI",
        language="pt-BR",
        detection_method=DetectionMethod.VOICE_AGENT,
        on_transcript=exemplo_callback
    )

    await assistant.start_v2(
        eager_eot_threshold=0.5,
        eot_threshold=0.7,
        eot_timeout_ms=1000
    )


# ========================================================================
# MAIN
# ========================================================================

if __name__ == "__main__":
    import sys

    print("""
╔════════════════════════════════════════════════════════════╗
║         Deepgram Voice Assistant - Exemplo Prático         ║
╚════════════════════════════════════════════════════════════╝

Escolha o modo:
  1. V1 Endpointing (rápido, baseado em silêncio)
  2. V1 UtteranceEnd (preciso, eventos VAD)
  3. V2 Voice Agent API (automático, conversacional)
    """)

    if len(sys.argv) > 1:
        escolha = sys.argv[1]
    else:
        escolha = input("Escolha (1-3): ").strip()

    if escolha == "1":
        exemplo_v1_endpointing()
    elif escolha == "2":
        exemplo_v1_utterance_end()
    elif escolha == "3":
        asyncio.run(exemplo_v2_voice_agent())
    else:
        print("❌ Escolha inválida")
