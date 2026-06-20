# Backend

Backend FastAPI responsavel por validar payloads, manter cadastros de atletas e dispositivos, controlar o historico de vinculos e persistir leituras de temperatura no PostgreSQL.

## Migracoes

Com a stack ativa, execute as migracoes pelo Docker Compose:

```bash
docker compose run --rm backend alembic upgrade head
```

O backend nao depende do Node-RED para persistencia. O Node-RED apenas encaminha eventos MQTT validos para a API HTTP.
