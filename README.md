# 🚀 Smart AI Resume Analyzer with Blockchain Certification

An AI-powered Resume Analysis and Job Matching Platform integrated with Blockchain-based Certificate Verification to help candidates optimize resumes, improve ATS scores, and securely validate certifications.

---

## 📌 Project Overview

The Smart AI Resume Analyzer helps candidates evaluate their resumes using AI and machine learning techniques. It analyzes resume content, extracts skills, calculates ATS compatibility scores, identifies skill gaps, and recommends improvements.

To enhance trust and authenticity, the system also uses Blockchain Technology for issuing and verifying certificates through smart contracts.

This project combines:

- Artificial Intelligence
- Machine Learning
- Natural Language Processing (NLP)
- Blockchain Technology
- Web Development

---

## ✨ Key Features

### 🤖 AI Resume Analyzer

- Resume Parsing
- ATS Score Calculation
- Skill Extraction
- Resume Quality Analysis
- Resume Improvement Suggestions
- Candidate Ranking

### 🎯 Job Matching System

- Resume vs Job Description Matching
- Skill Gap Detection
- Job Recommendations
- Candidate Evaluation

### 👤 Profile Generator

- Professional Summary Generation
- Candidate Profile Creation
- Career Suggestions

### 🔐 Blockchain Certification

- Certificate Issuance
- Certificate Verification
- Smart Contract Integration
- Tamper-Proof Storage
- Fraud Prevention

### 👥 User Management

- User Registration
- Authentication
- Candidate Records Management

---

# 🏗️ System Architecture

```text
                    ┌─────────────────┐
                    │     Resume      │
                    │      Upload     │
                    └────────┬────────┘
                             │
                             ▼

                ┌──────────────────────────┐
                │   Resume Parsing Engine   │
                └──────────┬───────────────┘
                           │

          ┌────────────────┼────────────────┐
          ▼                ▼                ▼

 ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
 │ Skill Extract │ │ ATS Scoring   │ │ Job Matching  │
 └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼

                ┌──────────────────────┐
                │ Recommendation Engine│
                └──────────┬───────────┘
                           ▼

                ┌──────────────────────┐
                │  Candidate Dashboard │
                └──────────────────────┘


─────────────────────────────────────────────

          Blockchain Certificate Module

      Issue Certificate → Smart Contract
                              ↓
                   Blockchain Storage
                              ↓
                 Certificate Verification
```

---

# 🔄 ATS Resume Workflow

```text
Resume Upload
      ↓
Resume Parsing
      ↓
Skill Extraction
      ↓
Keyword Analysis
      ↓
ATS Score Calculation
      ↓
Gap Identification
      ↓
Recommendations Generated
```

---

# 🔗 Blockchain Workflow

```text
Admin Issues Certificate
            ↓
Certificate Hash Generated
            ↓
Stored on Blockchain
            ↓
Verification Request
            ↓
Hash Comparison
            ↓
Certificate Valid / Invalid
```

---

# 🛠️ Tech Stack

## Frontend

- Streamlit

## Backend

- Python

## Machine Learning

- Scikit-Learn
- Pandas
- NumPy

## NLP

- NLTK
- Regex Processing

## Blockchain

- Solidity
- Ethereum
- Web3.py

## Database

- JSON Storage

## Development Tools

- VS Code
- Git
- GitHub

---

# 📂 Project Structure

```text
Smart_resume_analyzer_with_Blockchain_certification/

│
├── resume_analyzer/
│   ├── resume_parser.py
│   ├── resume_scorer.py
│   ├── job_matcher.py
│   └── profile_generator.py
│
├── blockchain_certificate/
│   ├── contracts/
│   ├── scripts/
│   ├── tests/
│   └── configs/
│
├── resume_app.py
├── issue_certificate.py
├── verify_certificate.py
├── deploy_contract.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Sumeet2005/Smart_resume_analyzer_with_Blockchain_certification.git
```

### Move into Project

```bash
cd Smart_resume_analyzer_with_Blockchain_certification
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

### Install Requirements

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

```bash
streamlit run resume_app.py
```

---

## Screenshots

### Home Page

![Home](screenshots/home.png)

### Resume Analysis

![Resume Analysis](screenshots/resume_analysis.png)

### ATS Score

![ATS Score](screenshots/ats_score.png)

### Job Matching

![Job Matching](screenshots/job_matching.png)

### Certificate Verification

![Certificate Verification](screenshots/certificate_verification.png)


# 📈 Future Enhancements

- LLM-based Resume Review
- AI Interview Preparation Assistant
- LinkedIn Profile Analyzer
- Resume Builder
- PDF Report Generation
- Multi-Blockchain Support
- Recruiter Dashboard

---

# 💼 Resume Highlights

### Key Achievements

✔ Developed an AI-powered ATS Resume Analyzer

✔ Implemented Resume Parsing and Skill Extraction

✔ Built Job Matching Recommendation Engine

✔ Integrated Blockchain-based Certificate Verification

✔ Designed Smart Contracts using Solidity

✔ Developed End-to-End Web Application using Python and Streamlit

---

# 👨‍💻 Author

**Sumeet Sonar**

B.E. Information Technology

GitHub:
https://github.com/Sumeet2005

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
