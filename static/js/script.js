// Attendance Tracker JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const attendanceForm = document.getElementById('attendanceForm');
    const recordIdField = document.getElementById('recordId');
    const studentIdField = document.getElementById('student_id');
    const nameField = document.getElementById('name');
    const classField = document.getElementById('class');
    const dateField = document.getElementById('date');
    const submitBtn = document.getElementById('submitBtn');
    const updateBtn = document.getElementById('updateBtn');
    const clearBtn = document.getElementById('clearBtn');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const showAllBtn = document.getElementById('showAllBtn');
    const recordsContainer = document.getElementById('recordsContainer');
    
    // Set current date as default for date field
    dateField.valueAsDate = new Date();
    
    // Clear form function
    function clearForm() {
        attendanceForm.reset();
        recordIdField.value = '';
        submitBtn.style.display = 'inline-block';
        updateBtn.style.display = 'none';
        attendanceForm.action = '/add';
        dateField.valueAsDate = new Date();
    }
    
    // Clear button click handler
    clearBtn.addEventListener('click', clearForm);
    
    // Edit button click handler (using event delegation)
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('edit-btn')) {
            const recordId = e.target.getAttribute('data-id');
            
            // Get record data
            fetch(`/api/record/${recordId}`)
                .then(response => response.json())
                .then(data => {
                    // Fill the form with record data
                    recordIdField.value = data.id;
                    studentIdField.value = data.student_id;
                    nameField.value = data.name;
                    classField.value = data.class_name;
                    dateField.value = data.date;
                    
                    // Change form appearance for update mode
                    submitBtn.style.display = 'none';
                    updateBtn.style.display = 'inline-block';
                    
                    // Scroll to form
                    window.scrollTo({
                        top: attendanceForm.offsetTop - 100,
                        behavior: 'smooth'
                    });
                })
                .catch(error => console.error('Error fetching record:', error));
        }
    });
    
    // Update button click handler
    updateBtn.addEventListener('click', function() {
        const recordId = recordIdField.value;
        if (recordId) {
            // Change form action to update endpoint
            attendanceForm.action = `/update/${recordId}`;
            attendanceForm.submit();
        }
    });
    
    // Search functionality
    searchBtn.addEventListener('click', function() {
        const searchTerm = searchInput.value.trim();
        
        // Fetch search results
        fetch(`/search?search=${encodeURIComponent(searchTerm)}`)
            .then(response => response.text())
            .then(html => {
                recordsContainer.innerHTML = html;
            })
            .catch(error => console.error('Error searching records:', error));
    });
    
    // Show all records
    showAllBtn.addEventListener('click', function() {
        searchInput.value = '';
        
        // Fetch all records
        fetch('/search')
            .then(response => response.text())
            .then(html => {
                recordsContainer.innerHTML = html;
            })
            .catch(error => console.error('Error fetching records:', error));
    });
    
    // Search on Enter key press
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });
});