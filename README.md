# NEXUS — Grand Tome Theatre

NEXUS is an immersive, interactive learning dashboard built with a visually stunning 3D book interface. It tracks student progress across various modules (like Cybersecurity, IoT Networks, and Advanced Python), features an AI Oracle for study guidance, and includes a "Personal Grimoire" for taking encrypted notes. 

The frontend uses an animated 3D book interface created with Three.js and GSAP, running against a Python Flask backend with JWT authentication and an SQLite database.

## Features

- **Immersive 3D UI**: A fully interactive 3D book built with HTML/CSS, GSAP for page-turning animations, and a Three.js deep-space starfield background.
- **Authentication**: Secure login and registration using `Flask-JWT-Extended` and password hashing (`Werkzeug`).
- **Progress Tracking**: Real-time progress updates across modules (Kali Linux, IoT Networks, Adv. Python).
- **Personal Grimoire (Notes)**: Full CRUD functionality for students to create, read, update, and delete study notes.
- **AI Oracle**: A built-in chat interface that provides contextual study guidance and reminders for upcoming practicums.
- **Achievements & Leaderboard**: Gamified learning with an XP system, cohort ranking, and unlockable badges.

## Tech Stack

### Frontend
- HTML5 / Vanilla CSS
- [Three.js](https://threejs.org/) (for the interactive 3D background)
- [GSAP](https://greensock.com/gsap/) (for smooth page-turning animations)

### Backend
- **Python 3.11**
- **Flask** (REST API)
- **Flask-SQLAlchemy** (SQLite Database)
- **Flask-JWT-Extended** (Authentication)
- **Gunicorn** (Production WSGI Server)

## Getting Started (Local Development)

### Prerequisites
- Python 3.8+

### Installation & Setup

1. **Clone the repository and navigate to the server directory**
   ```bash
   cd server
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   *Note: The SQLite database (`nexus.db`) will be automatically created and seeded with a default user on startup.*

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`.

### Default Seed Account
- **Username:** `allan`
- **Passphrase:** `nc14`

## Docker Deployment

You can easily containerize and deploy NEXUS using the provided Dockerfile.

1. **Build the Docker image**
   ```bash
   docker build -t nexus-theatre .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 nexus-theatre
   ```

The application will be served by Gunicorn and accessible at `http://localhost:5000`.

## Architecture

- `app.py`: Main Flask application handling all API routes (`/api/login`, `/api/register`, `/api/progress`, `/api/notes`, `/api/chat`) and serving the static files.
- `static/index.html`: The monolithic frontend containing all structural HTML, CSS styling, Three.js background logic, and JavaScript for API interactions and animations.
- `Dockerfile`: Production-ready configuration using `python:3.11-slim` and `gunicorn`.

## License
[MIT License](LICENSE)
