# Quick Start Guide - Workflow System

Guia rápido para começar a usar o sistema de workflows.

## Comandos Disponíveis

```bash
/orchestrate-agents   # Orquestrar agentes (com suporte a workflows)
/create-workflow      # Criar novos workflows
```

## Workflows Incluídos

| Workflow | Uso | Comando |
|----------|-----|---------|
| **SimpleSdlc** | Features simples, bug fixes | `--workflow SimpleSdlc` |
| **TeamSdlc** | Features complexas, time | `--workflow TeamSdlc` |
| **QuickPatch** | Hotfixes rápidos | `--workflow QuickPatch` |

## Exemplos Práticos

### 1. Feature Simples (SimpleSdlc)

```bash
/orchestrate-agents "Add password reset feature" --workflow SimpleSdlc
```

**O que acontece:**
1. Cria plano em `specs/password-reset-feature.md`
2. Implementa seguindo o plano
3. Roda testes
4. Revisa contra especificação

**Tempo estimado:** 5-10 minutos

### 2. Feature Complexa (TeamSdlc)

```bash
/orchestrate-agents "Build real-time chat with WebSocket" --workflow TeamSdlc
```

**O que acontece:**
1. Cria plano com time em `specs/realtime-chat.md`
2. Orquestra múltiplos agentes:
   - Backend (WebSocket server)
   - Frontend (Chat UI)
   - Integration (Connect)
3. Roda testes unit + integração + e2e
4. Revisa implementação

**Tempo estimado:** 15-30 minutos

### 3. Bug Fix Rápido (QuickPatch)

```bash
/orchestrate-agents "Fix mobile menu not working" --workflow QuickPatch
```

**O que acontece:**
1. Cria plano de patch cirúrgico
2. Aplica o patch
3. Valida que funcionou

**Tempo estimado:** 2-5 minutos

## Criar Seu Próprio Workflow

### Passo 1: Criar o Workflow

```bash
/create-workflow DevOpsPipeline "Setup CI/CD pipeline"
```

**Será perguntado:**
- Nome do workflow (TitleCase)
- Descrição do que faz
- Sequência de comandos
- Requisitos de agentes

### Passo 2: Usar o Workflow

```bash
/orchestrate-agents "Setup GitHub Actions for this project" --workflow DevOpsPipeline
```

## Padrões Comuns

### Criar Nova Feature API

```bash
/orchestrate-agents "Create REST API endpoint for user management" --workflow SimpleSdlc
```

### Criar Componente Frontend

```bash
/orchestrate-agents "Build reusable button component with variants" --workflow SimpleSdlc
```

### Feature Full-Stack

```bash
/orchestrate-agents "Build admin dashboard with charts" --workflow TeamSdlc
```

### Hotfix de Produção

```bash
/orchestrate-agents "Fix login page crashing on Safari" --workflow QuickPatch
```

## Comparação de Workflows

| Aspecto | SimpleSdlc | TeamSdlc | QuickPatch |
|---------|-----------|----------|------------|
| **Complexidade** | Baixa | Média/Alta | Baixa |
| **Tempo** | 5-10 min | 15-30 min | 2-5 min |
| **Agentes** | 1 (sequencial) | 3-10 (paralelo) | 1 (rápido) |
| **Planejamento** | Simples | Com time | Mínimo |
| **Testes** | Unit | Unit + E2E | Validar |
| **Uso ideal** | 70% dos casos | 20% dos casos | 10% dos casos |

## Quando Usar Cada Workflow

### Use SimpleSdlc quando:
- ✅ Feature simples ou média
- ✅ Bug fix comum
- ✅ Refatoração localizada
- ✅ Tarefa de rotina
- ❌ Feature complexa com múltiplas partes
- ❌ Requer múltiplos especialistas

### Use TeamSdlc quando:
- ✅ Feature complexa
- ✅ Full-stack (frontend + backend)
- ✅ Pode paralelizar trabalho
- ✅ Requer especialistas diferentes
- ❌ Tarefa simples (overkill)
- ❌ Mudança rápida em um arquivo

### Use QuickPatch quando:
- ✅ Bug claro e isolado
- ✅ Hotfix de produção
- ✅ Fix rápido necessário
- ❌ Nova feature
- ❌ Refatoração (use SimpleSdlc)

## Orquestração Manual (Sem Workflow)

Se precisar de controle total:

```bash
/orchestrate-agents "Build complex distributed system"
```

Sem `--workflow`, o orquestrador:
1. Analisa requisitos
2. Design time de agentes
3. Cria estrutura de tarefas
4. Define dependências
5. Orquestra execução

## Troubleshooting

### Workflow não encontrado?

```bash
# Verificar que workflow existe
ls .claude/commands/workflows/

# Deve retornar:
# SimpleSdlc.md
# TeamSdlc.md
# QuickPatch.md
```

### Comandos falhando?

Testar comandos individualmente primeiro:

```bash
/plan "Test feature"
/implement "specs/test-feature.md"
/test
/review "specs/test-feature.md"
```

### Paralelização não funcionando?

Verificar se as tarefas são realmente independentes. Se compartilham arquivos, use sequencial.

## Próximos Passos

1. **Experimentar com tarefa simples**
   ```bash
   /orchestrate-agents "Add example function" --workflow SimpleSdlc
   ```

2. **Entender a estrutura dos workflows**
   ```bash
   cat .claude/commands/workflows/SimpleSdlc.md
   ```

3. **Criar workflow customizado**
   ```bash
   /create-workflow MyWorkflow "Minha descrição"
   ```

4. **Documentar workflows específicos do seu time**
   - Padrões de API
   - Padrões de frontend
   - Processos de deploy

## Referências Rápidas

- **Workflows disponíveis:** `.claude/commands/workflows/`
- **Orquestrador:** `.claude/commands/orchestrate-agents.md`
- **Criador de workflows:** `.claude/commands/create-workflow.md`
- **Sumário completo:** `.claude/commands/workflows/SUMMARY.md`
