# NEXUS — Grand Tome Theatre

NEXUS is an immersive, interactive learning dashboard built with a visually stunning 3D book interface. It features a fully dynamic AI-driven syllabus generator, an interactive alien companion (Xeno), and a beautiful Theme Engine. 

The frontend uses an animated 3D book interface created with CSS and GSAP, running against a Python Flask backend with MongoDB Atlas for storage and Google's Gemini 2.5 Flash AI for dynamic content generation.

## Features

- **Immersive 3D UI**: A fully interactive physical 3D book built with HTML/CSS and GSAP for smooth page-turning and closing animations.
- **AI Syllabus Generator (Gemini)**: Enter your subjects, and Gemini AI will dynamically generate a custom study curriculum, physically constructing new pages in your 3D book on the fly!
- **Theme Engine**: Switch between multiple gorgeous aesthetics on the fly (Obsidian & Gold, Ruby & Silver, Emerald & Bronze).
- **Interactive Alien Companion**: Xeno the alien lives on the login page and reacts to your login attempts with a multi-stage emotional sequence (including a dramatic 3rd-strike laser sequence!).
- **AI Oracle**: A built-in chat interface powered by Gemini 2.5 Flash that acts as a wise mentor.
- **Authentication & Cloud Storage**: Secure login backed by MongoDB Atlas.

## Tech Stack

### Frontend
- HTML5 / Vanilla CSS
- [GSAP](https://greensock.com/gsap/) (for smooth 3D page-turning and structural animations)

### Backend
- **Python 3.11**
- **Flask** (REST API)
- **PyMongo** (MongoDB Atlas Database)
- **Google Generative AI (Gemini)** (For Oracle Chat and Syllabus Generation)

## Getting Started (Local Development)

### Prerequisites
- Python 3.8+
- MongoDB Atlas cluster (or local instance)
- Gemini API Key

### Installation & Setup

1. **Clone the repository and navigate to the server directory**
   ```bash
   cd server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory (DO NOT commit this file to GitHub!):
   ```ini
   MONGODB_URI="your_mongo_connection_string"
   GEMINI_API_KEY="your_gemini_api_key"
   JWT_SECRET_KEY="your_jwt_secret"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`.

### Default Seed Account
- **Username:** `ADMIN`
- **Passphrase:** `password123`

## Architecture

- `app.py`: Main Flask application handling API routes and Gemini AI generation logic.
- `static/index.html`: The monolithic frontend containing the structural 3D HTML, CSS themes, and JavaScript for rendering dynamic AI pages.

## License
[MIT License](LICENSE)
