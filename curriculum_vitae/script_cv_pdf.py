import os
import pdfplumber
import re
import shutil

it_keywords = [
    "Python", "Java", "C++", "JavaScript", "SQL", "HTML", "CSS", "PHP", "Ruby",
    "Go", "Linux", "Docker", "Kubernetes", "AWS", "Azure", "Machine Learning", "Data Science",
    "Artificial Intelligence", "TensorFlow", "PyTorch", "Git", "MongoDB", "Node.js",
    "React", "Vue.js", "Hadoop", "Spark", "NoSQL", "GitHub", "MySQL", "PostgreSQL", "Django",
    "Flask", "DevOps", "Cloud Computing", "Developer", "Web Developer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Software Engineer", "DevOps Engineer", "Mobile Developer", "Game Developer",
    "UI/UX Designer", "App Developer", "Web Designer", "Systems Engineer", "IT Specialist",
    "Network Engineer", "Database Administrator", "Cloud Engineer", "Embedded Systems Developer",
    "Automation Engineer", "IT Consultant", "Security Engineer", "Data Analyst", "Data Engineer",
    "Blockchain Developer", "AI Engineer", "Machine Learning Engineer", "Digital Transformation"
]


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


def find_it_skills(text):
    """
    Find IT skills in the given text and return a list of found skills.

    Parameters:
    text (str): The text in which IT skills will be searched.

    Returns:
    list: A list of IT skills found in the text.
    """
    found_skills = []
    for keyword in it_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            found_skills.append(keyword)
    return found_skills


def analyze_pdfs_in_folder(folder_path, output_folder):
    """
    Analyzes PDF files in a folder and extracts IT skills from them.

    Args:
        folder_path (str): The path to the folder containing PDF files.
        output_folder (str): The path to the folder where the results will be saved.

    Returns:
        list: A list of tuples containing the filename and found IT skills for files with at least 7 skills.
    """
    results = []
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    total_files = len(pdf_files)
    last_progress = 0
    for index, filename in enumerate(pdf_files):
        pdf_path = os.path.join(folder_path, filename)
        try:
            text = extract_text_from_pdf(pdf_path)
            skills = find_it_skills(text)
            if skills:
                if len(skills) >= 7:
                    results.append((filename, skills))
                    shutil.copy(pdf_path, os.path.join(output_folder, filename))
        except Exception as e:
            print(f"Error processing {filename}: {e}")
        progress = (index + 1) / total_files * 100
        if int(progress) % 10 == 0 and int(progress) != last_progress:
            print(f"Processed {index + 1} of {total_files} files ({progress:.2f}%)")
            last_progress = int(progress)
    results.sort(key=lambda x: x[0].lower())
    return results


folder_path = 'pdf'
output_folder = 'pdf_it'

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(output_folder):
    shutil.rmtree(output_folder)

os.makedirs(output_folder)

matching_files = analyze_pdfs_in_folder(folder_path, output_folder)

if matching_files:
    print("\nThe following resumes have at least 7 IT skills:")
    for file, skills in matching_files:
        print(f"{file}: {', '.join(skills)}")
else:
    print("No resumes with at least 7 IT skills found.")
