# Deepgram: Comparativo de Métodos de Detecção de Fala

## Visão Geral

O Deepgram oferece **três métodos principais** para detectar quando um usuário terminou de falar em tempo real. Esta comparação ajuda a escolher o melhor método para seu caso de uso.

---

## Métodos Comparados

| Método | API | Precisão | Latência | Complexidade | Caso de Uso |
|--------|-----|----------|----------|--------------|-------------|
| **Endpointing** | V1 | Média | Baixa | Baixa | Comandos rápidos |
| **UtteranceEnd** | V1 | Alta | Média | Média | Assistentes gerais |
| **Voice Agent EOT** | V2 | Muito Alta | Variável | Baixa | Conversação natural |

---

## 1. Endpointing (V1)

### Como Funciona
Detecta pausas na fala baseado em um tempo de silêncio configurável.

### Configuração
```python
with client.listen.v1.connect(
    endpointing=600,  # 600ms de silêncio
    interim_results=True,
) as connection:
    # ...
```

### Detecção
```python
def on_message(message):
    speech_final = getattr(message, 'speech_final', False)

    if speech_final:
        print("✅ Usuário terminou de falar!")
        # Processar comando
```

### Vantagens ✅
- **Implementação simples**
- **Baixa latência** (rápido)
- **Feedback visual em tempo real**
- **Boa para comandos curtos**

### Desvantagens ❌
- **Pode finalizar cedo demais** (pausas naturais)
- **Menos preciso** para frases longas
- **Requer ajuste fino** do tempo de silêncio

### Quando Usar
- Comandos de voz simples ("Ligar a luz", "Tocar música")
- Aplicações que requerem resposta rápida
- Feedback visual durante a fala

### Valores Recomendados
```python
# Comandos curtos
endpointing=400  # 400ms

# Conversação normal
endpointing=600  # 600ms

# Ditado ou fala mais pausada
endpointing=1000  # 1s
```

---

## 2. UtteranceEnd Events (V1)

### Como Funciona
Usa VAD (Voice Activity Detection) avançado para detectar o final real de uma utterance, considerando contexto e pausas naturais.

### Configuração
```python
with client.listen.v1.connect(
    interim_results=True,       # Obrigatório
    utterance_end_ms="1000",    # Tempo após última palavra
    vad_events=True,            # Obrigatório
    endpointing=300,            # Menor que utterance_end
) as connection:
    # ...
```

### Detecção
```python
def on_message(message):
    msg_type = getattr(message, "type", "Unknown")

    if msg_type == "SpeechStarted":
        print("🗣️ Usuário começou a falar")

    elif msg_type == "UtteranceEnd":
        print("✅ UTTERANCE FINALIZADA!")
        # Processar comando completo aqui
```

### Vantagens ✅
- **Mais preciso** que endpointing
- **Detecta pausas naturais**
- **Menos falsos positivos**
- **Eventos VAD informativos**
- **Boa para frases complexas**

### Desvantagens ❌
- **Maior latência** (espera mais tempo)
- **Requer mais configurações**
- **Sofisticado demais** para casos simples

### Quando Usar
- Assistentes de voz gerais (Siri, Alexa style)
- Aplicações que precisam de transcrições completas
- Quando a precisão é mais importante que velocidade
- Frases com pausas naturais

### Valores Recomendados
```python
# Conversação natural
utterance_end_ms="1000"  # 1s
endpointing=300

# Fala mais lenta/pausada
utterance_end_ms="1500"  # 1.5s
endpointing=500
```

---

## 3. Voice Agent API - EOT Detection (V2)

### Como Funciona
API V2 otimizada para voice agents com detecção automática de turnos conversacionais usando IA.

### Configuração
```python
with client.listen.v2.connect(
    model="flux-general-en",
    eager_eot_threshold="0.5",   # Threshold eager
    eot_threshold="0.7",          # Threshold conservador
    eot_timeout_ms="1000",        # Timeout máximo
) as connection:
    # ...
```

### Detecção
```python
def on_message(message):
    msg_type = getattr(message, "type", "Unknown")

    if msg_type == "UserStartedSpeaking":
        print("🗣️ Usuário falando...")

    elif msg_type == "ConversationText":
        print(f"📝 {message.content}")

    elif msg_type == "AgentThinking":
        print("🤔 Usuário parou, processando...")
        # Aqui o EOT foi detectado automaticamente
```

### Vantagens ✅
- **Mais inteligente** (usa IA)
- **Detecção automática** de turnos
- **Otimizado para conversação**
- **Menos configuração manual**
- **Eventos ricos** (thinking, speaking, etc.)
- **Melhor para voice agents**

### Desvantagens ❌
- **API mais nova** (menos documentada)
- **Menos controle** granular
- **Pode ser overkill** para casos simples
- **Modelos específicos** (flux-*)

### Quando Usar
- Voice agents conversacionais
- Chatbots de voz
- Aplicações de call center
- Quando experiência natural é prioridade

### Valores Recomendados
```python
# Conversação rápida
eager_eot_threshold="0.5"
eot_threshold="0.7"
eot_timeout_ms="1000"

# Conversação pausada/reflexiva
eager_eot_threshold="0.3"
eot_threshold="0.8"
eot_timeout_ms="1500"
```

---

## Comparação de Latência

| Método | Tempo Médio de Detecção |
|--------|------------------------|
| Endpointing (400ms) | 400-600ms |
| Endpointing (600ms) | 600-800ms |
| UtteranceEnd (1000ms) | 1000-1500ms |
| Voice Agent EOT | 800-1200ms (variável) |

---

## Fluxograma de Decisão

```
          Precisa de resposta rápida?
                 |
        +--------+--------+
        |                 |
       SIM               NÃO
        |                 |
        |         É uma conversa natural?
        |                 |
        |        +--------+--------+
        |        |                 |
        |       NÃO               SIM
        |        |                 |
  Usar ENDPOINTING      Usar VOICE AGENT (V2)
  (V1, 400-600ms)       (EOT automático)
        |
        |
   Fala é complexa?
        |
   +----+----+
   |         |
  NÃO       SIM
   |         |
   |    Usar UTTERANCEEND (V1)
   |    (com VAD events)
```

---

## Exemplos de Código Comparativo

### Cenário: Assistente Pessoal

**Endpointing (V1)**
```python
# Rápido, mas pode cortar frases
assistant.start_v1(
    silence_duration=500  # 500ms
)

# Usuário: "Ligar... [pausa] a luz do quarto"
# Resultado: "Ligar" (corta cedo demais) ❌
```

**UtteranceEnd (V1)**
```python
# Mais preciso, espera frase completa
assistant.start_v1(
    silence_duration=1000,  # 1s
    method="utterance_end"
)

# Usuário: "Ligar... [pausa] a luz do quarto"
# Resultado: "Ligar a luz do quarto" ✅
```

**Voice Agent (V2)**
```python
# Inteligente, detecta intenção
await assistant.start_v2(
    eot_threshold="0.7"
)

# Usuário: "Ligar... [pausa] a luz do quarto"
# Resultado: "Ligar a luz do quarto" ✅
# Plus: Entende contexto conversacional
```

---

## Recomendações por Caso de Uso

### 🏠 Smart Home / Domótica
**Método**: Endpointing (V1)
**Tempo**: 400-600ms
**Por quê**: Comandos curtos, resposta rápida

```python
endpointing=500  # Rápido
```

### 📞 Assistente Pessoal (Siri/Alexa)
**Método**: UtteranceEnd (V1) ou Voice Agent (V2)
**Tempo**: 1000ms / Auto
**Por quê**: Frases completas, compreensão de contexto

```python
utterance_end_ms="1000"  # V1
# ou
eot_threshold="0.7"  # V2
```

### 🎮 Games / Interatividade
**Método**: Endpointing (V1)
**Tempo**: 300-500ms
**Por quê**: Latência crítica

```python
endpointing=400  # Muito rápido
```

### 📞 Call Center / Atendimento
**Método**: Voice Agent (V2)
**Tempo**: Auto
**Por quê**: Conversação natural, análise de sentimento

```python
eot_threshold="0.8"  # Mais conservador
```

### 🎙️ Ditado / Transcrição
**Método**: UtteranceEnd (V1)
**Tempo**: 1500-2000ms
**Por quê**: Paixas naturais longas, precisão máxima

```python
utterance_end_ms="2000"  # Muito paciente
```

### 🔧 Controle de Dispositivos
**Método**: Endpointing (V1)
**Tempo**: 600-800ms
**Por quê**: Equilíbrio entre velocidade e precisão

```python
endpointing=700
```

---

## Performance e Custos

### Uso de API
- **V1** é geralmente **mais barato** que V2
- **V2** pode ter **custos mais altos** mas recursos avançados

### Uso de Recursos
- **Endpointing**: Menos processamento no servidor
- **UtteranceEnd**: Processamento moderado (VAD)
- **Voice Agent**: Maior processamento (IA de turno)

---

## Migração entre Métodos

### De Endpointing para UtteranceEnd

```python
# ANTES (Endpointing)
with client.listen.v1.connect(
    endpointing=600,
    interim_results=True,
) as conn:
    if speech_final:
        process()

# DEPOIS (UtteranceEnd)
with client.listen.v1.connect(
    interim_results=True,
    utterance_end_ms="1000",
    vad_events=True,
    endpointing=300,  # Menor!
) as conn:
    if msg_type == "UtteranceEnd":
        process()
```

### De V1 para V2

```python
# ANTES (V1 UtteranceEnd)
with client.listen.v1.connect(
    model="nova-3",
    utterance_end_ms="1000",
    vad_events=True,
) as conn:
    # ...

# DEPOIS (V2 Voice Agent)
with client.listen.v2.connect(
    model="flux-general-en",
    eot_threshold="0.7",
    eot_timeout_ms="1000",
) as conn:
    # ...
    # V2 gerencia EOT automaticamente
```

---

## Dicas de Otimização

### 1. Ajuste Dinâmico
```python
# Ajustar baseado no contexto
def get_silence_duration(context):
    if context == "comando_curto":
        return 400
    elif context == "pergunta":
        return 800
    else:
        return 600
```

### 2. Combinação de Métodos
```python
# Usar endpointing para feedback visual
# Usar utterance_end para processamento real
if speech_final:
    update_ui()  # Feedback rápido

if utterance_end:
    process_command()  # Processamento real
```

### 3. Timeout como Fallback
```python
# Sempre ter um timeout máximo
max_silence = 2000  # 2s máximo
if time_silence > max_silence:
    force_finalize()
```

---

## Conclusão

| Use | Quando |
|-----|--------|
| **Endpointing** | Precisa de resposta rápida, comandos simples |
| **UtteranceEnd** | Precisa de precisão, frases complexas |
| **Voice Agent V2** | Conversação natural, experiência avançada |

**Regra geral**: Comece com **UtteranceEnd** (V1) para a maioria dos casos de assistente de voz. Migre para **Voice Agent** (V2) se precisar de recursos conversacionais avançados.

---

**Última atualização**: 2025-02-15
