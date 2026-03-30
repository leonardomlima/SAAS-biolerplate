# Operações e Deploy

## Variáveis obrigatórias

### Backend
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `ASAAS_API_KEY`
- `ASAAS_WEBHOOK_SECRET`
- `BREVO_API_KEY`
- `BREVO_SENDER_EMAIL`
- `BREVO_TEMPLATE_WELCOME_ID`
- `BREVO_TEMPLATE_RESET_ID`
- `BREVO_TEMPLATE_INVITE_ID`

### Frontend
- `VITE_API_URL`

## Execução local

```bash
make up
make migrate
make seed
```

## Checklist de segurança

- [ ] Definir `ALLOWED_HOSTS` para domínios de produção.
- [ ] Definir `CORS_ORIGINS` apenas para frontends autorizados.
- [ ] Configurar segredo forte para `JWT_SECRET_KEY`.
- [ ] Configurar `ASAAS_WEBHOOK_SECRET` e validar no painel ASAAS.
- [ ] Validar templates Brevo e IDs publicados.

## Observabilidade e auditoria

- Eventos de autenticação e billing gravados em `auditlog`.
- Falhas e retries de email gravados em `emaildelivery`.
- Eventos recebidos do ASAAS gravados em `asaaswebhookevent`.

## Deploy

- Backend: rodar migration Alembic antes de subir novas versões.
- Frontend: publicar build do Vite com `VITE_API_URL` de produção.
- Celery worker: obrigatório para envio assíncrono de emails.
