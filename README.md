# ATS Integration Microservice (Python + Serverless)

This microservice provides a unified API for integrating with an Applicant Tracking System (ATS).

## Components

1.  **Mock ATS API (`mock-api/`)**: A standalone FastAPI service that simulates the Ashby ATS.
    - Runs on `http://127.0.0.1:8000`
    - API Key: `mock-key-12345`
2.  **Integration Microservice**: The Serverless service that provides the unified API.
    - Connects to the Mock ATS by default.

## Setup

### 1. Run the Mock ATS

Open a terminal, navigate to `mock-api/`, and run:
```bash
cd mock-api
pip install -r requirements.txt
uvicorn main:app --reload
```
This will start the mock service at `http://127.0.0.1:8000`.

### 2. Run the Integration Microservice

Open a **separate** terminal in the root directory:

1.  **Install dependencies** (Serverless v3 compatible):
    ```bash
    npm install --save-dev serverless@3 serverless-offline@13 serverless-python-requirements@6 --legacy-peer-deps
    ```
2.  **Environment Setup**:
    No `.env` is required for the mock demo; it defaults to the local Mock API.
3.  **Start the service**:
    ```bash
    npx serverless offline
    ```

## Example API Calls

### 1. Get Jobs
- **URL**: `http://localhost:3000/dev/jobs`
- **Method**: `GET`
- **Response**: List of available jobs from ATS.

### 2. Create Candidate
- **URL**: `http://localhost:3000/dev/candidates`
- **Method**: `POST`
- **Body (JSON)**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "123-456-7890",
    "resume_url": "https://example.com/resume.pdf",
    "job_id": "JOB_ID_HERE"
  }
  ```

### 3. List Applications
- **URL**: `http://localhost:3000/dev/applications`
- **Method**: `GET`
- **Query Params**: `job_id=JOB_ID_HERE`


## Error Handling

The service returns clean JSON errors for ATS failures:
```json
{
  "error": "Error message from ATS or validation"
}
```
