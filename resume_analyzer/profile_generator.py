"""
Profile Generator Module
Creates detailed candidate profiles for interview preparation
"""

def generate_candidate_profile(resume_data):
    """
    Generate organized profile summary
    Returns: Dictionary with categorized information
    """
    profile = {
        'personal_info': {
            'name': resume_data.get('name', 'N/A'),
            'email': resume_data.get('email', 'N/A'),
            'phone': resume_data.get('phone', 'N/A'),
        },
        'professional_summary': {
            'skills': resume_data.get('skills', []),
            'experience': resume_data.get('experience', 'Not specified'),
            'total_skills': len(resume_data.get('skills', [])),
        },
        'projects': resume_data.get('projects', ['Not specified']),
        'education': resume_data.get('education', ['Not specified']),
        'match_score': resume_data.get('score', 0),
        'match_category': get_match_category(resume_data.get('score', 0))
    }
    
    return profile

def get_match_category(score):
    """Categorize match quality"""
    if score >= 80:
        return "⭐ Excellent Match"
    elif score >= 60:
        return "✅ Good Match"
    elif score >= 40:
        return "🔶 Fair Match"
    else:
        return "⚠️ Poor Match"

def format_skills_for_display(skills):
    """Format skills list for UI display"""
    if not skills:
        return "No skills extracted"
    
    # Group by category (simplified)
    tech_skills = []
    other_skills = []
    
    tech_keywords = ['python', 'java', 'javascript', 'react', 'django', 
                     'sql', 'aws', 'docker', 'git', 'node']
    
    for skill in skills:
        if any(keyword in skill.lower() for keyword in tech_keywords):
            tech_skills.append(skill)
        else:
            other_skills.append(skill)
    
    return {
        'technical': tech_skills,
        'other': other_skills
    }

# Test
if __name__ == "__main__":
    print("✅ Profile Generator Module Ready!")
