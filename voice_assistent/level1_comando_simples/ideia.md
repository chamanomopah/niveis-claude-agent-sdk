# NERO - Assistente de Voz com Claude Agent SDK

**Nível:** 1 - Comando Simples
**Localização:** `C:\Users\JOSE\Downloads\niveis_claude_agent_SDK\voice_assistent\level1_comando_simples`

---

## 🎯 Visão Geral

Sistema simples de assistente de voz usando **Claude Agent SDK** com interação 100% por voz.

**Características principais:**
- Input do usuário 100% por voz
- Wake word detection sempre ativa (offline)
- Transcrição de alta qualidade com Deepgram
- Respostas em áudio com Cartesia TTS
- Logs detalhados no terminal para troubleshooting

---

## 🔄 Fluxo de Trabalho (Pipeline)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. STT Fraco (Offline) - Wake Word Detection                   │
│     Aguardando: "NERO OUVIR"                                    │
│     Biblioteca: speech_recognition + pyaudio + pocketsphinx    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. STT Forte (Deepgram) - Transcrição do Prompt               │
│     Início: "NERO OUVIR"                                        │
│     Fim: "NERO ENVIAR" ou timeout (10 min)                     │
│     STT fraco aguarda stop word em background                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. Claude Code Agent                                          │
│     Processa o prompt transcrito                                │
│     Executa tasks/tools necessárias                             │
│     Hook final: gera resumo do que foi feito                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. TTS (Cartesia) - Resposta em Áudio  (hook do claude code)                       │
│     Gera áudio do resumo final                                  │
│     Idioma: Português brasileiro                               │
│     Estilo: Mínimas palavras possíveis                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Exemplo de Uso

```bash
# 1. Iniciar o script
uv run nero_assistant.py
```

```
Usuário fala: "NERO OUVIR"
  → Sistema detecta wake word ✓
  → Deepgram é ativado

Usuário fala: "leia o arquivo de texto chamado claude code docs e crie um arquivo resumido"
  → Deepgram transcreve em tempo real

Usuário fala: "NERO ENVIAR"
  → Para transcrição
  → Envia prompt para Claude Code Agent
  → Agent executa task
  → Cartesia gera áudio do resultado: "Arquivo resumo criado com sucesso" (hook do claude code)
```

---

## 🛠️ Tech Stack

### STT Fraco (Wake Word Detection)
- **Biblioteca:** `speech_recognition`
- **Dependências:** `pyaudio`, `pocketsphinx`
- **Instalação:**
  ```bash
  uv add speechrecognition pyaudio
  ```
- **Características:**
  - ✅ Zero download de modelo (Pocketsphinx embutido)
  - ✅ Offline e sempre ativo
  - ✅ Suporte nativo a português brasileiro (`language='pt-BR'`)
  - ✅ Leve: <50MB RAM
  - ✅ CPU mínima

### STT Forte (Transcrição)
- **Serviço:** Deepgram API
- **Uso:** Transcrição precisa do prompt completo
- **Nota:** API REST simples (sem SDK complexo)

### TTS (Resposta em Áudio)
- **Serviço:** Cartesia API (hook do claude code)
- **Idioma:** Português brasileiro
- **Nota:** API REST simples (sem SDK complexo)

### Agente
- **SDK:** Claude Agent SDK
- **Plano:** Usar configuração existente do Claude Code (não usar Anthropic API direta)

---

## 📋 Requisitos Funcionais

### Obrigatórios
- [ ] Wake word "NERO OUVIR" ativa modo de escuta
- [ ] Stop word "NERO ENVIAR" envia prompt para o agente
- [ ] Timeout máximo de 10 minutos entre wake/stop word
- [ ] STT fraco fica em background aguardando stop word
- [ ] Claude Code Agent responde em português
- [ ] TTS gera áudio em português com resumo mínimo

### Flags e Configurações
```bash
--dangerously-skip-permissions  # Agente executa sem limitações
--locale=pt-BR                   # Respostas em português
```

### Hooks do Claude Code
- **Hook final:** Quando agente finaliza sessão → Chamar Cartesia TTS
- **Output:** Resumo mínimo do que foi executado

---

## 📊 Logs no Terminal

Usar `rich.terminal` para logs coloridos e estruturados:

```python
[INFO] Sistema iniciado - Aguardando wake word...
[LISTENING] 🔊 STT fraco ativo - Detectando "NERO OUVIR"
[WAKE WORD DETECTED] ✓ "NERO OUVIR" - Ativando Deepgram...
[RECORDING] 🎙️ Gravando prompt (timeout: 10 min)...
[TRANSCRIBING] 📝 Deepgram transcrevendo áudio...
[TRANSCRIPT] "leia o arquivo de texto chamado claude code docs..."
[STOP WORD] ✓ "NERO ENVIAR" - Enviando para agente...
[AGENT] 🤖 Claude Code Agent processando...
[TOOL] Read: arquivo.txt (linhas 1-50)
[TOOL] Write: resumo.txt (criado)
[COMPLETE] ✅ Task finalizada - Gerando áudio...
[TTS] 🎵 Cartesia: "Arquivo resumo criado"
[DONE] ✓ Voltando ao modo de escuta...
```

**Logs obrigatórios:**
- Captação de áudio (início/fim)
- Texto transcrito pelo Deepgram
- Tools usadas pelo agente
- Status de cada etapa
- Erros e warnings

---

## 📁 Estrutura de Arquivos

```
level1_comando_simples/
├──modules
   ├──tts.py
   ├──stt_fraco.py
   ├──stt_forte.py
├── nero_assistant.py       # Script principal (uv script único)
├── .env                     # API keys (Deepgram, Cartesia)
├── ideia.md                # Este documento
└── README.md                # Instruções de uso
```

**Chaves necessárias no `.env`:**
```env
DEEPGRAM_API_KEY=xxx
CARTESIA_API_KEY=xxx
```

---

## 📚 Contexto de Desenvolvimento

### SDK Python
Contexto: `../../ai_docs/sdk-python.md`

### UV Scripts
Contexto: `../../ai_docs/uv-scripts.md`

### claude code hooks pra cartesia
Contexto: `../../ai_docs/sdk-hooks.md`


---

## ⚠️ Notas Importantes

### Compatibilidade
- **Deepgram e Cartesia:** Usar apenas API REST simples (sem SDKs complexos)
- **STT fraco:** speech_recognition é perfeito para wake word offline
- **Não usar:** Anthropic API direta (usar plano Claude Code existente)

### Limitações
- Timeout de 10 minutos entre wake/stop word
- STT fraco tem acurácia menor (suficiente para wake word)
- Deepgram requer conexão com internet

### Troubleshooting
- Verificar logs detalhados para identificar problemas
- Testar wake word em ambiente silencioso
- Verificar APIs keys no `.env`
- Confirmar que microfone está funcionando

---

## 🚀 Próximos Passos

1. Criar arquivo `.env` com API keys
2. Implementar script `nero_assistant.py` seguindo contexto dos documentos de referência
3. Testar wake word detection isoladamente
4. Integrar Deepgram para transcrição
5. Implementar Claude Code Agent com hook final
6. Adicionar TTS Cartesia para resposta
7. Testar pipeline completo end-to-end
8. Otimizar logs e troubleshooting

---

**Data de criação:** 2026-02-12
**Versão:** 1.0
**Status:** Especificação
