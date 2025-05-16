"""
Attendance Tracker Web Application
A web application for tracking student attendance using Flask and SQLite database.
Enhanced with authentication and report generation.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import os
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check if DATABASE_URL environment variable exists
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    # Replace postgres:// with postgresql:// for SQLAlchemy 1.4+
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # For flash messages and session
db = SQLAlchemy(app)

# User model for authentication
class User(db.Model):
    """
    User model for authentication
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='teacher')  # 'admin' or 'teacher'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

class Attendance(db.Model):
    """
    Attendance model for database.
    """
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f"<Attendance {self.id}: {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'class_name': self.class_name,
            'date': self.date
        }

# Initialize database
with app.app_context():
    db.create_all()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first.', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/init-admin')
def init_admin():
    """
    Initialize admin user (only for setup)
    """
    try:
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            return jsonify({"message": "Admin user already exists"})
        
        # Create admin user
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.role = 'admin'
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({"message": "Admin user created successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    User logout
    """
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    """
    Register new users (admin only)
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'teacher')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} has been created successfully', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('register.html')

@app.route('/')
def index():
    """
    Redirect to login or dashboard
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard page after login
    """
    records = Attendance.query.order_by(Attendance.id.desc()).all()
    classes = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"]
    return render_template('dashboard.html', records=records, classes=classes)

@app.route('/add', methods=['POST'])
@login_required
def add_record():
    """
    Add a new attendance record.
    """
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        class_name = request.form.get('class')
        date = request.form.get('date')
        
        # Validate inputs
        if not student_id or not name or not class_name or not date:
            flash('All fields are required!', 'danger')
            return redirect(url_for('dashboard'))
        
        # Create a new attendance record
        new_record = Attendance()
        new_record.student_id = student_id
        new_record.name = name
        new_record.class_name = class_name
        new_record.date = date
        
        # Add to database
        db.session.add(new_record)
        db.session.commit()
        
        flash('Record added successfully!', 'success')
        return redirect(url_for('dashboard'))

@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update_record(id):
    """
    Update an existing attendance record.
    """
    record = Attendance.query.get_or_404(id)
    
    if request.method == 'POST':
        record.student_id = request.form.get('student_id')
        record.name = request.form.get('name')
        record.class_name = request.form.get('class')
        record.date = request.form.get('date')
        
        # Validate inputs
        if not record.student_id or not record.name or not record.class_name or not record.date:
            flash('All fields are required!', 'danger')
            return redirect(url_for('dashboard'))
        
        # Commit changes
        db.session.commit()
        
        flash('Record updated successfully!', 'success')
        return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
@login_required
def delete_record(id):
    """
    Delete an attendance record.
    """
    record = Attendance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/search')
@login_required
def search_records():
    """
    Search for records based on search term.
    """
    search_term = request.args.get('search', '')
    
    if search_term:
        # Search in name, student_id or date
        records = Attendance.query.filter(
            (Attendance.name.contains(search_term)) | 
            (Attendance.student_id.contains(search_term)) |
            (Attendance.date.contains(search_term))
        ).order_by(Attendance.id.desc()).all()
    else:
        records = Attendance.query.order_by(Attendance.id.desc()).all()
    
    return render_template('_records.html', records=records)

@app.route('/api/record/<int:id>')
@login_required
def get_record(id):
    """
    Get record data for editing.
    """
    record = Attendance.query.get_or_404(id)
    return jsonify(record.to_dict())

# Admin User Management
@app.route('/admin/users')
@admin_required
def admin_users():
    """
    User management page (admin only)
    """
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/delete/<int:id>')
@admin_required
def delete_user(id):
    """
    Delete a user (admin only)
    """
    if id == session.get('user_id'):
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin_users'))
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted', 'success')
    return redirect(url_for('admin_users'))

# Report Generation
@app.route('/reports')
@login_required
def reports():
    """
    Report generation page
    """
    classes = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"]
    return render_template('reports.html', classes=classes)

@app.route('/generate-report', methods=['POST'])
@login_required
def generate_report():
    """
    Generate attendance report based on filters
    """
    report_type = request.form.get('report_type')
    class_filter = request.form.get('class_filter')
    date_from = request.form.get('date_from')
    date_to = request.form.get('date_to')
    
    # Base query
    query = Attendance.query
    
    # Apply filters
    if class_filter and class_filter != 'all':
        query = query.filter_by(class_name=class_filter)
        
    if date_from:
        query = query.filter(Attendance.date >= date_from)
        
    if date_to:
        query = query.filter(Attendance.date <= date_to)
    
    # Execute query
    records = query.order_by(Attendance.date.desc()).all()
    
    # Generate CSV if requested
    if report_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Student ID', 'Name', 'Class', 'Date'])
        
        # Write data
        for record in records:
            writer.writerow([
                record.id,
                record.student_id,
                record.name,
                record.class_name,
                record.date
            ])
            
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=attendance_report.csv"}
        )
    
    # Otherwise, show results on page
    return render_template('report_results.html', records=records, 
                          class_filter=class_filter, 
                          date_from=date_from, 
                          date_to=date_to)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)