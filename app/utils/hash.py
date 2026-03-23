import hashlib

def normalize(text: str) -> str:
    return text.strip().lower() if text else ""

def generate_job_hash(job: dict) -> str:
    raw = f"{normalize(job.get('title'))}|{normalize(job.get('company'))}|{normalize(job.get('location'))}|{job.get('source')}"
    return hashlib.sha256(raw.encode()).hexdigest()