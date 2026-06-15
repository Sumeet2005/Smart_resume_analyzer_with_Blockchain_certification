"""
Resume Parser Module
Extracts text and key information from PDF/DOCX resumes
"""

import PyPDF2
from docx import Document
import re
import uuid
from datetime import datetime

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def parse_resume(uploaded_file):
    """
    Main parsing function
    Determines file type and extracts text
    """
    file_type = uploaded_file.type
    
    if "pdf" in file_type.lower():
        return extract_text_from_pdf(uploaded_file)
    elif "word" in file_type.lower() or "document" in file_type.lower():
        return extract_text_from_docx(uploaded_file)
    else:
        return "Error: Unsupported file format. Please upload PDF or DOCX."

def extract_name(text):
    """
    Extract candidate name from resume
    Assumes name is in first few lines
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Check first 5 non-empty lines
    for line in lines[:5]:
        # Name is usually 2-4 words, no special characters
        words = line.split()
        if 2 <= len(words) <= 4 and all(word.replace('.','').isalpha() for word in words):
            return line
    
    return "Name Not Found"

def extract_email(text):
    """Extract email address using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    """Extract phone number"""
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{10}',
        r'\+\d{12}'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return "Not found"

def extract_skills(text):
    """
    Extract technical skills using keyword matching
    """
    # Common technical skills database
    skill_keywords = [
        # Programming Languages
        'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby',
        'go', 'swift', 'kotlin', 'typescript', 'scala', 'rust',
        
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'nodejs',
        'express', 'django', 'flask', 'spring', 'asp.net', 'laravel',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis',
        'sqlite', 'cassandra', 'dynamodb',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'git', 'github', 'gitlab', 'ci/cd', 'terraform',
        
        # Data Science & ML
        'machine learning', 'ml', 'ai', 'deep learning', 'tensorflow',
        'pytorch', 'scikit-learn', 'pandas', 'numpy', 'jupyter',
        'data analysis', 'data science', 'nlp', 'computer vision',
        
        # Others
        'linux', 'android', 'ios', 'rest api', 'graphql', 'microservices',
        'agile', 'scrum', 'jira', 'blockchain', 'ethereum'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            # Capitalize properly
            found_skills.append(skill.title())
    
    # Remove duplicates and return
    return sorted(list(set(found_skills)))

def extract_experience(text):
    """
    Extract years of experience
    Looks for patterns like "3 years experience", "2+ years", etc.
    """
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*years?',
        r'(\d+)\s*years?\s*(?:in|as)',
        r'(\d+)\+?\s*yrs'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            years = match.group(1)
            return f"{years} years"
    
    # If no explicit mention, try to count work experiences
    # Simple heuristic: look for year ranges
    year_ranges = re.findall(r'(20\d{2})\s*[-–]\s*(20\d{2}|present|current)', text, re.IGNORECASE)
    
    if year_ranges:
        total_years = 0
        for start, end in year_ranges:
            start_year = int(start)
            end_year = datetime.now().year if 'present' in end.lower() or 'current' in end.lower() else int(end)
            total_years += (end_year - start_year)
        
        if total_years > 0:
            return f"~{total_years} years"
    
    return "Not specified"

def extract_education(text):
    """Extract education details"""
    education_keywords = [
        'b.tech', 'bachelor', 'btech', 'b.e', 'b.sc',
        'm.tech', 'master', 'mtech', 'm.e', 'm.sc',
        'mba', 'phd', 'doctorate',
        'diploma', 'high school'
    ]
    
    found_education = []
    lines = text.lower().split('\n')
    
    for line in lines:
        for keyword in education_keywords:
            if keyword in line:
                found_education.append(line.strip())
                break
    
    return found_education[:3] if found_education else ["Not specified"]

def extract_projects(text):
    """
    Extract project information
    Looks for sections labeled "projects" or "work"
    """
    projects = []
    
    # Split text into sections
    sections = re.split(r'\n(?=projects|work experience|experience)', text, flags=re.IGNORECASE)
    
    for section in sections:
        if 'project' in section.lower():
            # Extract project names (usually in bold or after bullets)
            project_lines = section.split('\n')
            for line in project_lines[1:10]:  # Skip header, take next 10 lines
                if line.strip() and not line.strip().startswith(('•', '-', '*')):
                    if len(line.split()) <= 8:  # Likely a project title
                        projects.append(line.strip())
    
    return projects[:5] if projects else ["Not specified"]

def generate_candidate_id():
    """Generate a globally unique candidate ID using UUID4."""
    return f"CAND-{uuid.uuid4().hex[:16].upper()}"

# Test function
if __name__ == "__main__":
    print("Resume Parser Module - Ready!")
    print("Functions available:")
    print("- parse_resume(file)")
    print("- extract_skills(text)")
    print("- extract_name(text)")
    print("- extract_experience(text)")
