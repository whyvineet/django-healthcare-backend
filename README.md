# Django Healthcare Backend

A REST API backend for healthcare management... handling doctors, patients, and doctor-patient mappings... built with Django and PostgreSQL.

---

## Stack

| | |
|---|---|
| **Language** | Python 3.11 |
| **Framework** | Django 5.2 + Django REST Framework |
| **Auth** | JWT via `djangorestframework-simplejwt` |
| **Database** | PostgreSQL (Psycopg 3) |
| **Dependencies** | `uv` |
| **Container** | Docker + Docker Compose |

---

## Setup

```powershell
# 1. Copy env template and fill in your values
Copy-Item .env.example .env

# 2. Generate a safe secret key
uv run python -c "import secrets, string; chars = string.ascii_letters + string.digits + '-_~'; print(''.join(secrets.choice(chars) for _ in range(64)))"
```

---

## Running

**With Docker (recommended)**
```powershell
docker compose up -d                          # start db + web
docker compose logs -f web                    # tail logs
docker compose exec web uv run --no-sync python manage.py check --database default
docker compose down                           # stop (data preserved)
docker compose down -v                        # stop + wipe database volume
```

**Locally (requires a running PostgreSQL)**
```powershell
uv run python manage.py check
uv run python manage.py runserver
```

Available at **http://127.0.0.1:8000/**
