import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-nexus-key-change-in-prod'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)

RESPONSES = [
    {
        "k": ['python', 'overload', 'dunder', '__add__', '__str__', 'practicum'],
        "r": 'Scholar, your Python Practicum is due in <strong style="color:var(--red);">48 hours</strong>. Focus on dunder methods: <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">__add__</code> overloads the + operator, <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">__str__</code> defines print output, <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">__eq__</code> handles equality checks. Submit <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">overload_demo.py</code> to the portal tonight.'
    },
    {
        "k": ['quiz', 'test', 'question', 'practice'],
        "r": 'Quiz time, Scholar! What does <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">__str__</code> return when you call <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">print(obj)</code>? A) Memory address &nbsp;·&nbsp;B) Human-readable string &nbsp;·&nbsp;C) None. Answer: <strong style="color:var(--gold);">B</strong> — the string you define in the method.'
    },
    {
        "k": ['kali', 'linux', 'cyber', 'security', 'apt', 'nmap', 'recon'],
        "r": 'Cybersecurity standing: <strong style="color:var(--gold);">92%</strong> — near mastery, Scholar. To close the final 8%, review packet analysis with Wireshark and run a full nmap reconnaissance scan on a local VM. One final quiz and you are certified.'
    },
    {
        "k": ['iot', 'sensor', 'dht', 'thingspeak', 'mqtt', 'esp', 'wifi'],
        "r": 'IoT progress at <strong style="color:var(--gold);">78%</strong>. Ensure your <code style="color:var(--gold);background:rgba(201,168,76,0.08);padding:1px 4px;">WRITE_API_KEY</code> is correct and HTTP POST intervals exceed 15 seconds to avoid ThingSpeak rate limiting. Use MQTT for real-time streaming.'
    },
    {
        "k": ['deadline', 'due', 'urgent', 'time', 'when', 'schedule'],
        "r": 'Critical timeline, Scholar — <strong style="color:var(--red);">Python Practicum: 48 hours.</strong> IoT lab report due next week. Kali Linux: one final quiz remaining at 92%. Prioritise Python immediately — submit tonight.'
    },
    {
        "k": ['plan', 'study', 'help', 'how', 'what', 'start'],
        "r": 'Battle plan, Night Coder: <strong>Tonight</strong> — Python Operator Overloading script. <strong>Tomorrow</strong> — IoT ThingSpeak lab report. <strong>Weekend</strong> — Kali Linux final recon quiz. All three modules at 100% by Sunday.'
    },
    {
        "k": ['progress', 'score', 'percent', 'complete', 'status'],
        "r": 'Current standings — Cybersecurity &amp; Kali: <strong style="color:var(--gold);">92%</strong> · IoT Networks: <strong style="color:var(--blue);">78%</strong> · Advanced Python: <strong style="color:var(--red);">45%</strong>. Overall GPA: <strong style="color:var(--gold);">8.6</strong>. Python urgently needs attention.'
    },
    {
        "k": ['team', 'night', 'coder', '14', 'independent scholar'],
        "r": 'Independent Scholar — a formidable intellect! Allan K J holds Level IV clearance and full admin rights across NEXUS. The Grand Theatre recognises your solo prowess. What shall we conquer today?'
    },
    {
        "k": ['certificate', 'cert', 'blockchain', 'hash'],
        "r": 'Your Cybersecurity module is at 92% — complete the final recon quiz to unlock your blockchain-verified certificate. SHA-256 hashed, tamper-proof, downloadable as a signed PDF from the Certificate Vault.'
    }
]

FALLBACK = [
    'The Oracle processes your query. Focus on the Python Practicum — 48 hours remain and Operator Overloading demands your attention tonight, Scholar.',
    'The NEXUS archives suggest prioritising Advanced Python before exploring further. Dunder methods await your command, Independent Scholar.',
    'The Grand Theatre hears you. Three active modules — Python, IoT, Kali — each hold secrets yet unlocked. Which shall we illuminate?',
    'With 92% in Cybersecurity you are near legend status. Push Python to match, and this tome\'s highest tier shall be yours.'
]

fallback_index = 0

# Seed database on startup
with app.app_context():
    db.create_all()
    # Check if 'allan' exists
    user = User.query.filter_by(username='allan').first()
    if not user:
        # Create seed user
        hashed_pw = generate_password_hash('nc14')
        new_user = User(username='allan', password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        # Create seed progress
        progress_data = [
            Progress(user_id=new_user.id, module_name='Kali Linux', score=92),
            Progress(user_id=new_user.id, module_name='IoT Networks', score=78),
            Progress(user_id=new_user.id, module_name='Adv. Python', score=45),
            Progress(user_id=new_user.id, module_name='Overall GPA', score=86) # 8.6 -> 86 for simple math or keep as int
        ]
        db.session.add_all(progress_data)
        db.session.commit()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({"success": False, "message": "Password is required"}), 400
    
    # Authenticate 'allan' directly for this single user app
    user = User.query.filter_by(username='allan').first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({"success": True, "token": access_token})
    else:
        return jsonify({"success": False, "message": "Invalid password"}), 401

@app.route('/api/progress', methods=['GET'])
@jwt_required()
def get_progress():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
        
    progress_records = Progress.query.filter_by(user_id=user.id).all()
    results = {p.module_name: p.score for p in progress_records}
    
    return jsonify({"success": True, "progress": results})

@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    global fallback_index
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"success": False, "message": "Message is required"}), 400
    
    msg = data['message'].lower()
    reply = None
    
    for r in RESPONSES:
        for keyword in r['k']:
            if keyword in msg:
                reply = r['r']
                break
        if reply:
            break
            
    if not reply:
        reply = FALLBACK[fallback_index % len(FALLBACK)]
        fallback_index += 1
        
    return jsonify({"success": True, "reply": reply})

if __name__ == '__main__':
    print("Starting Nexus Grand Tome Theatre Backend on port 5000...")
    app.run(debug=True, port=5000)
