"""
Attendance Tracker Web Application
A web application for tracking student attendance using Flask and SQLite database.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # For flash messages
db = SQLAlchemy(app)

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

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """
    Render the main page with all attendance records.
    """
    records = Attendance.query.order_by(Attendance.id.desc()).all()
    classes = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"]
    return render_template('index.html', records=records, classes=classes)

@app.route('/add', methods=['POST'])
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
            return redirect(url_for('index'))
        
        # Create a new attendance record
        new_record = Attendance(
            student_id=student_id,
            name=name,
            class_name=class_name,
            date=date
        )
        
        # Add to database
        db.session.add(new_record)
        db.session.commit()
        
        flash('Record added successfully!', 'success')
        return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
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
            return redirect(url_for('index'))
        
        # Commit changes
        db.session.commit()
        
        flash('Record updated successfully!', 'success')
        return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_record(id):
    """
    Delete an attendance record.
    """
    record = Attendance.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/search')
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
def get_record(id):
    """
    Get record data for editing.
    """
    record = Attendance.query.get_or_404(id)
    return jsonify(record.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)