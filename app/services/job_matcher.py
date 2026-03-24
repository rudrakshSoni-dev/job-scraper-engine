# app/services/job_matcher.py

def compute_match_score(job, skills):
    text = f"{job['title']} {job['company']}".lower()

    matched = [s for s in skills if s in text]

    # weighted score
    score = len(matched)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": list(set(skills) - set(matched))
    }


def rank_jobs(jobs, skills):
    results = []

    for job in jobs:
        match = compute_match_score(job, skills)

        results.append({
            **job,
            "match_score": match["score"],
            "matched_skills": match["matched_skills"],
            "missing_skills": match["missing_skills"]
        })

    return sorted(results, key=lambda x: x["match_score"], reverse=True)