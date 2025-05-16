"""
Attendance Tracker Application
A desktop application for tracking student attendance using Tkinter GUI and SQLite database.
"""

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from datetime import datetime
from tkcalendar import DateEntry

class AttendanceTracker:
    """
    Main application class for the Attendance Tracker.
    Handles UI setup and database operations.
    """
    
    def __init__(self, root):
        """
        Initialize the application with UI components and database connection.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.setup_window()
        self.create_fonts()
        self.setup_variables()
        self.setup_database()
        self.setup_ui()
        self.load_records()
        
    def setup_window(self):
        """Configure the main application window."""
        self.root.title("Student Attendance Tracker")
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        self.root.configure(bg="#f0f0f0")
        
    def create_fonts(self):
        """Define custom fonts for the application."""
        self.title_font = ("Helvetica", 18, "bold")
        self.header_font = ("Helvetica", 12, "bold")
        self.label_font = ("Arial", 10)
        self.button_font = ("Arial", 10, "bold")
        
    def setup_variables(self):
        """Initialize tkinter variables for form inputs."""
        self.student_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.selected_id = None
        
    def setup_database(self):
        """Create and connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect('attendance.db')
            self.cursor = self.conn.cursor()
            # Create table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    class TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            
    def setup_ui(self):
        """Create the user interface with all components."""
        self.create_header()
        self.create_form()
        self.create_table()
        self.create_footer()
        self.create_menu()
        
    def create_header(self):
        """Create the application header section."""
        header_frame = tk.Frame(self.root, bg="#4a7abc", height=60)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="Student Attendance Tracker", 
            font=self.title_font, 
            bg="#4a7abc", 
            fg="white",
            pady=10
        )
        title_label.pack()
        
    def create_form(self):
        """Create the input form section."""
        form_frame = tk.Frame(self.root, bg="#f0f0f0", pady=15)
        form_frame.pack(fill=tk.X, padx=20)
        
        # Form heading
        form_label = tk.Label(
            form_frame, 
            text="Attendance Details", 
            font=self.header_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        form_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        # Student ID
        id_label = tk.Label(
            form_frame, 
            text="Student ID:", 
            font=self.label_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        id_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        id_entry = tk.Entry(
            form_frame, 
            textvariable=self.student_id_var, 
            font=self.label_font, 
            width=15
        )
        id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Student Name
        name_label = tk.Label(
            form_frame, 
            text="Name:", 
            font=self.label_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        name_label.grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        
        name_entry = tk.Entry(
            form_frame, 
            textvariable=self.name_var, 
            font=self.label_font, 
            width=25
        )
        name_entry.grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Class/Section
        class_label = tk.Label(
            form_frame, 
            text="Class:", 
            font=self.label_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        class_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        class_values = ["I-MCA-A", "II-MCA-A", "I-MCA-B", "II-MCA-B"]
        class_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.class_var, 
            values=class_values, 
            font=self.label_font, 
            width=13
        )
        class_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Date
        date_label = tk.Label(
            form_frame, 
            text="Date:", 
            font=self.label_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        date_label.grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        
        self.date_picker = DateEntry(
            form_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2, 
            font=self.label_font,
            date_pattern='yyyy-mm-dd'
        )
        self.date_picker.grid(row=2, column=3, sticky=tk.W, pady=5)
        
        # Search frame
        search_frame = tk.Frame(form_frame, bg="#f0f0f0")
        search_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(15, 5))
        
        search_label = tk.Label(
            search_frame, 
            text="Search:", 
            font=self.label_font, 
            bg="#f0f0f0", 
            fg="#333333"
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            font=self.label_font, 
            width=25
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        search_button = tk.Button(
            search_frame, 
            text="Search", 
            font=self.button_font,
            bg="#5c8adc", 
            fg="white", 
            bd=0, 
            padx=10, 
            pady=2,
            command=self.search_records
        )
        search_button.pack(side=tk.LEFT)
        
        show_all_button = tk.Button(
            search_frame, 
            text="Show All", 
            font=self.button_font,
            bg="#6c757d", 
            fg="white", 
            bd=0, 
            padx=10, 
            pady=2,
            command=self.load_records
        )
        show_all_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Button frame
        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.grid(row=4, column=0, columnspan=4, pady=(15, 0))
        
        # Add button
        add_button = tk.Button(
            button_frame, 
            text="Add Record", 
            font=self.button_font,
            bg="#28a745", 
            fg="white", 
            bd=0, 
            padx=15, 
            pady=5,
            command=self.add_record
        )
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Update button
        update_button = tk.Button(
            button_frame, 
            text="Update", 
            font=self.button_font,
            bg="#ffc107", 
            fg="black", 
            bd=0, 
            padx=15, 
            pady=5,
            command=self.update_record
        )
        update_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_button = tk.Button(
            button_frame, 
            text="Delete", 
            font=self.button_font,
            bg="#dc3545", 
            fg="white", 
            bd=0, 
            padx=15, 
            pady=5,
            command=self.delete_record
        )
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_button = tk.Button(
            button_frame, 
            text="Clear", 
            font=self.button_font,
            bg="#6c757d", 
            fg="white", 
            bd=0, 
            padx=15, 
            pady=5,
            command=self.clear_form
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_button = tk.Button(
            button_frame, 
            text="Exit", 
            font=self.button_font,
            bg="#343a40", 
            fg="white", 
            bd=0, 
            padx=15, 
            pady=5,
            command=self.exit_app
        )
        exit_button.pack(side=tk.LEFT, padx=5)
        
    def create_table(self):
        """Create the table view for displaying attendance records."""
        # Table frame with a border
        table_container = tk.Frame(self.root, bg="#d0d0d0", padx=2, pady=2)
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scroll_y = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        
        # Table heading
        columns = ("id", "student_id", "name", "class", "date")
        self.records_table = ttk.Treeview(
            table_container,
            columns=columns,
            yscrollcommand=scroll_y.set,
            show="headings",
            height=10
        )
        
        # Configure scrollbar
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.records_table.yview)
        
        # Define column headings
        self.records_table.heading("id", text="ID")
        self.records_table.heading("student_id", text="Student ID")
        self.records_table.heading("name", text="Name")
        self.records_table.heading("class", text="Class")
        self.records_table.heading("date", text="Date")
        
        # Define column widths
        self.records_table.column("id", width=50)
        self.records_table.column("student_id", width=100)
        self.records_table.column("name", width=200)
        self.records_table.column("class", width=100)
        self.records_table.column("date", width=100)
        
        self.records_table.pack(fill=tk.BOTH, expand=True)
        
        # Bind select event
        self.records_table.bind("<<TreeviewSelect>>", self.select_record)
        
    def create_footer(self):
        """Create the footer section with status bar."""
        footer_frame = tk.Frame(self.root, bg="#e0e0e0", height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = tk.Label(
            footer_frame, 
            textvariable=self.status_var, 
            font=("Arial", 9), 
            bg="#e0e0e0", 
            fg="#333333",
            anchor=tk.W,
            padx=10,
            pady=5
        )
        status_label.pack(fill=tk.X)
        
    def create_menu(self):
        """Create the application menu bar."""
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
    def load_records(self):
        """Load all records from the database into the table view."""
        # Clear the table first
        for row in self.records_table.get_children():
            self.records_table.delete(row)
            
        try:
            # Get all records from the database
            self.cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
            records = self.cursor.fetchall()
            
            # Insert records into the table
            for record in records:
                self.records_table.insert("", "end", values=record)
                
            self.status_var.set(f"Loaded {len(records)} records")
        except sqlite3.Error as e:
            self.status_var.set(f"Error loading records: {e}")
            messagebox.showerror("Database Error", f"Failed to load records: {e}")
            
    def search_records(self):
        """Search for records based on student name or ID."""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self.load_records()
            return
            
        try:
            # Clear the table first
            for row in self.records_table.get_children():
                self.records_table.delete(row)
                
            # Search by name, ID or date
            self.cursor.execute("""
                SELECT * FROM attendance 
                WHERE name LIKE ? OR student_id LIKE ? OR date LIKE ?
                ORDER BY id DESC
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            records = self.cursor.fetchall()
            
            # Insert matching records into the table
            for record in records:
                self.records_table.insert("", "end", values=record)
                
            self.status_var.set(f"Found {len(records)} matching records")
        except sqlite3.Error as e:
            self.status_var.set(f"Error searching records: {e}")
            messagebox.showerror("Database Error", f"Failed to search records: {e}")
            
    def validate_inputs(self):
        """Validate form inputs before database operations."""
        student_id = self.student_id_var.get().strip()
        name = self.name_var.get().strip()
        class_val = self.class_var.get().strip()
        date = self.date_picker.get()
        
        errors = []
        
        if not student_id:
            errors.append("Student ID is required")
        
        if not name:
            errors.append("Name is required")
            
        if not class_val:
            errors.append("Class is required")
            
        if not date:
            errors.append("Date is required")
            
        return (len(errors) == 0, errors, (student_id, name, class_val, date))
    
    def add_record(self):
        """Add a new attendance record to the database."""
        valid, errors, data = self.validate_inputs()
        
        if not valid:
            error_message = "\n".join(errors)
            messagebox.showerror("Validation Error", error_message)
            self.status_var.set("Failed to add record - validation errors")
            return
            
        student_id, name, class_val, date = data
        
        try:
            self.cursor.execute("""
                INSERT INTO attendance (student_id, name, class, date)
                VALUES (?, ?, ?, ?)
            """, (student_id, name, class_val, date))
            
            self.conn.commit()
            self.clear_form()
            self.load_records()
            self.status_var.set("Record added successfully")
            messagebox.showinfo("Success", "Attendance record added successfully")
        except sqlite3.Error as e:
            self.status_var.set(f"Error adding record: {e}")
            messagebox.showerror("Database Error", f"Failed to add record: {e}")
            
    def select_record(self, event):
        """Handle selection of a record in the table view."""
        try:
            # Get selected item
            selected_item = self.records_table.selection()[0]
            values = self.records_table.item(selected_item, "values")
            
            # Store the ID for update/delete operations
            self.selected_id = values[0]
            
            # Populate form with selected record's data
            self.student_id_var.set(values[1])
            self.name_var.set(values[2])
            self.class_var.set(values[3])
            
            # Handle date format for the date picker
            try:
                self.date_picker.set_date(values[4])
            except:
                # If date format is not compatible
                self.date_picker.set_date(datetime.now())
                
            self.status_var.set(f"Selected record ID: {self.selected_id}")
        except IndexError:
            # No selection
            pass
            
    def update_record(self):
        """Update the selected attendance record."""
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a record to update")
            self.status_var.set("No record selected for update")
            return
            
        valid, errors, data = self.validate_inputs()
        
        if not valid:
            error_message = "\n".join(errors)
            messagebox.showerror("Validation Error", error_message)
            self.status_var.set("Failed to update record - validation errors")
            return
            
        student_id, name, class_val, date = data
        
        try:
            self.cursor.execute("""
                UPDATE attendance 
                SET student_id = ?, name = ?, class = ?, date = ?
                WHERE id = ?
            """, (student_id, name, class_val, date, self.selected_id))
            
            self.conn.commit()
            self.clear_form()
            self.load_records()
            self.status_var.set("Record updated successfully")
            messagebox.showinfo("Success", "Attendance record updated successfully")
        except sqlite3.Error as e:
            self.status_var.set(f"Error updating record: {e}")
            messagebox.showerror("Database Error", f"Failed to update record: {e}")
            
    def delete_record(self):
        """Delete the selected attendance record."""
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a record to delete")
            self.status_var.set("No record selected for deletion")
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        
        if not confirm:
            self.status_var.set("Deletion cancelled")
            return
            
        try:
            self.cursor.execute("DELETE FROM attendance WHERE id = ?", (self.selected_id,))
            self.conn.commit()
            self.clear_form()
            self.load_records()
            self.status_var.set("Record deleted successfully")
            messagebox.showinfo("Success", "Attendance record deleted successfully")
        except sqlite3.Error as e:
            self.status_var.set(f"Error deleting record: {e}")
            messagebox.showerror("Database Error", f"Failed to delete record: {e}")
            
    def clear_form(self):
        """Clear all form inputs."""
        self.student_id_var.set("")
        self.name_var.set("")
        self.class_var.set("")
        self.date_picker.set_date(datetime.now())
        self.selected_id = None
        self.status_var.set("Form cleared")
        
    def exit_app(self):
        """Close the database connection and exit the application."""
        confirm = messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?")
        if confirm:
            try:
                # Close database connection
                if hasattr(self, 'conn'):
                    self.conn.close()
            except:
                pass
                
            self.root.destroy()
            
    def show_about(self):
        """Display information about the application."""
        about_text = """
        Student Attendance Tracker
        Version 1.0
        
        A desktop application for tracking student attendance.
        
        Features:
        - Add, update, and delete attendance records
        - Search functionality
        - SQLite database for storage
        """
        
        messagebox.showinfo("About", about_text)

def main():
    """Main function to initialize and run the application."""
    root = tk.Tk()
    app = AttendanceTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
