

from resume_parser import extract_skills, extract_name, extract_experience

# Test text
sample_resume = """
John Doe
john.doe@email.com
+1-234-567-8900

PROFESSIONAL SUMMARY
Software Developer with 3 years of experience in Python and web development.

SKILLS
Python, Django, JavaScript, React, SQL, Git, AWS

EXPERIENCE
Software Engineer at TechCorp (2021 - Present)
- Developed web applications using Django
- Implemented REST APIs

EDUCATION
B.Tech Computer Science, XYZ University (2017-2021)
"""

print("Testing Resume Parser...")
print("="*50)
print(f"Name: {extract_name(sample_resume)}")
print(f"Skills: {extract_skills(sample_resume)}")
print(f"Experience: {extract_experience(sample_resume)}")
print("="*50)
print("✅ Test Complete!")
