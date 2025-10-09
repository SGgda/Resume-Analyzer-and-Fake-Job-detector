import os
import fitz  # PyMuPDF
import docx
import re # Import the regular expression module

def clean_text(text):
    """
    Cleans the extracted text by stitching together words broken by hyphenation at line breaks.
    
    Args:
        text (str): The raw text extracted from a file.
        
    Returns:
        str: The cleaned text.
    """
    # Stitch together words broken by a hyphen and a newline
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # You can add other cleaning steps here if needed, e.g., removing multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_resumes_from_directory(directory_path):
    """
    Loads all resumes from a directory, extracts their text, and stores it in a dictionary.

    Args:
        directory_path (str): The path to the folder containing resume files.

    Returns:
        dict: A dictionary where keys are filenames and values are the extracted text.
    """
    resumes_data = {}
    supported_formats = ('.pdf', '.docx')
    
    # This print statement is from the original file, it's fine to keep
    # print(f"Scanning for resumes in directory: '{directory_path}'...")
    
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at '{directory_path}'")
        return resumes_data

    for filename in os.listdir(directory_path):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(directory_path, filename)
            # print(f"  -> Processing: {filename}")
            
            # Extract text based on file type
            text = ""
            if filename.lower().endswith('.pdf'):
                try:
                    doc = fitz.open(file_path)
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                except Exception as e:
                    print(f"    Error reading PDF file: {e}")
            
            elif filename.lower().endswith('.docx'):
                try:
                    doc = docx.Document(file_path)
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except Exception as e:
                    print(f"    Error reading DOCX file: {e}")
            
            if text:
                # <<< APPLY THE CLEANING FUNCTION HERE >>>
                cleaned_text = clean_text(text)
                resumes_data[filename] = cleaned_text
    
    return resumes_data

# --- The __main__ block remains the same, no changes needed below this line ---
if __name__ == '__main__':
    RESUMES_DIRECTORY = 'resumes'
    if not os.path.exists(RESUMES_DIRECTORY):
        os.makedirs(RESUMES_DIRECTORY)
        print(f"Please place your resume files inside the '{RESUMES_DIRECTORY}' folder and run the script again.")
    all_resumes_text = load_resumes_from_directory(RESUMES_DIRECTORY)
    if all_resumes_text:
        print(f"\nSuccessfully loaded and processed {len(all_resumes_text)} resumes.")
        for filename, text in all_resumes_text.items():
            print("\n" + "="*50)
            print(f"PREVIEW for: {filename}")
            print("="*50)
            print(text[:400] + "...")
    else:
        print(f"\nNo resumes were loaded. Make sure the '{RESUMES_DIRECTORY}' folder is not empty.")