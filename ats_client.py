import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ATSClient:
    def __init__(self):
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.dc = os.getenv('ZOHO_DC', 'in')  
        self.base_url = f"https://recruit.zoho.{self.dc}/recruit/v2"
        self.auth_url = f"https://accounts.zoho.{self.dc}/oauth/v2/token"
        
       
        self.access_token = self._get_access_token()
        self.headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _get_access_token(self):
        """
        Exchanges Refresh Token for a new Access Token.
        """
        if not self.refresh_token or not self.client_id:
             print("Missing Zoho Credentials")
             return "mock-token"

        params = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        try:
            response = requests.post(self.auth_url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'access_token' in data:
                return data['access_token']
            else:
                print(f"Failed to get access token: {data}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return None

    def fetch_jobs(self):
        """
        Fetches list of open jobs from Zoho Recruit Job_Openings.
        """
        url = f"{self.base_url}/Job_Openings"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get('data', []):
               
                jobs.append({
                    "id": job.get('id'),
                    "title": job.get('Posting_Title'),
                    "location": job.get('City', 'Remote'), 
                    "status": job.get('Job_Opening_Status'),
                    "external_url": job.get('Job_Opening_Name') 
                })
            return jobs
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return {"error": str(e)}

    def create_candidate(self, candidate_data):
        """
        Creates a candidate and associates them with a job.
        """
        candidates_url = f"{self.base_url}/Candidates"
        associate_url = f"{self.base_url}/Candidates/actions/associate"
        
        try:
            # 1. Create Candidate
            candidate_payload = {
                "data": [{
                    "First_Name": candidate_data.get('name').split(' ')[0] if candidate_data.get('name') else 'Unknown',
                    "Last_Name": " ".join(candidate_data.get('name', '').split(' ')[1:]) or "Candidate",
                    "Email": candidate_data.get('email'),
                    "Phone": candidate_data.get('phone'),
                    
                }]
            }
            
            res_candidate = requests.post(candidates_url, json=candidate_payload, headers=self.headers)
            res_candidate.raise_for_status()
            candidate_resp = res_candidate.json()
            
            if 'data' not in candidate_resp or not candidate_resp['data']:
                 return {"error": "Failed to create candidate", "details": candidate_resp}
                 
            candidate_id = candidate_resp['data'][0]['details']['id']
            
           
            if candidate_data.get('job_id'):
                assoc_url = f"{self.base_url}/Candidates/actions/associate"
              
                assoc_payload = {
                    "data": [{
                        "ids": [candidate_id],
                        "jobids": [candidate_data.get('job_id')],
                        "comments": "Associated via API"
                    }]
                }
                
                print(f"Associating candidate {candidate_id} to job {candidate_data.get('job_id')} via {assoc_url}")
                res_assoc = requests.put(assoc_url, json=assoc_payload, headers=self.headers)
                print(f"Association Response: {res_assoc.status_code} {res_assoc.text}")
                
                if res_assoc.status_code not in [200, 201]:
                     print(f"Failed to associate: {res_assoc.text}")
            
            return {"status": "success", "candidate_id": candidate_id}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def fetch_applications(self, job_id):
        """
        Fetches candidates associated with a given job (acting as applications).
        """
      
        url = f"{self.base_url}/Job_Openings/{job_id}/associate"
        
        print(f"Fetching applications from: {url}")
        try:
            response = requests.get(url, headers=self.headers)
            print(f"Response Status: {response.status_code}")
          
            if response.status_code == 204:
                return []
            
            if response.status_code != 200:
                 print(f"Error response: {response.text}")
                 return []

            data = response.json()
            
            apps = []
          
            for candidate in data.get('data', []):
                apps.append({
                    "id": candidate.get('id'),
                    "candidate_name": f"{candidate.get('First_Name')} {candidate.get('Last_Name')}",
                    "email": candidate.get('Email'),
                    "status": candidate.get('candidate_status_in_job') or candidate.get('Status') or "Applied" # Zoho might use different field names in association
                })
            return apps
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

