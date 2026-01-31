import json
from ats_client import ATSClient

client = ATSClient()

def get_jobs(event, context):
    jobs = client.fetch_jobs()
    
    if isinstance(jobs, dict) and "error" in jobs:
        return {
            "statusCode": 500,
            "body": json.dumps(jobs)
        }
        
    return {
        "statusCode": 200,
        "body": json.dumps(jobs)
    }

def create_candidate(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}
        
    required = ['name', 'email', 'job_id']
    if not all(k in body for k in required):
        return {"statusCode": 400, "body": json.dumps({"error": f"Missing fields: {required}"})}
        
    result = client.create_candidate(body)
    
    if "error" in result:
        return {"statusCode": 500, "body": json.dumps(result)}
        
    return {
        "statusCode": 201,
        "body": json.dumps(result)
    }

def get_applications(event, context):
    params = event.get('queryStringParameters') or {}
    job_id = params.get('job_id')
    
    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "job_id query parameter is required"})}
        
    apps = client.fetch_applications(job_id)
    
    if isinstance(apps, dict) and "error" in apps:
        return {"statusCode": 500, "body": json.dumps(apps)}
        
    return {
        "statusCode": 200,
        "body": json.dumps(apps)
    }
