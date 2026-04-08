Alembic migrations for KubeWise. Run from the `backend` directory:

```bash
alembic upgrade head
```

Ensure `DATABASE_URL_SYNC` in `.env` points at your Postgres instance.
