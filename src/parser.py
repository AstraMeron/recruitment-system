import pdfplumber
import re
import spacy
import hashlib
import datetime
import json

# Load spaCy for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# Expanded Skill Map for Industrial/Technical Accuracy
SKILL_MAP = {
    "python": "Python", "sql": "SQL", "machine learning": "Machine Learning",
    "java": "Java", "c": "C", "javascript": "JavaScript", "html": "HTML", "css": "CSS",
    "labview": "LabView", "dasylab": "DasyLab", "iso 9001": "ISO 9001",
    "pneumatic": "Pneumatic Systems", "hydraulic": "Hydraulic Testing",
    "automation": "Automation", "robotics": "Robotics", "lean": "Lean Six Sigma"
}

def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except Exception:
        return None

def extract_name(lines):
    blacklist = ["profile", "experience", "summary", "objective", "engineer", 
                 "technician", "addis ababa", "ethiopia", "university", "page", "career", "focus"]
    
    for line in lines[:8]:
        clean = line.strip()
        if any(b in clean.lower() for b in blacklist) or len(clean.split()) > 4:
            continue
        
        doc = nlp(clean)
        has_person = any(ent.label_ == "PERSON" for ent in doc.ents)
        has_location = any(ent.label_ == "GPE" for ent in doc.ents)
        
        if has_person and not has_location:
            return clean
        if 2 <= len(clean.split()) <= 3 and clean.istitle():
            return clean
            
    return "Unknown Candidate"

def extract_education(lines):
    """Refined to capture degree and institution across multi-line blocks."""
    education = []
    inst_keywords = ["university", "college", "academy", "institute", "school"]
    degree_keywords = ["associates", "bachelor", "master", "phd", "diploma", "bsc", "msc", "science"]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Look for institution markers
        if any(kw in line_lower for kw in inst_keywords):
            # Context Window: Check current, previous, and next line for degree/year
            context_block = " ".join(lines[max(0, i-1):min(len(lines), i+2)])
            
            # Find Degree
            found_degree = "Certificate/Degree"
            for deg in degree_keywords:
                if deg in context_block.lower():
                    found_degree = deg.capitalize()
                    break
            
            # Find Year
            year_match = re.search(r"\b(19|20)\d{2}\b", context_block)
            
            education.append({
                "degree": found_degree,
                "institution": line.strip(),
                "year": year_match.group(0) if year_match else ""
            })
    return education

def extract_experience_list(text, lines):
    """Populates the specific role/company/years objects for the schema."""
    exp_list = []
    # Pattern to find date ranges
    date_pattern = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{2})?[\s/]?\d{4})\s*(?:to|-|–)\s*(Current|Present|(?:\d{2}[\s/])?\d{4})"
    
    for i, line in enumerate(lines):
        match = re.search(date_pattern, line, re.IGNORECASE)
        if match:
            # The role is usually on the same line or line before
            role = line.replace(match.group(0), "").strip()
            if not role and i > 0: role = lines[i-1]
            
            # Company is often the next line
            company = lines[i+1] if i+1 < len(lines) else "Unknown Company"
            
            # Calculate years for this specific role
            try:
                start_yr = int(re.search(r"\d{4}", match.group(1)).group())
                end_str = match.group(2).lower()
                end_yr = 2026 if "current" in end_str or "present" in end_str else int(re.search(r"\d{4}", end_str).group())
                
                exp_list.append({
                    "role": role if role else "Professional Experience",
                    "company": company.split(" - ")[0].strip(),
                    "years": max(1, end_yr - start_yr)
                })
            except:
                continue
    return exp_list

def calculate_total_years(exp_list):
    return sum(item["years"] for item in exp_list)

def parse_resume(raw_text, filename):
    if not raw_text: return None
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    
    # Extraction
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
    structured_exp = extract_experience_list(raw_text, lines)
    
    data = {
        "candidate_id": hashlib.md5(filename.encode()).hexdigest()[:8],
        "name": extract_name(lines),
        "email": email_match.group(0) if email_match else "",
        "skills": [val for key, val in SKILL_MAP.items() if re.search(rf'\b{re.escape(key)}\b', raw_text, re.IGNORECASE)],
        "education": extract_education(lines),
        "experience": structured_exp,
        "total_experience_years": calculate_total_years(structured_exp)
    }
            
    return data