document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const form = document.getElementById('diagnosticForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            // Basic validation
            const glucose = document.getElementById('glucose').value;
            const systolic = document.getElementById('systolic_bp').value;
            const diastolic = document.getElementById('diastolic_bp').value;
            const cholesterol = document.getElementById('cholesterol').value;
            
            if (!glucose || !systolic || !diastolic || !cholesterol) {
                event.preventDefault();
                alert('Please fill in all lab result fields');
                return false;
            }
            
            // Validate numeric values
            if (isNaN(glucose) || isNaN(systolic) || isNaN(diastolic) || isNaN(cholesterol)) {
                event.preventDefault();
                alert('Please enter valid numeric values for all lab results');
                return false;
            }
            
            // Validate ranges
            if (glucose < 0 || glucose > 1000) {
                event.preventDefault();
                alert('Please enter a valid glucose level (0-1000 mg/dL)');
                return false;
            }
            
            if (systolic < 0 || systolic > 300) {
                event.preventDefault();
                alert('Please enter a valid systolic blood pressure (0-300 mmHg)');
                return false;
            }
            
            if (diastolic < 0 || diastolic > 200) {
                event.preventDefault();
                alert('Please enter a valid diastolic blood pressure (0-200 mmHg)');
                return false;
            }
            
            if (cholesterol < 0 || cholesterol > 1000) {
                event.preventDefault();
                alert('Please enter a valid cholesterol level (0-1000 mg/dL)');
                return false;
            }
        });
    }
});