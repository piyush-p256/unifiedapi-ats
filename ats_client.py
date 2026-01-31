import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ATSClient:
    def __init__(self):
        self.api_key = os.getenv('ATS_API_KEY', 'mock-key-12345')
        self.base_url = os.getenv('ATS_BASE_URL', 'http://127.0.0.1:8000').strip('/')
        self.headers = {
            'Authorization': f'Basic {self.api_key}',
            'Content-Type': 'application/json'
        }

    def fetch_jobs(self):
        """
        Fetches list of open jobs from Ashby API.
        Ashby uses Basic Auth with API key as username and empty password.
        """
        url = f"{self.base_url}/jobBoard.listJobs"
        # Using the jobBoard API which is public-facing but good for this demo
        # For a full ATS integration, we might use /jobs endpoint with a proper API key
        payload = {"jobBoardName": "demo"} # Placeholder for real job board name
        
        try:
            # Ashby's jobBoard API is often a POST for listing
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get('results', []):
                jobs.append({
                    "id": job.get('id'),
                    "title": job.get('title'),
                    "location": job.get('location'),
                    "status": "OPEN", # Simplification for demo
                    "external_url": job.get('jobUrl')
                })
            return jobs
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return {"error": str(e)}

    def create_candidate(self, candidate_data):
        """
        Creates a candidate and applies them to a job.
        
        """
        candidate_url = f"{self.base_url}/candidate.create"
        application_url = f"{self.base_url}/application.create"
        
        try:
            # 1. Create Candidate
            candidate_payload = {
                "name": candidate_data.get('name'),
                "email": candidate_data.get('email'),
                "phoneNumber": candidate_data.get('phone'),
                "resumeUrl": candidate_data.get('resume_url')
            }
            res_candidate = requests.post(candidate_url, json=candidate_payload, headers=self.headers)
            res_candidate.raise_for_status()
            candidate = res_candidate.json()
            
            # 2. Apply to Job
            application_payload = {
                "candidateId": candidate.get('id'),
                "jobId": candidate_data.get('job_id')
            }
            res_app = requests.post(application_url, json=application_payload, headers=self.headers)
            res_app.raise_for_status()
            
            return {"status": "success", "candidate_id": candidate.get('id')}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def fetch_applications(self, job_id):
        """
        Fetches applications for a given job.
        """
        url = f"{self.base_url}/application.list"
        payload = {"jobId": job_id}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            apps = []
            for app in data.get('results', []):
                apps.append({
                    "id": app.get('id'),
                    "candidate_name": app.get('candidate', {}).get('name'),
                    "email": app.get('candidate', {}).get('email'),
                    "status": self._map_status(app.get('status'))
                })
            return apps
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _map_status(self, ats_status):
        status_map = {
            "Active": "APPLIED",
            "Screener": "SCREENING",
            "Archived": "REJECTED",
            "Hired": "HIRED"
        }
        return status_map.get(ats_status, "APPLIED")
