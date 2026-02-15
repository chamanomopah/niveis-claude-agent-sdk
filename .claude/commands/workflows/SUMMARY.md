# Workflow System Summary

## O Que Foi Criado

Sistema completo de workflows reutilizáveis para orquestração de agentes no Claude Code.

## Estrutura de Arquivos

```
.claude/commands/
├── orchestrate-agents.md          # Comando principal de orquestração (ATUALIZADO)
├── create-workflow.md             # Novo comando para criar workflows
└── workflows/                     # Novo diretório de workflows
    ├── README.md                  # Documentação do sistema
    ├── SimpleSdlc.md              # Workflow SDLC simples
    ├── TeamSdlc.md                # Workflow SDLC com time
    └── QuickPatch.md              # Workflow de patch rápido
```

## Comandos Criados

### 1. `/create-workflow` - Criador de Workflows

**Uso:**
```bash
/create-workflow [WorkflowName] "[descrição]"
```

**O que faz:**
- Cria arquivos de workflow em `.claude/commands/workflows/`
- Define sequência de comandos
- Especifica requisitos de agentes
- Define estratégia paralela/sequencial

**Exemplo:**
```bash
/create-workflow FeatureDevelopment "Complete feature lifecycle with documentation"
```

### 2. `/orchestrate-agents` - Orquestrador com Suporte a Workflows (ATUALIZADO)

**Modos de operação:**

#### Modo Workflow (novo)
```bash
/orchestrate-agents "[objetivo]" --workflow [WorkflowName]
```

#### Modo Customizado (existente)
```bash
/orchestrate-agents "[objetivo]" [orientações]
```

**Workflows disponíveis:**
- `SimpleSdlc` - Plan → Implement → Test → Review
- `TeamSdlc` - Plan com time → Orquestrar → Test → E2E → Review
- `QuickPatch` - Patch → Implement → Validate

## Workflows Incluídos

### SimpleSdlc Workflow

**Propósito:** SDLC básico para tarefas simples

**Sequência:**
1. `plan` - Criar plano de implementação
2. `implement` - Executar o plano
3. `test` - Rodar testes
4. `review` - Revisar contra especificação

**Quando usar:**
- Features simples
- Bug fixes
- Refator pequenas
- Chores

**Exemplo:**
```bash
/orchestrate-agents "Add password reset feature" --workflow SimpleSdlc
```

### TeamSdlc Workflow

**Propósito:** SDLC baseado em time com execução paralela

**Sequência:**
1. `plan_w_team` - Criar plano com time (com definição de agentes)
2. `orchestrate-agents` - Orquestrar time para executar
3. `test` - Rodar testes
4. `test-e2e` - Testes end-to-end
5. `review` - Revisar implementação

**Quando usar:**
- Features de média/alta complexidade
- Desenvolvimento full-stack
- Tarefas que podem ser paralelizadas
- Múltiplos especialistas necessários

**Exemplo:**
```bash
/orchestrate-agents "Build real-time chat feature" --workflow TeamSdlc
```

**Fluxo de execução:**
```
Plan (com time)
    ↓
Orquestrar (múltiplos agentes em paralelo)
    ├─ Backend Agent
    ├─ Frontend Agent
    └─ Database Agent
    ↓
Test (unit + integration)
    ↓
E2E Test (user journeys)
    ↓
Review (vs spec)
```

### QuickPatch Workflow

**Propósito:** Workflow rápido de bug fix

**Sequência:**
1. `patch` - Criar plano de patch cirúrgico
2. `implement` - Aplicar patch
3. `test` - Validar fix

**Quando usar:**
- Bugs com sintomas claros
- Hotfixes
- Correções rápidas

**Exemplo:**
```bash
/orchestrate-agents "Fix mobile navigation menu" --workflow QuickPatch
```

## Princípios de Orquestração

### Orquestrador vs Executors

**Orquestrador (Team Lead):**
- NUNCA escreve código diretamente
- Usa ferramentas Task* para coordenação
- Deploy agentes especialistas
- Monitora progresso
- Coordena comunicação

**Executores (Specialist Agents):**
- Executam trabalho específico
- Escrevem código, criam arquivos
- Testam e validam
- Reportam resultados

### Padrões de Coordenamento

**Sequential:**
```
Task 1 → Task 2 → Task 3
```

**Parallel:**
```
       Task 1
         ↓
    Task 2   Task 3
         ↓       ↓
         Task 4
```

**Diamond:**
```
    Task 1
      ↓
Task 2  Task 3
      ↓
    Task 4
```

## Exemplos de Uso Completos

### Exemplo 1: Feature Simples

```bash
# Usar SimpleSdlc workflow
/orchestrate-agents "Add user profile page" --workflow SimpleSdlc
```

**Resultado:**
```
✅ SimpleSdlc Workflow Started

Step 1: Planning...
→ Plan: specs/user-profile-page.md

Step 2: Implementing...
→ Profile component created
→ Data fetching added
→ Styles applied

Step 3: Testing...
→ All tests passing ✓

Step 4: Review...
→ Matches spec ✓

✅ Complete
```

### Exemplo 2: Feature Complexa

```bash
# Usar TeamSdlc workflow
/orchestrate-agents "Build WebSocket notifications" --workflow TeamSdlc
```

**Resultado:**
```
✅ TeamSdlc Workflow Started

Step 1: Planning with team...
→ Plan: specs/websocket-notifications.md
→ Team: builder-backend, builder-frontend, validator
→ Tasks: 8 tasks (3 parallel tracks)

Step 2: Orchestrating agents...
→ Deploying builder-backend (WebSocket setup)...
→ Deploying builder-frontend (notification UI) [PARALLEL]...
✓ Both completed
→ Deploying builder-integration (connect frontend to backend)...
✓ Completed

Step 3: Testing...
→ Unit tests: 134 passing ✓

Step 4: E2E Testing...
→ User journeys: 8 passing ✓

Step 5: Review...
→ Matches spec ✓

✅ Complete
```

### Exemplo 3: Criar Novo Workflow

```bash
# Criar workflow customizado
/create-workflow FeatureDevelopment "Complete SDLC with documentation"
```

**Resultado:**
```
## Workflow Created

Name: FeatureDevelopment
File: .claude/commands/workflows/FeatureDevelopment.md

Command Sequence:
1. plan_w_team
2. orchestrate-agents
3. test
4. test-e2e
5. review
6. (new) document

Usage:
/orchestrate-agents "[objective]" --workflow FeatureDevelopment
```

## Integração com SDLC

O sistema de workflows segue o padrão SDLC do lesson-003-analysis.md:

```
Meta-Prompt → Plan → Implement → Test → Review
```

**Workflow como Higher-Order Prompt:**
- Workflow define o padrão (template)
- Objetivo do usuário é o input
- Orquestrador executa seguindo o workflow
- Resultado é a implementação completa

## Próximos Passos

1. **Testar workflows existentes**
   ```bash
   /orchestrate-agents "Simple test feature" --workflow SimpleSdlc
   ```

2. **Criar workflows customizados**
   ```bash
   /create-workflow DevOpsWorkflow "CI/CD pipeline setup"
   ```

3. **Combinar workflows**
   - Workflows podem referenciar outros workflows
   - Criar hierarquias de workflows

4. **Documentar padrões específicos do projeto**
   - Criar workflows para padrões comuns
   - Ex: `ApiEndpoint`, `FrontendComponent`, `DatabaseMigration`

## Referências

- `.claude/commands/orchestrate-agents.md` - Documentação completa do orquestrador
- `.claude/commands/workflows/README.md` - Guia de workflows
- `.claude/commands/create-workflow.md` - Como criar workflows
- `c:\.nero\docs\tac\analysis\lesson-003-analysis.md` - SDLC e meta-prompts
- `c:\Users\JOSE\.claude\skills_stop\CreateSkill\SKILL.md` - Sistema de skills
