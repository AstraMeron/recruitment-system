from sentence_transformers import SentenceTransformer, util
import os
import json
import re
import sys

# Ensure local imports work
sys.path.append(os.path.dirname(__file__))
from parser import extract_text_from_pdf, parse_resume

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_jd_experience(jd_text):
    match = re.search(r'(\d+)\+?\s*(year|yr)', jd_text.lower())
    return int(match.group(1)) if match else 0

def rank_candidates(resumes_dir, job_description):
    results = []
    required_years = extract_jd_experience(job_description)
    jd_skills = ["python", "sql", "machine learning"] # Target skills for verification
    jd_emb = model.encode(job_description, convert_to_tensor=True)

    for filename in os.listdir(resumes_dir):
        if not filename.endswith(".pdf"): continue

        path = os.path.join(resumes_dir, filename)
        raw_text = extract_text_from_pdf(path)
        candidate = parse_resume(raw_text, filename)
        if not candidate: continue

        # --- Signal 1: Semantic Match (40%) ---
        profile = f"Candidate Skills: {', '.join(candidate['skills'])}. Experience: {candidate['total_experience_years']} years."
        res_emb = model.encode(profile, convert_to_tensor=True)
        semantic_score = float(util.cos_sim(res_emb, jd_emb))

        # --- Signal 2: Experience (20%) - Capped to prevent outliers ---
        cand_years = candidate["total_experience_years"]
        exp_score = min(cand_years / required_years, 1.2) if required_years > 0 else 0.5

        # --- Signal 3: Specific Skill Match (40%) ---
        skill_overlap = len([s for s in candidate["skills"] if s.lower() in jd_skills])
        skill_score = skill_overlap / len(jd_skills)

        # Apply Penalty for zero skill matches
        penalty = 1.0 if skill_score > 0 else 0.4

        # Final Weighted Formula
        final_score = penalty * (
            0.4 * semantic_score +
            0.2 * exp_score +
            0.4 * skill_score
        )

        # --- Inside the rank_candidates loop in src/ranker.py ---
        results.append({
            "candidate_id": candidate["candidate_id"],
            "name": candidate["name"],
            "email": candidate["email"],
            "skills": candidate["skills"],
            "education": candidate["education"],  # Add this line to include education in output
            "total_experience_years": cand_years,
            "score": round(final_score * 100, 2),
            "explanation": f"Semantic={round(semantic_score*100,1)}%, Exp={cand_years}/{required_years}, SkillMatch={skill_overlap}/3"
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)

if __name__ == "__main__":
    JD = "Looking for a Python developer with SQL and Machine Learning experience. 3+ years required."
    
    # Path setup
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RESUMES_PATH = os.path.join(BASE_DIR, "data", "resumes")

    rankings = rank_candidates(RESUMES_PATH, JD)
    print(json.dumps(rankings, indent=4))