## 💾 Software Project Specification

---

### 1. Project Overview

* **Project Name:** Tidal Helper
* **Start Version:** 0.1.0
* **Short Description (1-2 sentences):** A tool to help manage Tidal music playlists and songs.
* **Target Audience:** Melomaniacs or music lovers that want to create and manage their playlists.
* **Goal:** To help users create and manage their playlists.

---

### 2. Core Features & Functionality

* **Primary Features (Must-Haves):**
    * User authentication (sign-up/login)
    * Data CRUD operations (Create, Read, Update, Delete) for playlists and songs
    * Data synchronization by a manual sync button
* **Secondary Features (Nice-to-Haves/Future Scope):**
    * Integrated analytics dashboard
    * Mobile responsive design
* **Future Features:**
    * Real-time data synchronization at version 1.0.0
* **Important notes:**
    * The application has two main sections that works similar, but they are independant:
        * Tidal section:
         - Is the current user Tidal playlists and songs.
        * Local section:
         - Is the current user local playlists and songs saved at the local database.
        - The main goal of this is to handle data locally and then sync to the Tidal's user account or get the data from the Tidal's user account to the local database to organize and the push again to Tidal's user account.

---

## 3. User Flows

### 3.1 User Authentication (Onboarding)
**Goal:** Securely access the application.

**Pre-condition:** User has opened the application.

* **Landing:** User lands on the **Welcome** screen.
* **Choice:** User selects **"Sign Up"** or **"Log In"**.

#### A. Sign Up
1.  User enters email, password, and confirm password.
2.  System validates input and creates a new user record.
3.  System redirects to the **Login** screen.

#### B. Log In
1.  User enters registered email and password.
2.  System validates credentials.
    * **Success:** User is redirected to the **Main Dashboard**.
    * **Failure:** Error message displayed (> "Invalid credentials").

---

### 3.2 Playlist Management (CRUD)
**Goal:** Organize music into collections [Playlists].

**Pre-condition:** User is logged in.

#### View (Read)
* User navigates to the **Dashboard** to see a grid/list of all existing playlists.

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

### 3.3 Song Management
**Goal:** Manage contents of specific playlists

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

#### Important Note
-  The Songs are being saved at DB with the unique identifier of the Tidal API.
- When a song is removed from a playlist, the song is not deleted from the database only from the playlist.
- When a song is search it first checks if the song is already in the database and if it is not it will add it to the database.
- The response of the search indicates from where is getting the song if from the database or from the Tidal API.
- The songs can be force to be refreshed from the Tidal API by clicking the **"Refresh"** (Sync icon).

---

### 3.4 Manual Data Synchronization
**Goal:** Ensure local data matches external Tidal account data.

**Pre-condition:** User is logged in.

#### 1. Trigger
* User clicks the **"Sync Data"** button located in the top navigation bar.

#### 2. Processing
* System changes button state to **"Syncing..."** (spinner icon).
* System fetches latest data from Tidal API.
* System resolves conflicts and updates local database.

#### 3. Completion
* System displays a success toast notification: > "Data Synchronized"
* Dashboard refreshes to show the latest state.

---

### 3.5 Edge Cases & Error Handling
**Goal:** Manage failure states gracefully to prevent app crashes and user frustration.

#### Tidal API Unreachable
* **Scenario:** Internet is down or Tidal API is unresponsive.
* **Behavior:** App enters **"Offline Mode"**. Users can view locally cached playlists [saved at db] and songs [saved at db] but cannot Sync. It can Search, Add, or Delete, but with a warning message of "No Connection" and the sync button is disabled [All searchs and adds are locally saved to db].

#### Token Expiry
* **Scenario:** The Tidal authentication token expires during a session.
* **Behavior:** The backend attempts a silent refresh. If that fails, the user is redirected to the Login for tidal token refresh screen with a toast:
    > "Session expired. Please log in again."

#### Song No Longer Exists on Tidal
* **Scenario:** A song saved locally was removed from Tidal's catalog.
* **Behavior:** During Sync, the system flags this song. In the UI, the song is grayed out with a "Not Available" tooltip. The user can manually delete it from the playlist.
- The song must be continue saved at db but grayed out in the UI.
- If the playlist contains songs unavailable on Tidal, group them into a separate section of the playlist.
- Not available songs can be added to the playlist if was previously saved at db.

#### Empty States (Onboarding)
* **Scenario:** New user logs in for the first time.
* **UI:** The Dashboard displays a friendly **"Get Started"** card encouraging the user to "Create your first Playlist".

---

### 4. Technical Specifications

* **Programming Languages:** Python for backend, TypeScript for frontend
* **Frontend Technologies/Frameworks:** Vue.js, HTML, Tailwind CSS, Vite, Pinia, Vue Router
* **Backend Technologies/Frameworks:** FastAPI, Uvicorn, Pydantic, SQLModel, SQLAlchemy / Alembic, Poetry, FastAPI CLI
* **Database:** SQLite
* **Deployment/Hosting:** Docker
* **Key Dependencies/Libraries:** Tailwind CSS for styling, tidalapi for Tidal API

---

### 5. Folder Structure (Detailed)

* **Root Directory (`/tidal-helper`)**
    * **`/backend`:** Main backend application files (FastAPI).
        * **`/backend/app`:** Main Python package.
            * **`/backend/app/api`:** API route definitions and endpoints.
            * **`/backend/app/core`:** Configuration, database connection (Engine), and security settings.
            * **`/backend/app/models`:** SQLModel classes (Database tables + Pydantic schemas).
            * **`/backend/app/services`:** Business logic, including the `tidalapi` integration wrapper.
            * **`/backend/app/main.py`:** Application entry point.
        * **`/backend/alembic`:** Database migration scripts and configuration.
        * **`/backend/tests`:** Backend unit and integration tests.
        * **`pyproject.toml`:** Poetry dependency management file.
        * **`Dockerfile`:** Backend container configuration.

    * **`/frontend`:** Main frontend application files (Vue.js + TypeScript).
        * **`/frontend/src`:** Source code.
            * **`/frontend/src/assets`:** Static files (Images, global CSS).
            * **`/frontend/src/components`:** Reusable UI components (e.g., Buttons, Cards).
            * **`/frontend/src/views`:** Top-level pages (e.g., Dashboard, Login).
            * **`/frontend/src/stores`:** Pinia state management stores.
            * **`/frontend/src/router`:** Vue Router configuration.
            * **`/frontend/src/services`:** API client functions to communicate with the backend.
            * **`/frontend/src/types`:** TypeScript interfaces and type definitions.
        * **`vite.config.ts`:** Vite build configuration.
        * **`package.json`:** NPM dependencies and scripts.
        * **`Dockerfile`:** Frontend container configuration.

    * **Root Configuration:**
        * **`docker-compose.yml`:** Orchestration for Backend, Frontend, and Database containers.
        * **`.env`:** Environment variables (Secrets, API Keys, DB URL).
---

## 6. Data Schema (ERD Description)
**Goal:** Define the database structure to support the application logic, specifically the Many-to-Many relationship between Playlists and Songs.

Note: Fields or tables can be added or modified if needed.

### 6.1 Tables

**User**
* `id` (Primary Key)
* `email` (Unique, Index)
* `password_hash`
* `created_at`

**TidalToken**
* `id` (Primary Key)
* `user_id` (Foreign Key -> User.id)
* `refresh_token`
* `access_token`
* `expires_at`
* `created_at`
* `updated_at`

**Playlist**
* `id` (Primary Key)
* `tidal_token_id` (Foreign Key -> TidalToken.id)
* `name`
* `description`
* `created_at`
* `updated_at`

**Song**
* `id` (Primary Key - Internal DB ID)
* `tidal_id` (Unique, Index - The ID provided by Tidal API)
* `title`
* `artist`
* `album`
* `cover_url`

**PlaylistSongLink (Join Table)**
* *This table enables the Many-to-Many relationship.*
* `playlist_id` (Foreign Key -> Playlist.id)
* `song_id` (Foreign Key -> Song.id)
* `order` (Integer) - Crucial for maintaining custom sort order in playlists.
* `added_at` (Timestamp)

### 6.2 Key Relationships
* **User** has Many **Playlists**.
* **Playlist** has Many **Songs** (via `PlaylistSongLink`).
* **Song** belongs to Many **Playlists** (via `PlaylistSongLink`).

> **Note:** Songs are unique in the database based on `tidal_id`. If User A adds "Thriller" and User B adds "Thriller", the database stores one `Song` row, but two `PlaylistSongLink` rows.

---

## 7. Integration Strategy (Tidal API)
**Goal:** Define how the backend interacts with the external service.

### 7.1 Authentication & Session
* **Library:** `tidalapi` (Python).
* **Auth Flow:** The application will use the `tidalapi` Session object.
* **Persistence:** Upon successful login, the Session credentials (refresh token/access token) will be encrypted and stored associated with the User record.
* **Refresh Strategy:** Before every call to Tidal, the backend middleware checks if the token is valid. If expired, it attempts a refresh using the stored refresh token *before* executing the request.

### 7.2 Synchronization Logic (Conflict Resolution)
**Strategy:** Master-Slave (Tidal is Master).

**Sync Button Behavior:**
1.  Fetch current playlist state from Tidal.
2.  Compare with Local Database.
3.  **If Song exists on Tidal but not Local:** Add to Local.
4.  **If Song exists Local but not on Tidal:**
    * *Strict Mode:* Remove from Local (to match Tidal).
    * *Safe Mode (Default):* Mark as "Local Only" in UI.
5.  Update metadata (Title/Artist) in Local DB if Tidal data has changed.
! **Note:** The sync must be by specific playlist or all playlists depending on the user's choice.

### 7.3 Rate Limiting
To prevent IP bans, the backend will implement a basic **leaky bucket rate limiter** (e.g., max 5 requests per second to Tidal API). [This should be consult to tidal api doc too see how many requests are allowed per second and set the rate limiter accordingly - Also this can be configured in the .env file]

---

## Appendix: Environment Variables
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

