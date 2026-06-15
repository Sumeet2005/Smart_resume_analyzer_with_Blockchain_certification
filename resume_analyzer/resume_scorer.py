"""
Resume Scorer Module
Calculates match scores and ATS scores between resumes and job requirements

ATS Score Breakdown (100 points):
  - Skills Match:        30 pts
  - Experience Match:    25 pts
  - Education Keywords:  15 pts
  - Projects/Internships:10 pts
  - Resume Text Quality: 10 pts
  - Certifications:      10 pts
"""

import re


# ──────────────────────────────────────────────────────────────
# EXISTING FUNCTIONS (unchanged)
# ──────────────────────────────────────────────────────────────

def calculate_score(resume_data, job_requirements):
    """
    Calculate comprehensive job-match score (0-100).

    Scoring Breakdown:
    - Skills Match:    40 %
    - Experience Match:30 %
    - Education Match: 15 %
    - Keyword Density: 15 %
    """
    total_score = 0

    # 1. Skills Matching (40 points)
    skills_score = calculate_skills_match(
        resume_data.get('skills', []),
        job_requirements.get('required_skills', [])
    )
    total_score += skills_score * 0.4

    # 2. Experience Matching (30 points)
    exp_score = calculate_experience_match(
        resume_data.get('experience', '0'),
        job_requirements.get('required_experience', 0)
    )
    total_score += exp_score * 0.3

    # 3. Education Matching (15 points)
    edu_score = calculate_education_match(
        resume_data.get('education', []),
        job_requirements.get('required_education', '')
    )
    total_score += edu_score * 0.15

    # 4. Keyword Density (15 points)
    keyword_score = calculate_keyword_match(
        resume_data.get('full_text', ''),
        job_requirements.get('job_description', '')
    )
    total_score += keyword_score * 0.15

    return round(min(total_score, 100), 2)  # Cap at 100


def calculate_skills_match(candidate_skills, required_skills):
    """Calculate percentage of required skills present."""
    if not required_skills:
        return 50  # Default score if no requirements specified

    candidate_skills_lower = [s.lower() for s in candidate_skills]
    required_skills_lower = [s.lower().strip() for s in required_skills]

    matched_skills = set(candidate_skills_lower) & set(required_skills_lower)
    match_percentage = (len(matched_skills) / len(required_skills_lower)) * 100

    return min(match_percentage, 100)


def calculate_experience_match(candidate_exp, required_exp):
    """Calculate experience match score."""
    try:
        candidate_years = int(''.join(filter(str.isdigit, str(candidate_exp))) or 0)
        required_years = int(required_exp)

        if candidate_years >= required_years:
            return 100
        elif candidate_years == 0:
            return 0
        else:
            return (candidate_years / required_years) * 100
    except Exception:
        return 50  # Default if parsing fails


def calculate_education_match(candidate_education, required_education):
    """Calculate education match score."""
    if not required_education:
        return 100  # No specific requirement

    required_lower = required_education.lower()
    candidate_edu_text = ' '.join(candidate_education).lower()

    if required_lower in candidate_edu_text:
        return 100
    elif any(keyword in candidate_edu_text for keyword in ['bachelor', 'b.tech', 'b.e', 'degree']):
        return 70
    else:
        return 30


def calculate_keyword_match(resume_text, job_description):
    """Calculate keyword density match."""
    if not job_description:
        return 50

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    common_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'with'}
    job_words = [w for w in job_lower.split() if w not in common_words and len(w) > 3]

    if not job_words:
        return 50

    matches = sum(1 for word in job_words[:30] if word in resume_lower)
    match_percentage = (matches / min(len(job_words), 30)) * 100
    return min(match_percentage, 100)


def rank_candidates(candidates_list):
    """
    Rank candidates by score (highest first).
    Returns sorted list.
    """
    return sorted(candidates_list, key=lambda x: x.get('score', 0), reverse=True)


def get_match_category(score):
    """Categorize match quality."""
    if score >= 80:
        return "Excellent Match"
    elif score >= 60:
        return "Good Match"
    elif score >= 40:
        return "Fair Match"
    else:
        return "Poor Match"


# ──────────────────────────────────────────────────────────────
# NEW: ATS SCORE CALCULATION  (6 dimensions, 100 pts total)
# ──────────────────────────────────────────────────────────────

# Education degree tier weights
_EDUCATION_TIERS = {
    'phd': 100, 'doctorate': 100,
    'm.tech': 90, 'mtech': 90, 'm.e': 90, 'm.sc': 85, 'mba': 85, 'master': 90, 'msc': 85,
    'b.tech': 75, 'btech': 75, 'b.e': 75, 'b.sc': 70, 'bachelor': 75, 'bsc': 70,
    'diploma': 50, 'high school': 30,
}

# Certification keywords that indicate formal certifications
_CERT_KEYWORDS = [
    'certified', 'certification', 'certificate', 'aws certified', 'azure certified',
    'google certified', 'pmp', 'cpa', 'ccna', 'ceh', 'cissp', 'comptia',
    'oracle certified', 'microsoft certified', 'scrum master', 'six sigma',
    'prince2', 'itil', 'coursera', 'udemy', 'linkedin learning', 'credential',
]

# Resume structure keywords that indicate a well-structured resume
_STRUCTURE_KEYWORDS = [
    'objective', 'summary', 'experience', 'education', 'skills',
    'projects', 'achievements', 'certifications', 'internship', 'publications',
    'awards', 'languages', 'hobbies', 'interests', 'references',
]

# Project / internship indicators
_PROJECT_KEYWORDS = [
    'project', 'internship', 'intern', 'developed', 'built', 'created',
    'implemented', 'designed', 'deployed', 'contributed', 'led', 'managed',
]


def _ats_skills_score(candidate_skills, required_skills, full_text):
    """
    ATS dimension 1 – Skills match (30 pts).
    Combines exact match on required skills + depth bonus for total skills found.
    """
    if not required_skills:
        # No JD skills → reward breadth only
        breadth = min(len(candidate_skills) * 3, 30)
        return breadth

    c_lower = [s.lower() for s in candidate_skills]
    r_lower = [s.lower().strip() for s in required_skills]

    matched = [s for s in r_lower if s in c_lower or s in full_text.lower()]
    match_ratio = len(matched) / len(r_lower)

    # Up to 25 pts for required-skill match + up to 5 pts breadth bonus
    exact_pts = match_ratio * 25
    breadth_bonus = min(len(candidate_skills) / 5, 5)

    return min(exact_pts + breadth_bonus, 30)


def _ats_experience_score(candidate_exp, required_exp):
    """
    ATS dimension 2 – Relevant experience (25 pts).
    Meets or exceeds requirement → full marks.
    Partial experience → proportional credit.
    """
    try:
        digits = ''.join(filter(str.isdigit, str(candidate_exp)))
        cand_years = int(digits) if digits else 0
        req_years = int(required_exp)

        if req_years == 0:
            # No minimum → award based on raw years (capped)
            return min(cand_years * 5, 25)
        if cand_years >= req_years:
            return 25
        return round((cand_years / req_years) * 25, 2)
    except Exception:
        return 12  # Neutral default


def _ats_education_score(full_text):
    """
    ATS dimension 3 – Education keywords (15 pts).
    Detects highest detected degree tier.
    """
    text_lower = full_text.lower()
    best = 0
    for keyword, weight in _EDUCATION_TIERS.items():
        if keyword in text_lower:
            best = max(best, weight)

    # Scale best (0-100) → 0-15 pts
    return round((best / 100) * 15, 2)


def _ats_projects_score(full_text):
    """
    ATS dimension 4 – Projects / internships (10 pts).
    Counts distinct project/internship mentions.
    """
    text_lower = full_text.lower()

    # Count trigger words
    mention_count = sum(1 for kw in _PROJECT_KEYWORDS if kw in text_lower)

    # 1 mention → 3 pts, 3 → 6 pts, 5+ → 10 pts
    pts = min(mention_count * 2, 10)
    return round(pts, 2)


def _ats_text_quality_score(full_text):
    """
    ATS dimension 5 – Resume text quality / structure (10 pts).
    Checks: word count, section headers, sentence length consistency.
    """
    if not full_text or len(full_text.strip()) < 50:
        return 0

    text_lower = full_text.lower()
    words = full_text.split()
    word_count = len(words)

    # Section header score (0-5 pts)
    sections_found = sum(1 for kw in _STRUCTURE_KEYWORDS if kw in text_lower)
    section_pts = min(sections_found * 0.8, 5)

    # Word count score (0-5 pts): 200-700 words is ideal
    if word_count >= 200:
        wc_pts = min((word_count / 700) * 5, 5)
    else:
        wc_pts = (word_count / 200) * 2.5  # Penalise very short

    return round(section_pts + wc_pts, 2)


def _ats_certifications_score(full_text):
    """
    ATS dimension 6 – Certifications detected (10 pts).
    Each unique certification keyword found → pts, capped at 10.
    """
    text_lower = full_text.lower()
    hits = sum(1 for kw in _CERT_KEYWORDS if kw in text_lower)
    return round(min(hits * 2.5, 10), 2)


def calculate_ats_score(candidate_data, job_requirements):
    """
    Calculate ATS Score (0-100) across 6 professional dimensions.

    Args:
        candidate_data  (dict): parsed resume fields + full_text
        job_requirements(dict): required_skills, required_experience, job_description

    Returns:
        dict with keys:
            'ats_score'       – overall ATS score (int, 0-100)
            'skills_pts'      – raw pts from skills dimension
            'experience_pts'  – raw pts from experience dimension
            'education_pts'   – raw pts from education dimension
            'projects_pts'    – raw pts from projects dimension
            'quality_pts'     – raw pts from text quality dimension
            'certifications_pts' – raw pts from certifications dimension
            'skill_match_pct' – % of required skills found (0-100)
    """
    full_text = candidate_data.get('full_text', '')
    candidate_skills = candidate_data.get('skills', [])
    required_skills = job_requirements.get('required_skills', [])
    required_exp = job_requirements.get('required_experience', 0)

    # ── Calculate each dimension ──────────────────────────────
    skills_pts = _ats_skills_score(candidate_skills, required_skills, full_text)
    experience_pts = _ats_experience_score(candidate_data.get('experience', '0'), required_exp)
    education_pts = _ats_education_score(full_text)
    projects_pts = _ats_projects_score(full_text)
    quality_pts = _ats_text_quality_score(full_text)
    cert_pts = _ats_certifications_score(full_text)

    # ── Total ─────────────────────────────────────────────────
    raw_total = skills_pts + experience_pts + education_pts + projects_pts + quality_pts + cert_pts
    ats_score = round(min(raw_total, 100))

    # ── Skill match % (for charts) ───────────────────────────
    if required_skills:
        c_lower = [s.lower() for s in candidate_skills]
        r_lower = [s.lower().strip() for s in required_skills]
        matched = [s for s in r_lower if s in c_lower or s in full_text.lower()]
        skill_match_pct = round((len(matched) / len(r_lower)) * 100, 1)
    else:
        skill_match_pct = round(min(len(candidate_skills) * 10, 100), 1)

    return {
        'ats_score': ats_score,
        'skills_pts': round(skills_pts, 1),
        'experience_pts': round(experience_pts, 1),
        'education_pts': round(education_pts, 1),
        'projects_pts': round(projects_pts, 1),
        'quality_pts': round(quality_pts, 1),
        'certifications_pts': round(cert_pts, 1),
        'skill_match_pct': skill_match_pct,
    }


def get_ats_label(ats_score):
    """Return human-readable ATS tier label."""
    if ats_score >= 80:
        return "🟢 Strong"
    elif ats_score >= 60:
        return "🔵 Good"
    elif ats_score >= 40:
        return "🟡 Average"
    else:
        return "🔴 Weak"


# ── Module self-test ──────────────────────────────────────────
if __name__ == "__main__":
    print("Resume Scorer Module — Ready!")
    print("Functions: calculate_score | calculate_ats_score | rank_candidates")
