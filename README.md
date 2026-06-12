# AI Vacation Planner API

A RESTful backend for an intelligent travel assistant that helps users plan trips end-to-end. Phase 1 covers user authentication, trip management, and itinerary creation. The architecture is designed to grow into a full AI agent with conversational memory, real-time data, and multimodal input — without breaking changes.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | SQLite (dev) → PostgreSQL-ready |
| Migrations | Alembic |
| Auth | JWT via PyJWT, passwords with Argon2 (pwdlib) |
| Runtime | Python 3.13, uvicorn, aiosqlite |
| Package manager | uv |

---

## Architecture

The project follows a **layered architecture** inspired by Domain-Driven Design (DDD). Each layer has a single responsibility and only talks to the layer below it.

```
HTTP Request
     │
     ▼
┌─────────────────────────────┐
│         API Layer           │  app/api/v1/
│  Routers – parse HTTP,      │  auth.py · trip.py · itinerary.py
│  call service, return HTTP  │
└────────────┬────────────────┘
             │ calls
             ▼
┌─────────────────────────────┐
│      Application Layer      │  app/application/
│  Services – business logic, │  services/user.py
│  validation, transactions   │  services/trip.py
│                             │  services/itinerary.py
│  Schemas – Pydantic DTOs    │  schemas/user.py
│  (request / response)       │  schemas/trip.py
│                             │  schemas/itinerary.py
└────────────┬────────────────┘
             │ reads / writes
             ▼
┌─────────────────────────────┐
│       Domain Layer          │  app/domain/models/
│  SQLModel table definitions │  user.py · trip.py · itinerary.py
│  (source of truth for DB    │
│   schema and types)         │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│        Core Layer           │  app/core/
│  Config, DB session,        │  config.py · database.py · security.py
│  JWT / auth middleware      │
└─────────────────────────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

### 1. Clone the repository

```bash
git clone <repo-url>
cd ai-vacation-planner-api
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the values:

```env
# Generate a secure key with: openssl rand -hex 32
SECRET_KEY=your-secret-key-at-least-32-chars

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
env=development
DATABASE_URL=sqlite+aiosqlite:///./ai_vacation_planner.db
```

### 4. Apply database migrations

```bash
uv run alembic upgrade head
```

This creates the SQLite database file and all tables (`user`, `trip`, `itinerary`).

### 5. Run the development server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`  
Alternative docs (ReDoc): `http://localhost:8000/redoc`

### 6. Quick smoke test

```bash
# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "Secret1!"}'

# Get a token
curl -X POST http://localhost:8000/auth/token \
  -F "username=alice" -F "password=Secret1!"

# Use the token for authenticated requests
curl http://localhost:8000/trips \
  -H "Authorization: Bearer <token>"
```

### Creating a new migration (after changing a model)

```bash
uv run alembic revision --autogenerate -m "describe_your_change"
uv run alembic upgrade head
```

---

## Roadmap

| Phase | Features |
|-------|---------|
| **1 (current)** | User auth, Trip CRUD, Itinerary CRUD |
| **2** | AI itinerary generation via Claude API, conversational memory |
| **3** | Real-time enrichment: weather, maps, pricing |
| **4** | RAG (Retrieval-Augmented Generation) for destination knowledge |
| **5** | Multimodal input (images, voice), evaluation framework, production hardening |
