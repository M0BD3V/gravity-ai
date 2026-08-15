# LLM Providers

Gravity AI usa adapters atras do contrato `LLMProvider`. No Marco 1.1, o runtime suporta:

- `local`: resposta de desenvolvimento sem internet ou custo.
- `gemini`: chamada real para a Gemini API do Google.
- `openai`: chamada real para a OpenAI Responses API.
- `auto`: usa Gemini quando `GEMINI_API_KEY` ou `GOOGLE_API_KEY` existe, depois OpenAI quando `OPENAI_API_KEY` existe; caso contrario usa `local`.

## Configuracao

Defina as variaveis antes de iniciar o backend:

```powershell
$env:GRAVITY_AI_LLM_PROVIDER = "gemini"
$env:GEMINI_API_KEY = "..."
$env:GRAVITY_AI_GEMINI_MODEL = "gemini-3.5-flash"
$env:GRAVITY_AI_GEMINI_STORE = "false"
python scripts/run_backend_api.py
```

Tambem funciona com `GOOGLE_API_KEY`.

O backend tambem le um arquivo `.env` na raiz do projeto. Ele ja foi criado com
Gemini como provider padrao; basta preencher `GEMINI_API_KEY` e reiniciar a API.

## OpenAI

```powershell
$env:GRAVITY_AI_LLM_PROVIDER = "openai"
$env:OPENAI_API_KEY = "sk..."
$env:GRAVITY_AI_OPENAI_MODEL = "gpt-5.6-terra"
$env:GRAVITY_AI_REASONING_EFFORT = "low"
$env:GRAVITY_AI_OPENAI_STORE = "false"
python scripts/run_backend_api.py
```

Modelos OpenAI recomendados para comecar:

- `gpt-5.6-terra`: equilibrio de inteligencia, velocidade e custo.
- `gpt-5.6-sol`: maior capacidade.
- `gpt-5.6-luna`: alto volume e menor custo.

O backend nunca expoe a chave ao frontend. O app desktop chama apenas a API local.
