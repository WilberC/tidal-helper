## 💾 Software Project Specification

This document outlines the technical details of the Tidal Helper project, including its architecture, features, and implementation details.
- This is a living document that will be updated as the project progresses and new features are added.
- It is not a final document so it is subject to change and can be changed at any time if needed.

---

### 1. Project Overview

- **Project Name:** Tidal Helper
- **Start Version:** 0.1.0
- **Short Description (1-2 sentences):** A tool to help manage Tidal music playlists and songs.
- **Target Audience:** Melomaniacs or music lovers that want to create and manage their playlists.
- **Goal:** To help users create and manage their playlists.

---

### 2. Version Planning & Development Roadmap

This section outlines the incremental development milestones for the Tidal Helper project. Each version represents a specific deliverable or feature implementation.

#### Phase 0.1.x - Project Initialization & Setup

- **v0.1.0** → Initial project structure created (root directory, backend/frontend folders)
- **v0.1.1** → Install core dependencies (Poetry for backend, npm for frontend)
- **v0.1.2** → Setup backend structure (FastAPI app, folder organization, initial configs)
- **v0.1.3** → Add linters and formatters (Black, Flake8, ESLint, Prettier)
- **v0.1.4** → Configure frontend tooling (Vite, TypeScript config, Tailwind CSS)
- **v0.1.5** → Setup Docker containers and docker-compose.yml
- **v0.1.6** → Initialize database models and migrations (SQLModel, Alembic)
- **v0.1.7** → Create environment variable templates and documentation

#### Phase 0.2.x - Authentication & Core Infrastructure

- **v0.2.0** → Implement User model and database schema
- **v0.2.1** → Build user registration endpoint (POST /api/auth/signup)
- **v0.2.2** → Build user login endpoint with JWT (POST /api/auth/login)
- **v0.2.3** → Add password hashing and validation (bcrypt)
- **v0.2.4** → Create authentication middleware for protected routes
- **v0.2.5** → Implement TidalToken model and Tidal API integration basics
- **v0.2.6** → Build Tidal OAuth flow (tidalapi session management)
- **v0.2.7** → Create token refresh mechanism
- **v0.2.8** → Frontend: Authentication UI components (Login/Signup forms)
- **v0.2.9** → Frontend: Auth state management with Pinia
- **v0.2.10** → Frontend: Protected route guards (Vue Router)

#### Phase 0.3.x - Playlist Management (CRUD)

- **v0.3.0** → Implement Playlist and Song models with Many-to-Many relationship
- **v0.3.1** → Create PlaylistSongLink join table with ordering support
- **v0.3.2** → Build Playlist CRUD endpoints (GET, POST, PUT, DELETE /api/playlists)
- **v0.3.3** → Implement playlist service layer with business logic
- **v0.3.4** → Frontend: Dashboard view component
- **v0.3.5** → Frontend: Playlist list/grid display
- **v0.3.6** → Frontend: Create playlist dialog/form
- **v0.3.7** → Frontend: Edit playlist functionality
- **v0.3.8** → Frontend: Delete playlist with confirmation
- **v0.3.9** → Frontend: Empty state for new users

#### Phase 0.4.x - Song Management

- **v0.4.0** → Build Song search endpoint (Tidal API integration)
- **v0.4.1** → Implement Song deduplication logic (by tidal_id)
- **v0.4.2** → Create Add Song to Playlist endpoint (POST /api/playlists/{id}/songs)
- **v0.4.3** → Create Remove Song from Playlist endpoint (DELETE /api/playlists/{id}/songs/{song_id})
- **v0.4.4** → Implement song reordering within playlist
- **v0.4.5** → Add song refresh functionality (force Tidal API fetch)
- **v0.4.6** → Frontend: Song search component with autocomplete
- **v0.4.7** → Frontend: Add song to playlist UI
- **v0.4.8** → Frontend: Song list within playlist view
- **v0.4.9** → Frontend: Remove song functionality with immediate update
- **v0.4.10** → Frontend: Display song metadata (title, artist, album, cover)

#### Phase 0.5.x - Data Synchronization

- **v0.5.0** → Design sync strategy (Tidal as master, conflict resolution)
- **v0.5.1** → Implement Tidal playlist fetch service
- **v0.5.2** → Build sync comparison logic (local vs Tidal)
- **v0.5.3** → Add sync endpoint (POST /api/sync) with playlist selection
- **v0.5.4** → Implement "unavailable song" flagging system
- **v0.5.5** → Add rate limiter for Tidal API calls
- **v0.5.6** → Frontend: Sync button in navigation bar
- **v0.5.7** → Frontend: Sync progress indicator (loading state)
- **v0.5.8** → Frontend: Sync completion toast notification
- **v0.5.9** → Frontend: Display unavailable songs with visual distinction

#### Phase 0.6.x - Error Handling & Edge Cases

- **v0.6.0** → Implement offline mode detection
- **v0.6.1** → Add graceful API failure handling
- **v0.6.2** → Implement token expiry auto-refresh
- **v0.6.3** → Build token expiry fallback (redirect to login)
- **v0.6.4** → Add unavailable song grouping in playlist view
- **v0.6.5** → Create comprehensive error message system
- **v0.6.6** → Frontend: Offline mode UI indicator
- **v0.6.7** → Frontend: Error boundary components
- **v0.6.8** → Frontend: User-friendly error messages

#### Phase 0.7.x - Testing & Quality Assurance

- **v0.7.0** → Setup pytest for backend testing
- **v0.7.1** → Write unit tests for authentication
- **v0.7.2** → Write unit tests for playlist CRUD
- **v0.7.3** → Write integration tests for Tidal API sync
- **v0.7.4** → Setup Vitest for frontend testing
- **v0.7.5** → Write component tests for authentication views
- **v0.7.6** → Write component tests for playlist management
- **v0.7.7** → Add E2E tests with Playwright/Cypress
- **v0.7.8** → Achieve 80%+ code coverage

#### Phase 0.8.x - Polish & UX Enhancements

- **v0.8.0** → Implement mobile-responsive design
- **v0.8.1** → Add loading skeletons for async operations
- **v0.8.2** → Improve form validation with user feedback
- **v0.8.3** → Add keyboard shortcuts for power users
- **v0.8.4** → Implement dark/light theme toggle
- **v0.8.5** → Add accessibility features (ARIA labels, keyboard navigation)
- **v0.8.6** → Optimize performance (lazy loading, code splitting)
- **v0.8.7** → Add user onboarding tooltips/tutorial

#### Phase 0.9.x - Pre-Release & Documentation

- **v0.9.0** → Complete API documentation (OpenAPI/Swagger)
- **v0.9.1** → Write user guide and README
- **v0.9.2** → Create deployment guide
- **v0.9.3** → Finalize Docker production configuration
- **v0.9.4** → Security audit and penetration testing
- **v0.9.5** → Performance testing and optimization
- **v0.9.6** → Beta testing with select users
- **v0.9.7** → Bug fixes and stability improvements
- **v0.9.8** → Release candidate preparation

#### Phase 1.0.x - Production Release & Future Features

- **v1.0.0** → Official production release (MVP complete)
- **v1.0.1** → Add analytics dashboard (user insights)
- **v1.0.2** → Implement real-time synchronization (WebSocket)
- **v1.0.3** → Add collaborative playlists (multi-user sharing)
- **v1.0.4** → Implement playlist import/export (Spotify, Apple Music)
- **v1.0.5** → Add playlist recommendations (ML-based)
- **v1.1.0** → Mobile app development (React Native or Flutter)

> **Note:** Version numbers follow [Semantic Versioning](https://semver.org/):
> `MAJOR.MINOR.PATCH` where PATCH increments represent backwards-compatible bug fixes or small additions, MINOR increments represent new backwards-compatible features, and MAJOR increments represent breaking changes.

---

### 3. Core Features & Functionality

- **Primary Features (Must-Haves):**
  - User authentication (sign-up/login)
  - Data CRUD operations (Create, Read, Update, Delete) for playlists and songs
  - Data synchronization by a manual sync button
- **Secondary Features (Nice-to-Haves/Future Scope):**
  - Integrated analytics dashboard
  - Mobile responsive design
- **Future Features:**
  - Real-time data synchronization at version 1.0.0

#### Important Architecture Notes

The application has **two independent but parallel sections**:

**1. Tidal Section**

- Represents the user's current Tidal account playlists and songs
- Data fetched directly from Tidal API
- Read-only view of the user's Tidal state

**2. Local Section**

- Represents playlists and songs stored in the local database
- Allows offline management and organization
- Primary workspace for users to curate before syncing

**Workflow:** Users manage playlists locally → organize and refine → sync to Tidal account OR pull from Tidal → organize locally → push back to Tidal.

---

## 4. User Flows

### 4.1 User Authentication (Onboarding)

**Goal:** Securely access the application and establish Tidal connection.

**Pre-condition:** User has opened the application.

- **Landing:** User lands on the **Welcome** screen.
- **Choice:** User selects **"Sign Up"** or **"Log In"**.

#### A. Sign Up

1.  User enters email, password, and confirm password.
2.  System validates input and creates a new user record.
3.  System redirects to the **Login** screen.

#### B. Log In

1.  User enters registered email and password.
2.  System validates credentials.
    - **Success:** User is redirected to the **Main Dashboard**.
    - **Failure:** Error message displayed (> "Invalid credentials").

---

### 4.2 Playlist Management (CRUD)

**Goal:** Organize music into collections (Playlists).

**Pre-condition:** User is logged in.

#### View (Read)

- User navigates to the **Dashboard** to see a grid/list of all existing playlists.

#### Create

1.  User clicks the **"New Playlist"** button.
2.  User enters a `Name` and `Description`.
3.  User clicks **"Save"**.
4.  The new playlist is added to the Dashboard view.

#### Update

1.  User clicks the **"Edit"** icon on a playlist.
2.  User modifies the metadata.
3.  User clicks **"Update"**.

#### Delete

1.  User selects **"Delete"** on a playlist.
2.  System prompts: > "Are you sure?"
3.  User confirms.
4.  Playlist is removed from the database and view.

---

### 4.3 Song Management

**Goal:** Manage contents of specific playlists.

**Pre-condition:** User has selected a specific playlist.

#### Add Song

1.  User clicks **"Add Song"**.
2.  User inputs `Song Title/Artist` or `Tidal ID` [the song is search at the Tidal API].
3.  System verifies song details.
4.  User confirms addition.
5.  Song appears in the playlist list.

#### Remove Song

1.  User locates a song within the playlist.
2.  User clicks the **"Remove"** (Trash icon).
3.  Song is immediately removed from the list [But the song is not deleted from the database only from the playlist].

#### Song Management Rules

> **Database Storage:** Songs are stored using Tidal's unique identifier (`tidal_id`) to prevent duplicates.

> **Deletion Behavior:** Removing a song from a playlist does NOT delete it from the database—only the playlist association is removed.

> **Search Priority:** When searching for a song:
>
> 1. Check local database first
> 2. If not found, fetch from Tidal API and save to database
> 3. Search response indicates source (Local DB vs. Tidal API)

> **Force Refresh:** Users can force-refresh song metadata from Tidal API using the **Refresh** button (sync icon).

---

### 4.4 Manual Data Synchronization

**Goal:** Ensure local database reflects the latest state from Tidal account, or push local changes to Tidal.

**Pre-condition:** User is logged in.

#### 1. Trigger

- User clicks the **"Sync Data"** button located in the top navigation bar.

#### 2. Processing

- System changes button state to **"Syncing..."** (spinner icon).
- System fetches latest data from Tidal API.
- System resolves conflicts and updates local database.

#### 3. Completion

- System displays a success toast notification: > "Data Synchronized"
- Dashboard refreshes to show the latest state.

---

### 4.5 Edge Cases & Error Handling

**Goal:** Gracefully handle failure states to maintain app stability and user trust.

#### 4.5.1 Tidal API Unreachable

**Scenario:** Internet is down or Tidal API is unresponsive.

**Behavior:**

- App enters **Offline Mode**
- Users can view locally cached playlists and songs from database
- Search, Add, and Delete operations continue working locally
- Warning banner displays: _"No Internet Connection - Working Offline"_
- Sync button is disabled
- All operations are saved to local database only

#### 4.5.2 Token Expiry

**Scenario:** Tidal authentication token expires mid-session.

**Behavior:**

1. Backend automatically attempts silent token refresh
2. **If refresh succeeds:** User continues without interruption
3. **If refresh fails:** User is redirected to Tidal login screen
4. Toast notification displays: _"Session expired. Please log in again."_

#### 4.5.3 Song No Longer Available on Tidal

**Scenario:** A locally-saved song has been removed from Tidal's catalog.

**Behavior:**

- During sync, the system flags the song as unavailable
- Song remains in database but displays as grayed out in UI
- Tooltip shows: _"Not available on Tidal"_
- Unavailable songs are grouped in a separate section: **"Unavailable Songs"**
- Users can still add previously-saved unavailable songs to playlists
- Users can manually delete unavailable songs from playlists

#### 4.5.4 Empty States (First-Time Users)

**Scenario:** New user logs in with no playlists or songs.

**Behavior:**

- Dashboard displays a welcoming **"Get Started"** card
- Message: _"No playlists yet. Create your first playlist to begin organizing your music!"_
- Prominent **"Create Playlist"** button

---

## 5. Technical Specifications

### Backend Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Server:** Uvicorn (ASGI server)
- **ORM/Database:** SQLModel + SQLAlchemy
- **Migrations:** Alembic
- **Package Manager:** Poetry
- **Validation:** Pydantic
- **Key Libraries:** tidalapi (Tidal integration), python-jose (JWT), passlib (password hashing)

### Frontend Stack

- **Language:** TypeScript
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State Management:** Pinia
- **Routing:** Vue Router
- **HTTP Client:** Axios / Fetch API

### Infrastructure

- **Database:** SQLite (development), PostgreSQL (production-ready)
- **Containerization:** Docker + Docker Compose
- **Environment Management:** .env files

### Development Tools

- **Linting/Formatting (Backend):** Black, Flake8, isort
- **Linting/Formatting (Frontend):** ESLint, Prettier
- **Testing (Backend):** pytest, pytest-asyncio
- **Testing (Frontend):** Vitest, Playwright/Cypress (E2E)

---

## 6. Folder Structure

- **Root Directory (`/tidal-helper`)**

  - **`/backend`:** Main backend application files (FastAPI).

    - **`/backend/app`:** Main Python package.
      - **`/backend/app/api`:** API route definitions and endpoints.
      - **`/backend/app/core`:** Configuration, database connection (Engine), and security settings.
      - **`/backend/app/models`:** SQLModel classes (Database tables + Pydantic schemas).
      - **`/backend/app/services`:** Business logic, including the `tidalapi` integration wrapper.
      - **`/backend/app/main.py`:** Application entry point.
    - **`/backend/alembic`:** Database migration scripts and configuration.
    - **`/backend/tests`:** Backend unit and integration tests.
    - **`pyproject.toml`:** Poetry dependency management file.
    - **`Dockerfile`:** Backend container configuration.

  - **`/frontend`:** Main frontend application files (Vue.js + TypeScript).

    - **`/frontend/src`:** Source code.
      - **`/frontend/src/assets`:** Static files (Images, global CSS).
      - **`/frontend/src/components`:** Reusable UI components (e.g., Buttons, Cards).
      - **`/frontend/src/views`:** Top-level pages (e.g., Dashboard, Login).
      - **`/frontend/src/stores`:** Pinia state management stores.
      - **`/frontend/src/router`:** Vue Router configuration.
      - **`/frontend/src/services`:** API client functions to communicate with the backend.
      - **`/frontend/src/types`:** TypeScript interfaces and type definitions.
    - **`vite.config.ts`:** Vite build configuration.
    - **`package.json`:** NPM dependencies and scripts.
    - **`Dockerfile`:** Frontend container configuration.

  - **Root Configuration:**
    - **`docker-compose.yml`:** Orchestration for Backend, Frontend, and Database containers.
    - **`.env`:** Environment variables (Secrets, API Keys, DB URL).

---

## 7. Data Schema (ERD Description)

**Goal:** Define the database structure to support the application logic, specifically the Many-to-Many relationship between Playlists and Songs.

Note: Fields or tables can be added or modified if needed.

### 7.1 Tables

**User**

- `id` (Primary Key)
- `email` (Unique, Index)
- `password_hash`
- `created_at`

**TidalToken**

- `id` (Primary Key)
- `user_id` (Foreign Key -> User.id)
- `refresh_token`
- `access_token`
- `expires_at`
- `created_at`
- `updated_at`

**Playlist**

- `id` (Primary Key)
- `tidal_token_id` (Foreign Key -> TidalToken.id)
- `name`
- `description`
- `created_at`
- `updated_at`

**Song**

- `id` (Primary Key - Internal DB ID)
- `tidal_id` (Unique, Index - The ID provided by Tidal API)
- `title`
- `artist`
- `album`
- `cover_url`

**PlaylistSongLink (Join Table)**

- _This table enables the Many-to-Many relationship._
- `playlist_id` (Foreign Key -> Playlist.id)
- `song_id` (Foreign Key -> Song.id)
- `order` (Integer) - Crucial for maintaining custom sort order in playlists.
- `added_at` (Timestamp)

### 7.2 Key Relationships

- **User** has Many **Playlists**.
- **Playlist** has Many **Songs** (via `PlaylistSongLink`).
- **Song** belongs to Many **Playlists** (via `PlaylistSongLink`).

> **Note:** Songs are unique in the database based on `tidal_id`. If User A adds "Thriller" and User B adds "Thriller", the database stores one `Song` row, but two `PlaylistSongLink` rows.

---

## 8. Integration Strategy (Tidal API)

**Goal:** Define how the backend interacts with the external service.

### 8.1 Authentication & Session

- **Library:** `tidalapi` (Python).
- **Auth Flow:** The application will use the `tidalapi` Session object.
- **Persistence:** Upon successful login, the Session credentials (refresh token/access token) will be encrypted and stored associated with the User record.
- **Refresh Strategy:** Before every call to Tidal, the backend middleware checks if the token is valid. If expired, it attempts a refresh using the stored refresh token _before_ executing the request.

### 8.2 Synchronization Logic (Conflict Resolution)

**Strategy:** Master-Slave (Tidal is Master).

**Sync Button Behavior:**

1.  Fetch current playlist state from Tidal.
2.  Compare with Local Database.
3.  **If Song exists on Tidal but not Local:** Add to Local.
4.  **If Song exists Local but not on Tidal:**
    - _Strict Mode:_ Remove from Local (to match Tidal).
    - _Safe Mode (Default):_ Mark as "Local Only" in UI.
5.  Update metadata (Title/Artist) in Local DB if Tidal data has changed.
    ! **Note:** The sync must be by specific playlist or all playlists depending on the user's choice.

### 8.3 Rate Limiting

To prevent IP bans, the backend will implement a basic **leaky bucket rate limiter** (e.g., max 5 requests per second to Tidal API). [This should be consult to tidal api doc too see how many requests are allowed per second and set the rate limiter accordingly - Also this can be configured in the .env file]

---

## 9. Appendix: Environment Variables

Add these to your `.env` file configuration list:

```bash
# Application Secrets
SECRET_KEY=change_this_to_random_string  # Required for JWT
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL="sqlite:///./tidal_helper.db" # or Postgres URL

# Tidal Configuration (Optional/If custom Client)
# Only required if not using default tidalapi keys
TIDAL_API_TOKEN=
TIDAL_CLIENT_ID=

# Rate Limiting
RATE_LIMITER_MAX_REQUESTS_PER_SECOND=5

```
