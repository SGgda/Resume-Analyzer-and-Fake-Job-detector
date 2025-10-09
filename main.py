# Import the functions from our other two files
from resume_parser import load_resumes_from_directory
from analyzer import rank_resumes

# --- CONFIGURATION ---

# 1. Define the folder where you have stored the resumes
RESUMES_DIRECTORY = 'resumes'

# 2. Paste the job description you want to match against.
#    I've added a sample one for a "Software Engineer" role.
#    <<< YOU CAN REPLACE THE TEXT BETWEEN THE TRIPLE QUOTES WITH ANY JOB DESCRIPTION >>>
JOB_DESCRIPTION = """
Job Title: Software Engineer (AI/ML)

Summary:
We are seeking a talented Software Engineer with a keen interest in AI/ML to join our innovative team.
The ideal candidate will have a strong foundation in computer science, algorithms, and data structures.
This role involves developing scalable software solutions and contributing to our machine learning projects.
Experience in full-stack web development is a significant advantage.

Responsibilities:
- Write clean, scalable, and efficient code in Python.
- Develop and maintain web applications and backend services.
- Collaborate with data scientists to implement AI/ML models.
- Participate in competitive programming challenges to sharpen skills.

Required Skills & Qualifications:
- Bachelor's degree in Computer Science or related field.
- Strong proficiency in Python.
- Experience with full-stack development (e.g., Django, Flask, React).
- Knowledge of machine learning concepts and libraries (e.g., scikit-learn, TensorFlow).
- Familiarity with databases like SQL.
- Excellent problem-solving abilities.
"""

def main():
    """The main function to orchestrate the resume analysis."""
    print("--- Starting Resume Analyzer ---")

    # Step 1: Load all resumes from the directory using our parser
    resumes_data = load_resumes_from_directory(RESUMES_DIRECTORY)

    # Check if any resumes were loaded
    if not resumes_data:
        print(f"No resumes were found in the '{RESUMES_DIRECTORY}' directory. Please add some and try again.")
        return  # Exit the program if no resumes

    print(f"\nSuccessfully loaded {len(resumes_data)} resumes.")
    
    # Step 2: Pass the job description and resumes to our analyzer for ranking
    print("Analyzing and ranking resumes against the job description...")
    sorted_resumes = rank_resumes(JOB_DESCRIPTION, resumes_data)

    # Step 3: Display the final, ranked results
    print("\n" + "="*40)
    print("      RESUME ANALYSIS RESULTS")
    print("="*40)

    if not sorted_resumes:
        print("Could not generate rankings. Please check the inputs.")
        return

    # Print each resume's rank, filename, and score
    for rank, (filename, score) in enumerate(sorted_resumes, 1):
        # Format the score as a percentage
        match_percentage = score * 100
        print(f"\nRank #{rank}")
        print(f"  -> File: {filename}")
        print(f"  -> Match Score: {match_percentage:.2f}%")
        print("-" * 30)

# This makes the script runnable
if __name__ == '__main__':
    main()