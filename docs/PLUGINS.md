# Plugin Guide

Plugins vivem em `plugins/<plugin-id>/` e sao descobertos por manifesto.

## Manifesto minimo

```json
{
  "id": "gravity.example",
  "name": "Example Plugin",
  "version": "0.1.0",
  "entrypoint": "plugin.py",
  "permissions": ["filesystem.read"],
  "commands": [
    {
      "name": "example.search",
      "description": "Searches example files.",
      "tool": "file.search"
    }
  ],
  "settings": {}
}
```

## Contrato

- `id`: identificador estavel e unico.
- `entrypoint`: arquivo relativo ao diretorio do plugin.
- `permissions`: capacidades solicitadas pelo plugin.
- `commands`: comandos expostos para o planejador ou UI.
- `settings`: configuracao declarativa inicial.

No Marco 1, plugins sao descobertos e validados, mas ainda nao executam codigo arbitrario isolado.

