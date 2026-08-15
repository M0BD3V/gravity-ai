# Gravity AI

Gravity AI e uma fundacao profissional para um assistente inteligente de Windows, com foco em automacao real do computador, memoria, ferramentas seguras e plugins independentes.

Este marco cria o monorepo inicial com:

- Backend Python modular e testavel.
- Frontend React + TypeScript preparado para Tauri.
- Contratos compartilhados para ferramentas, plugins, LLM e memoria.
- Sistema inicial de ferramentas com classificacao de risco e confirmacao.
- Loader de plugins por manifesto.
- API local para o app desktop.
- Documentacao tecnica inicial.

## Estrutura

```text
gravity-ai/
  apps/desktop/         # React, TypeScript, Vite e Tauri
  backend/src/          # Runtime Python do assistente
  docs/                 # Arquitetura, seguranca, plugins e roadmap
  packages/shared/      # Tipos TypeScript compartilhados
  plugins/              # Plugins instalados/localizados por manifesto
  tests/backend/        # Testes do backend e contratos
```

## Pre-requisitos

- Python 3.12+ recomendado.
- Node.js 20+ recomendado.
- Rust + Cargo para executar ou empacotar o Tauri.

No ambiente atual, Python e Node estao disponiveis. Rust/Cargo precisam ser instalados antes de rodar `npm run tauri:dev`.

## Comandos

```powershell
npm install
npm run build
npm run test
npm run backend:test
python -m gravity_ai.api
```

Para importar o backend diretamente sem instalacao editavel:

```powershell
$env:PYTHONPATH = "backend/src"
python -m gravity_ai.api
```

Por padrao, a API local sobe em `http://127.0.0.1:8765`.

## Respostas reais com LLM

Sem chave, o backend usa um provedor local de desenvolvimento. Para ativar respostas reais:

```powershell
$env:GEMINI_API_KEY = "..."
$env:GRAVITY_AI_LLM_PROVIDER = "gemini"
$env:GRAVITY_AI_GEMINI_MODEL = "gemini-3.5-flash"
python scripts/run_backend_api.py
```

Veja [docs/LLM.md](docs/LLM.md).

Tambem da para preencher `GEMINI_API_KEY` no arquivo local `.env` da raiz do projeto
e reiniciar o backend.

## Principios

- A IA escolhe ferramentas; ela nao executa comandos diretamente.
- Acoes destrutivas exigem confirmacao explicita.
- Plugins declaram permissoes e comandos por manifesto.
- Storage inicia em SQLite, com repositorios isolados para migracao futura.
- Frontend e backend se comunicam por contratos estaveis.
