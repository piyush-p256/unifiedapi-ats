from fastapi import FastAPI, Header, HTTPException, Body
from typing import List, Optional
import uuid

app = FastAPI(title="Mock ATS API")

# Simple "generated" API key for local testing
MOCK_API_KEY = "mock-key-12345"

# Mock Data
MOCK_JOBS = [
    {"id": "job_001", "title": "Software Engineer", "location": "Remote", "jobUrl": "http://localhost:5000/jobs/1"},
    {"id": "job_002", "title": "Product Manager", "location": "New York", "jobUrl": "http://localhost:5000/jobs/2"},
]

MOCK_APPLICATIONS = []

def verify_api_key(authorization: str = Header(...)):
    if authorization != f"Basic {MOCK_API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

@app.get("/")
def root():
    return {"message": "Mock ATS API is running", "api_key_to_use": MOCK_API_KEY}

@app.post("/jobBoard.listJobs")
def list_jobs(authorization: str = Header(...), payload: dict = Body(...)):
    # Simulating Ashby's jobBoard API structure
    if authorization != f"Basic {MOCK_API_KEY}":
         raise HTTPException(status_code=401, detail="Unauthorized")
    return {"results": MOCK_JOBS}

@app.post("/candidate.create")
def create_candidate(authorization: str = Header(...), payload: dict = Body(...)):
    if authorization != f"Basic {MOCK_API_KEY}":
         raise HTTPException(status_code=401, detail="Unauthorized")
    
    candidate_id = str(uuid.uuid4())
    return {
        "id": candidate_id,
        "name": payload.get("name"),
        "email": payload.get("email")
    }

@app.post("/application.create")
def create_application(authorization: str = Header(...), payload: dict = Body(...)):
    if authorization != f"Basic {MOCK_API_KEY}":
         raise HTTPException(status_code=401, detail="Unauthorized")
    
    app_id = str(uuid.uuid4())
    application = {
        "id": app_id,
        "candidateId": payload.get("candidateId"),
        "jobId": payload.get("jobId"),
        "status": "Active"
    }
    MOCK_APPLICATIONS.append(application)
    return application

@app.post("/application.list")
def list_applications(authorization: str = Header(...), payload: dict = Body(...)):
    if authorization != f"Basic {MOCK_API_KEY}":
         raise HTTPException(status_code=401, detail="Unauthorized")
    
    job_id = payload.get("jobId")
    results = [a for a in MOCK_APPLICATIONS if a["jobId"] == job_id]
    
    # Enrich with candidate info for the integration service
    enriched_results = []
    for app in results:
        enriched_results.append({
            "id": app["id"],
            "status": app["status"],
            "candidate": {"name": "Test Candidate", "email": "test@example.com"}
        })
        
    return {"results": enriched_results}
