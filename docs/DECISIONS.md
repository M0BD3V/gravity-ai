# Technical Decisions

## ADR-001: Monorepo modular

O projeto inicia como monorepo para manter contratos, backend e desktop sincronizados. Cada pacote continua com fronteiras explicitas para permitir extracao futura.

## ADR-002: Tauri como desktop alvo

Tauri foi escolhido por ser leve, moderno e adequado para um assistente desktop nativo. Rust/Cargo sao pre-requisitos para executar o shell Tauri, mas o frontend Vite pode ser desenvolvido separadamente enquanto Rust nao estiver instalado.

## ADR-003: Backend Python sem dependencia obrigatoria no Marco 1

O backend inicial usa bibliotecas padrao para API local, SQLite, contratos e testes. Isso reduz atrito no primeiro boot e evita bloquear a arquitetura em frameworks antes de estabilizar os contratos.

## ADR-004: Toda acao real passa por ferramentas

A IA nao executa comandos diretamente. Ela produz intencoes que sao convertidas em `ToolCall`, avaliadas por politica de seguranca e executadas por handlers registrados.

## ADR-005: SQLite primeiro, repositorios sempre

SQLite atende ao produto local. A camada `storage` mantem SQL e persistencia isolados para facilitar migracao para PostgreSQL quando houver sincronizacao, multi-dispositivo ou times.

