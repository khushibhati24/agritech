# Agritech Marketplace

Backend for the Agritech Marketplace project built with FastAPI and PostgreSQL.

## Folder Structure

agri/
├── README.md
├── .gitignore
│
└── backend/
    ├── .env
    ├── .venv/
    ├── Dockerfile
    ├── alembic.ini
    ├── requirements.txt
    │
    ├── alembic/
    │   ├── env.py
    │   └── versions/
    │       └── 001_initial.py
    │
    └── app/
        ├── main.py
        ├── api/
        ├── core/
        ├── db/
        ├── models/
        └── schemas/

## Setup

### Step 1 — Go to the backend

cd backend

### Step 2 — Activate the virtual environment

.\.venv\Scripts\Activate.ps1

### Step 3 — Install dependencies

pip install -r requirements.txt

### Step 4 — Configure PostgreSQL

Make sure PostgreSQL is running and create a database named:

agritech

### Step 5 — Create the environment file

Create:

backend/.env

Add your database URL and other required configuration.

### Step 6 — Run database migrations

python -m alembic upgrade head

### Step 7 — Start the server

uvicorn app.main:app --reload

### Step 8 — Open the API

http://127.0.0.1:8000

### Step 9 — Open Swagger

http://127.0.0.1:8000/docs

## Currently Working

- FastAPI server
- PostgreSQL connection
- SQLAlchemy database setup
- Alembic migrations
- Initial database schema
- Root endpoint
- Health endpoint
- Swagger documentation

More features will be implemented and tested as development continues.
