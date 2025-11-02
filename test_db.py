from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from functools import wraps
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['college_events']
staff_collection = db['staff']
events_collection = db['events']
registrations_collection = db['registrations']

# File Upload Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'events')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_id' not in session:
            flash('Please login first', 'danger')
            return redirect(url_for('staff_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== HOME & PUBLIC ROUTES ==========

@app.route('/')
def index():
    """Home Page"""
    events = list(events_collection.find().sort('date', -1).limit(6))
    for event in events:
        event['_id'] = str(event['_id'])
    return render_template('index.html', events=events)

# ========== EVENTS ROUTES ==========

@app.route('/events')
def events_list():
    """View All Events"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = {}
    if category:
        query['category'] = category
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    events = list(events_collection.find(query).sort('date', -1))
    for event in events:
        event['_id'] = str(event['_id'])
    
    return render_template('events/events_list.html', events=events)

@app.route('/event/<event_id>')
def event_detail(event_id):
    """Event Details Page"""
    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event:
            flash('Event not found', 'danger')
            return redirect(url_for('events_list'))
        event['_id'] = str(event['_id'])
        event['staff_id'] = str(event['staff_id'])
        return render_template('events/event_detail.html', event=event)
    except:
        flash('Invalid event ID', 'danger')
        return redirect(url_for('events_list'))

@app.route('/register-event/<event_id>', methods=['GET', 'POST'])
def register_event(event_id):
    """Register for Event"""
    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event:
            flash('Event not found', 'danger')
            return redirect(url_for('events_list'))
        
        if request.method == 'POST':
            student_name = request.form.get('student_name', '').strip()
            student_email = request.form.get('student_email', '').strip()
            student_phone = request.form.get('student_phone', '').strip()
            college = request.form.get('college', '').strip()
            
            if not all([student_name, student_email, student_phone, college]):
                flash('All fields are required', 'danger')
                return redirect(url_for('register_event', event_id=event_id))
            
            existing = registrations_collection.find_one({
                'event_id': event_id,
                'student_email': student_email
            })
            
            if existing:
                flash('You are already registered for this event', 'info')
                return redirect(url_for('event_detail', event_id=event_id))
            
            registrations_collection.insert_one({
                'event_id': event_id,
                'student_name': student_name,
                'student_email': student_email,
                'student_phone': student_phone,
                'college': college,
                'registered_at': datetime.now()
            })
            
            flash('Event registered successfully!', 'success')
            return redirect(url_for('event_detail', event_id=event_id))
        
        event['_id'] = str(event['_id'])
        return render_template('events/register_event.html', event=event)
    except:
        flash('Invalid event ID', 'danger')
        return redirect(url_for('events_list'))

# ========== STAFF AUTHENTICATION ==========

@app.route('/staff/register', methods=['GET', 'POST'])
def staff_register():
    """Staff Registration"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        department = request.form.get('department', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not all([name, email, username, password, department, phone]):
            flash('All fields are required', 'danger')
            return redirect(url_for('staff_register'))
        
        if staff_collection.find_one({'email': email}):
            flash('Email already registered', 'danger')
            return redirect(url_for('staff_register'))
        
        if staff_collection.find_one({'username': username}):
            flash('Username already taken', 'danger')
            return redirect(url_for('staff_register'))
        
        staff_collection.insert_one({
            'name': name,
            'email': email,
            'username': username,
            'password': generate_password_hash(password),
            'department': department,
            'phone': phone,
            'created_at': datetime.now()
        })
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('staff_login'))
    
    return render_template('auth/staff_register.html')

@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    """Staff Login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('staff_login'))
        
        staff = staff_collection.find_one({'username': username})
        
        if staff and check_password_hash(staff['password'], password):
            session['staff_id'] = str(staff['_id'])
            session['staff_name'] = staff['name']
            flash(f'Welcome {staff["name"]}!', 'success')
            return redirect(url_for('staff_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/staff_login.html')

@app.route('/staff/logout')
def staff_logout():
    """Staff Logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ========== STAFF DASHBOARD & EVENTS ==========

@app.route('/staff/dashboard')
@login_required
def staff_dashboard():
    """Staff Dashboard"""
    staff_id = ObjectId(session['staff_id'])
    events = list(events_collection.find({'staff_id': staff_id}).sort('date', -1))
    
    for event in events:
        event['_id'] = str(event['_id'])
        event['registrations_count'] = registrations_collection.count_documents({'event_id': str(event['_id'])})
    
    return render_template('staff/dashboard.html', events=events)

@app.route('/staff/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create New Event"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        venue = request.form.get('venue', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()
        category = request.form.get('category', '').strip()
        capacity = request.form.get('capacity', '0')
        image = request.files.get('image')
        
        if not all([title, description, venue, date, time, category, capacity]):
            flash('All fields are required', 'danger')
            return redirect(url_for('create_event'))
        
        image_data = None
        if image and image.filename:
            if allowed_file(image.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{image.filename}")
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_data = filename
            else:
                flash('Invalid image format. Allowed: png, jpg, jpeg, gif', 'danger')
                return redirect(url_for('create_event'))
        
        events_collection.insert_one({
            'title': title,
            'description': description,
            'venue': venue,
            'date': date,
            'time': time,
            'category': category,
            'capacity': int(capacity),
            'staff_id': ObjectId(session['staff_id']),
            'image': image_data,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    
    return render_template('staff/create_event.html')

@app.route('/staff/edit-event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Edit Event"""
    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event or str(event['staff_id']) != session['staff_id']:
            flash('Unauthorized', 'danger')
            return redirect(url_for('staff_dashboard'))
        
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            venue = request.form.get('venue', '').strip()
            date = request.form.get('date', '').strip()
            time = request.form.get('time', '').strip()
            category = request.form.get('category', '').strip()
            capacity = request.form.get('capacity', '0')
            image = request.files.get('image')
            
            if not all([title, description, venue, date, time, category, capacity]):
                flash('All fields are required', 'danger')
                return redirect(url_for('edit_event', event_id=event_id))
            
            update_data = {
                'title': title,
                'description': description,
                'venue': venue,
                'date': date,
                'time': time,
                'category': category,
                'capacity': int(capacity),
                'updated_at': datetime.now()
            }
            
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{image.filename}")
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                update_data['image'] = filename
            
            events_collection.update_one({'_id': ObjectId(event_id)}, {'$set': update_data})
            flash('Event updated successfully!', 'success')
            return redirect(url_for('staff_dashboard'))
        
        event['_id'] = str(event['_id'])
        return render_template('staff/edit_event.html', event=event)
    except:
        flash('Event not found', 'danger')
        return redirect(url_for('staff_dashboard'))

@app.route('/staff/delete-event/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    """Delete Event"""
    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event or str(event['staff_id']) != session['staff_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        events_collection.delete_one({'_id': ObjectId(event_id)})
        registrations_collection.delete_many({'event_id': event_id})
        return jsonify({'success': True, 'message': 'Event deleted successfully'})
    except:
        return jsonify({'success': False, 'message': 'Error deleting event'}), 400

@app.route('/staff/my-events')
@login_required
def my_events():
    """View Staff's Events"""
    staff_id = ObjectId(session['staff_id'])
    events = list(events_collection.find({'staff_id': staff_id}).sort('date', -1))
    
    for event in events:
        event['_id'] = str(event['_id'])
        event['registrations_count'] = registrations_collection.count_documents({'event_id': str(event['_id'])})
    
    return render_template('staff/my_events.html', events=events)

@app.route('/staff/event-registrations/<event_id>')
@login_required
def event_registrations(event_id):
    """View Event Registrations"""
    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event or str(event['staff_id']) != session['staff_id']:
            flash('Unauthorized', 'danger')
            return redirect(url_for('staff_dashboard'))
        
        registrations = list(registrations_collection.find({'event_id': event_id}))
        for reg in registrations:
            reg['_id'] = str(reg['_id'])
        
        event['_id'] = str(event['_id'])
        return render_template('staff/event_registrations.html', event=event, registrations=registrations)
    except:
        flash('Event not found', 'danger')
        return redirect(url_for('staff_dashboard'))

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
