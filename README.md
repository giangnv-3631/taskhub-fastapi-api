# taskhub-fastapi-api

Task management REST API built with FastAPI, SQLAlchemy 2.x, Alembic and PostgreSQL.

## Features

- JWT authentication (register, login, current user)
- Roles: `admin`, `project_manager`, `member`
- Projects, tasks (filtering by status / priority, pagination), tags, bookmarks
- Task assignment and comments with author / project owner permissions
- Email notification on new comments, sent as a background task
- CORS, logging, Docker

## Run with Docker

```bash
cp .env.example .env    # set SECRET_KEY (at least 32 characters)
docker compose up --build
```

API docs: http://localhost:8000/docs

## Run locally

Requires Python 3.12 and PostgreSQL.

```bash
python -m venv venv
venv\Scripts\activate          # Linux / macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # set DATABASE_URL and SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Tests

Tests use a separate database `<database>_test`, created automatically on the server from `DATABASE_URL`.

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Environment variables

| Name | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL URL (`postgresql+psycopg://...`) |
| `SECRET_KEY` | — | JWT signing key, at least 32 characters |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime |
| `SMTP_HOST` | empty | Empty: emails are written to the log |
| `SMTP_PORT` | `1025` | SMTP port |
| `MAIL_FROM` | `TaskHub <noreply@taskhub.local>` | Sender address |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | Allowed frontend origins (JSON list) |
| `LOG_LEVEL` | `INFO` | Log level |

## Roles

New users are `member`. Change a role with SQL:

```sql
UPDATE users SET role = 'admin' WHERE username = '<username>';
UPDATE users SET role = 'project_manager' WHERE username = '<username>';
```
