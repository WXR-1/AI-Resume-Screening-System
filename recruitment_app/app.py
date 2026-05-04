from flask import Flask, render_template, request, redirect, flash, send_from_directory, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-me-in-production')
app.config['HR_LOGIN_USER'] = os.getenv('HR_LOGIN_USER', 'hr')
app.config['HR_LOGIN_PASS'] = os.getenv('HR_LOGIN_PASS', 'admin123')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Decorator to protect HR routes
def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_hr'):
            flash('Please log in to access this page', 'warning')
            return redirect('/hr-login')
        return f(*args, **kwargs)
    return decorated_function

# --------- DATABASE CONNECTION ----------
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
db = sqlite3.connect(db_path, check_same_thread=False)
cursor = db.cursor()

# Create tables if not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    position_applied TEXT,
    skills TEXT,
    experience TEXT,
    status TEXT,
    resume_path TEXT,
    submission_date TEXT
)
''')
db.commit()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'Resumes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_candidate_in_background(name, email, phone, position, skills, experience, file_content, filename):
    """Save file and insert candidate into database in background thread"""
    try:
        resume_path = None
        if file_content and filename and allowed_file(filename):
            filename = secure_filename(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Write bytes directly to file
            with open(filepath, 'wb') as f:
                f.write(file_content)
            resume_path = filename
        
        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a new database connection for the background thread
        db_bg = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'database.db'))
        cursor_bg = db_bg.cursor()
        
        cursor_bg.execute(
            "INSERT INTO candidates (name, email, phone, position_applied, skills, experience, status, resume_path, submission_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, position, skills, experience, "submitted", resume_path, submission_date)
        )
        db_bg.commit()
        db_bg.close()
    except Exception as e:
        print(f"Error saving candidate: {e}")


# ---------- HOME PAGE ----------
@app.route('/')
def home():
    return render_template('home.html')

# ---------- APPLICATION FORM ----------
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        position = request.form.get('position')
        skills = request.form.get('skills')
        experience = request.form.get('experience')
        file = request.files.get('resume')

        # Read file content into memory while in request context
        file_content = None
        filename = None
        if file:
            filename = file.filename
            file_content = file.read()  # Read bytes into memory
        
        # Save file and database in background thread for faster response
        thread = Thread(
            target=save_candidate_in_background,
            args=(name, email, phone, position, skills, experience, file_content, filename)
        )
        thread.daemon = True
        thread.start()

        # Immediately redirect to success page
        return redirect('/success')

    return render_template('apply.html')

# ---------- HR LOGIN ----------
@app.route('/hr-login', methods=['GET', 'POST'])
def hr_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == app.config['HR_LOGIN_USER'] and password == app.config['HR_LOGIN_PASS']:
            session.permanent = True
            session['is_hr'] = True
            return redirect('/dashboard')
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

# ---------- HR DASHBOARD ----------
@app.route('/dashboard')
@hr_required
def dashboard():
    cursor.execute("SELECT * FROM candidates ORDER BY submission_date DESC")
    data = cursor.fetchall()
    return render_template('dashboard.html', data=data)

# ---------- UPDATE STATUS ----------
@app.route('/update/<int:candidate_id>/<status>')
@hr_required
def update_status(candidate_id, status):
    cursor.execute(
        "UPDATE candidates SET status=? WHERE id=?",
        (status, candidate_id)
    )
    db.commit()
    return redirect('/dashboard')

# ---------- DELETE CANDIDATE ----------
@app.route('/delete/<int:candidate_id>')
@hr_required
def delete_candidate(candidate_id):
    cursor.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
    db.commit()
    return redirect('/dashboard')

# ---------- RESUME SERVING ----------
@app.route('/resumes/<path:filename>')
def serve_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- LOGOUT / HOME REDIRECT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------- SUCCESS PAGE ----------
@app.route('/success')
def success():
    return render_template('success.html')

# ---------- RUN APP ----------
if __name__ == '__main__':
    app.run(debug=True)