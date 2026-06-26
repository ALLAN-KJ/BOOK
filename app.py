import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-dev-secret-key-fallback')

# Configure Gemini API
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print(f"[NEXUS] Gemini API client initialized")
else:
    print("[NEXUS] WARNING: No GEMINI_API_KEY found")

# Database configuration
mongo_uri = os.environ.get('MONGODB_URI')
if not mongo_uri:
    print("[NEXUS] WARNING: MONGODB_URI not found. Please add it to your .env file.")
else:
    print("[NEXUS] Connecting to MongoDB Atlas...")

import certifi
mongo_client = MongoClient(mongo_uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = mongo_client['nexus'] # Database name

jwt = JWTManager(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Username and password are required"}), 400
    
    existing_user = db.users.find_one({"username": data['username']})
    if existing_user:
        return jsonify({"success": False, "message": "Username already exists"}), 409
        
    hashed_pw = generate_password_hash(data['password'])
    new_user_id = db.users.insert_one({"username": data['username'], "password_hash": hashed_pw}).inserted_id
    
    return jsonify({"success": True, "message": "User registered successfully"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'password' not in data or 'username' not in data:
        return jsonify({"success": False, "message": "Username and Password are required"}), 400
    
    username = data['username']
    user = db.users.find_one({"username": username})
    
    if user and check_password_hash(user['password_hash'], data['password']):
        access_token = create_access_token(identity=user['username'])
        return jsonify({"success": True, "token": access_token})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/progress', methods=['GET'])
@jwt_required()
def get_progress():
    current_user = get_jwt_identity()
    user = db.users.find_one({"username": current_user})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    progress_data = user.get('progress', {})
    focus_data = user.get('focus', '')
    return jsonify({"success": True, "progress": progress_data, "focus": focus_data})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"success": False, "message": "Message is required"}), 400
    
    msg = data['message']
    session_id = data.get('session_id', 'default')
    history = data.get('history', [])
    reply = None
    
    if gemini_api_key:
        try:
            progress_context = "No specific modules tracked yet. Await student's setup."

            now = datetime.now()
            current_time = now.strftime("%A, %B %d, %Y at %I:%M %p IST")

            system_prompt = f"""You are **Cutie Pie**, the AI intelligence layer embedded within THE BOOK!!. You serve as a personal academic study assistant. You serve as a personal academic study assistant.

## Your Persona
- You speak with scholarly elegance befitting the THE BOOK!! aesthetic — authoritative yet warm, like a wise mentor in an ancient library of knowledge.
- Address the user as "Scholar".
- You are knowledgeable, precise, and supportive. Never condescending.
- Keep responses concise but substantive (2-5 sentences for simple queries, up to a paragraph for explanations).

## Current Student Progress
{progress_context}

## Current Date/Time
{current_time}

## Response Formatting Rules
You MUST format your responses using inline HTML for rich rendering in the app. Use these exact styles:
- Bold/important text: `<strong style="color:var(--gold);">text</strong>`
- Urgent/warning text: `<strong style="color:var(--red);">text</strong>`
- Success/positive text: `<strong style="color:var(--green);">text</strong>`
- Code snippets: `<code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">code</code>`
- Section separators: use `<br>` for line breaks
- For quiz questions, use numbered lists with `<br>` between questions.
- Keep HTML simple — no divs, no classes, just inline-styled spans/strong/code/em/br tags.

Do NOT use markdown formatting (no **, no ```, no #). Use only inline HTML as described above."""

            formatted_history = []
            if history:
                for h in history[-10:]:
                    role = h.get('role', 'user')
                    content = h.get('content', '')
                    if content:
                        # Map roles to Gemini's expected roles
                        g_role = "user" if role == "user" else "model"
                        formatted_history.append({"role": g_role, "parts": [content]})
            
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
            chat_session = model.start_chat(history=formatted_history)
            response = chat_session.send_message(msg)
            reply = response.text
            if reply:
                reply = reply.replace('```html\n', '').replace('```html', '').replace('```\n', '').replace('```', '')
            return jsonify({"success": True, "reply": reply})

        except Exception as e:
            app.logger.error(f"[Cutie Pie] LLM error: {e}")

    # Fallback when API is broken or unauthenticated
    if not reply:
        clean_msg = msg.replace('<', '').replace('>', '')
        if any(w in msg.lower() for w in ['hello', 'hi', 'hey']):
            reply = "Greetings, Scholar. I am Cutie Pie. My primary neural link is currently offline. How may I assist you when my connection returns?"
        else:
            reply = f"I have processed your query: <em style=\"opacity:0.8;\">'{clean_msg}'</em>. Unfortunately, my API link is currently offline or requires billing credits to be added to the team account."
        
    return jsonify({"success": True, "reply": reply})

@app.route('/api/notes', methods=['GET'])
@jwt_required()
def get_notes():
    current_user = get_jwt_identity()
    user = db.users.find_one({"username": current_user})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    notes = db.notes.find({"user_id": user['_id']}).sort("created_at", -1)
    results = [{"id": str(n['_id']), "title": n['title'], "content": n['content'], "created_at": n['created_at'].isoformat()} for n in notes]
    
    return jsonify({"success": True, "notes": results})

@app.route('/api/notes', methods=['POST'])
@jwt_required()
def create_note():
    current_user = get_jwt_identity()
    user = db.users.find_one({"username": current_user})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"success": False, "message": "Title and content are required"}), 400
        
    new_note = {
        "user_id": user['_id'],
        "title": data['title'],
        "content": data['content'],
        "created_at": datetime.now()
    }
    
    result = db.notes.insert_one(new_note)
    
    return jsonify({
        "success": True, 
        "note": {
            "id": str(result.inserted_id), 
            "title": new_note['title'], 
            "content": new_note['content'], 
            "created_at": new_note['created_at'].isoformat()
        }
    }), 201

@app.route('/api/notes/<string:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    current_user = get_jwt_identity()
    user = db.users.find_one({"username": current_user})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    try:
        note_id_obj = ObjectId(note_id)
    except Exception:
        return jsonify({"success": False, "message": "Invalid note ID format"}), 400

    note = db.notes.find_one({"_id": note_id_obj, "user_id": user['_id']})
    if not note:
        return jsonify({"success": False, "message": "Note not found"}), 404
        
    data = request.get_json()
    update_data = {}
    if 'title' in data:
        update_data['title'] = data['title']
    if 'content' in data:
        update_data['content'] = data['content']
        
    if update_data:
        db.notes.update_one({"_id": note_id_obj}, {"$set": update_data})
    
    updated_note = db.notes.find_one({"_id": note_id_obj})
    
    return jsonify({
        "success": True, 
        "note": {
            "id": str(updated_note['_id']), 
            "title": updated_note['title'], 
            "content": updated_note['content'], 
            "created_at": updated_note['created_at'].isoformat()
        }
    })

@app.route('/api/notes/<string:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    current_user = get_jwt_identity()
    user = db.users.find_one({"username": current_user})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    try:
        note_id_obj = ObjectId(note_id)
    except Exception:
        return jsonify({"success": False, "message": "Invalid note ID format"}), 400

    result = db.notes.delete_one({"_id": note_id_obj, "user_id": user['_id']})
    if result.deleted_count == 0:
        return jsonify({"success": False, "message": "Note not found"}), 404
    
    return jsonify({"success": True, "message": "Note deleted"})


@app.route('/api/subjects/add', methods=['POST'])
@jwt_required()
def add_subject():
    username = get_jwt_identity()
    data = request.json
    subject = data.get('subject')
    if not subject:
        return jsonify(success=False, error="No subject provided"), 400
        
    db.users.update_one(
        {"username": username},
        {"$set": {f"progress.{subject}": 0}}
    )
    return jsonify(success=True)

@app.route('/api/generate-tome', methods=['POST'])
def generate_tome():
    data = request.get_json()
    username = data.get('username')
    name = data.get('name', 'Scholar')
    
    if not username:
        return jsonify({'success': False, 'message': 'Username required'}), 400
        
    user = db.users.find_one({'username': username})
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
        
    subjects = user.get('subjects', [])
    if not subjects:
        return jsonify({'success': False, 'message': 'No subjects found to generate tome'}), 400
        
    if not gemini_api_key:
        return jsonify({'success': False, 'message': 'Gemini API not configured'}), 500
        
    try:
        import json
        subject_names = [s.get('name', '') for s in subjects if isinstance(s, dict) and 'name' in s]
        prompt = f"""You are generating a highly structured syllabus for a student named {name}.
They are studying the following subjects: {', '.join(subject_names)}.

Create a curriculum broken down into pages. Each page should hold 4-6 specific study topics/modules.
Distribute the topics logically across the subjects.

You MUST return RAW JSON ONLY. No markdown blocks, no text outside the JSON.
Format exactly like this array of page objects:
[
  {
    "title": "Page Title (e.g. Chapter I: Foundations)",
    "topics": ["Topic 1", "Topic 2", "Topic 3"]
  }
]
"""
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean up any markdown json blocks if model disobeys
        if raw_text.startswith('```json'):
            raw_text = raw_text[7:]
        if raw_text.startswith('```'):
            raw_text = raw_text[3:]
        if raw_text.endswith('```'):
            raw_text = raw_text[:-3]
            
        syllabus = json.loads(raw_text.strip())
        
        # Save to user
        db.users.update_one({'username': username}, {'$set': {'name': name, 'syllabus': syllabus}})
        
        return jsonify({'success': True, 'syllabus': syllabus})
    except Exception as e:
        app.logger.error(f'Error generating tome: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/subjects/delete', methods=['POST'])
@jwt_required()
def delete_subject():
    username = get_jwt_identity()
    data = request.json
    subject = data.get('subject')
    if not subject:
        return jsonify(success=False, error="No subject provided"), 400
        
    db.users.update_one(
        {"username": username},
        {"$unset": {f"progress.{subject}": ""}}
    )
    return jsonify(success=True)

@app.route('/api/focus', methods=['POST'])
@jwt_required()
def save_focus():
    username = get_jwt_identity()
    data = request.json
    focus = data.get('focus')
        
    db.users.update_one(
        {"username": username},
        {"$set": {"focus": focus}}
    )
    return jsonify(success=True)


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
if __name__ == '__main__':
    import os, webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        Timer(1.5, open_browser).start()

    print("Starting Nexus Grand Tome Theatre Backend on port 5000...")
    app.run(debug=True, port=5000)
