# Security Model

Gravity AI trata automacao local como uma area sensivel. O modelo inicial e simples e conservador.

## Principios

- Ferramentas declaram permissoes e nivel de risco.
- Acoes destrutivas retornam `requires_confirmation` quando nao confirmadas.
- O backend executa comandos por handlers conhecidos, nao por strings livres geradas por LLM.
- Plugins declaram permissoes no manifesto antes de serem considerados carregaveis.

## Niveis de risco

- `safe`: leitura ou resposta sem efeito colateral.
- `low`: efeito local pequeno e reversivel.
- `medium`: abre programas, move dados ou afeta estado do sistema.
- `high`: altera configuracoes importantes ou toca areas sensiveis.
- `destructive`: exclui dados, encerra processos criticos ou modifica areas perigosas.

## Confirmacao

Ferramentas com `requires_confirmation=true` nao executam ate receberem `confirmed=true` em `ToolCall`. A UI deve mostrar nome da ferramenta, argumentos e risco antes de permitir a confirmacao.

## Fora do Marco 1

Sandbox de processo, assinatura de plugins, controle fino de ACLs e auditoria criptografada ficam para marcos posteriores.

