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
    - **Frontend**: [http://localhost:5173](http://localhost:5173)
    - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

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
