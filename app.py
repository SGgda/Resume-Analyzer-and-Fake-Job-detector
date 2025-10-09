import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# Import our existing functions
from resume_parser import load_resumes_from_directory
from analyzer import rank_resumes

# Define the folder for temporary file uploads
UPLOAD_FOLDER = 'uploads'

# Create the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route to handle the form display and the analysis process.
    """
    if request.method == 'POST':
        # --- Handle the form submission ---

        # 1. Get the job description from the form
        job_description = request.form.get('job_description')

        # 2. Get the uploaded resume files
        uploaded_files = request.files.getlist('resumes')

        if not job_description or not uploaded_files:
            # If something is missing, show an error (or just reload the page)
            return render_template('index.html', error="Please provide a job description and at least one resume.")

        # 3. Save the uploaded files to the 'uploads' directory
        for file in uploaded_files:
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 4. Process the resumes using our existing functions
        resumes_data = load_resumes_from_directory(app.config['UPLOAD_FOLDER'])
        
        # ==========================================================
        # <<< ADDED FOR DEBUGGING >>>
        # This section prints the raw text to your terminal so we can see what the model is analyzing.
        print("\n" + "="*50)
        print("DEBUGGING: RAW TEXT INPUTS TO THE ANALYZER")
        print("="*50)
        print("\n----------- JOB DESCRIPTION -----------")
        print(job_description)
        print("\n----------- EXTRACTED RESUME TEXT -----------")
        for filename, text in resumes_data.items():
            print(f"--- From file: {filename} ---")
            print(text)
        print("\n" + "="*50 + "\n")
        # <<< END OF DEBUGGING SECTION >>>
        # ==========================================================

        sorted_resumes = rank_resumes(job_description, resumes_data)

        # 5. Clean up the uploaded files after analysis
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
            
        # 6. Render the page again, but this time with the results
        return render_template('index.html', results=sorted_resumes, job_description=job_description)

    # --- For a GET request, just show the main page ---
    return render_template('index.html')

if __name__ == '__main__':
    # Run the web app
    app.run(debug=True)