# Tidal Helper

A tool to help manage Tidal music playlists and songs.

> **Note:** This project is currently in early development.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLModel, Alembic
- **Frontend**: TypeScript, Vue.js 3, Pinia, Tailwind CSS
- **Database**: SQLite
- **Infrastructure**: Docker, Docker Compose

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

### Installation & Running

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd tidal-helper
    ```

2.  **Environment Setup:**
    Create a `.env` file from the example template:

    ```bash
    cp .env.example .env
    ```

3.  **Start the Application:**
    Run the following command to build and start the services:

    ```bash
    docker-compose up --build
    ```

4.  **Access the Application:**
    - **Frontend**: [http://localhost:22002](http://localhost:22002)
    - **Backend API Docs**: [http://localhost:22001/docs](http://localhost:22001/docs)

## Development

### Backend (Local)

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend (Local)

```bash
cd frontend
npm install
npm run dev
```

## Database Management

### Database Migrations with Alembic

The project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations.

#### Initialize Alembic (First Time Only)

If the `alembic` directory doesn't exist, initialize it:

```bash
cd backend
poetry run alembic init alembic
```

#### Create a New Migration

After modifying your SQLModel models, generate a new migration:

```bash
cd backend
poetry run alembic revision --autogenerate -m "Description of changes"
```

This will create a new migration file in `backend/alembic/versions/`.

#### Apply Migrations

To apply all pending migrations to the database:

```bash
cd backend
poetry run alembic upgrade head
```

#### Rollback Migrations

To rollback the last migration:

```bash
cd backend
poetry run alembic downgrade -1
```

To rollback to a specific revision:

```bash
cd backend
poetry run alembic downgrade <revision_id>
```

#### Check Current Migration Status

To see the current migration version:

```bash
cd backend
poetry run alembic current
```

To see migration history:

```bash
cd backend
poetry run alembic history
```

### Initialize Database (Alternative Method)

For quick database initialization without migrations, you can use the `init_db.py` script:

```bash
cd backend
poetry run python init_db.py
```

> **Note:** This creates all tables based on your SQLModel definitions but doesn't track migration history. For production use, prefer Alembic migrations.
