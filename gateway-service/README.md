# Gateway Service

A gateway service that routes requests to the appropriate microservices (Feedback and Member services).

## API Documentation

The service provides OpenAPI/Swagger documentation in two formats:

1. **Interactive Swagger UI**
   - URL: `http://localhost:8000/docs`
   - Provides an interactive interface to explore and test all APIs
   - Includes detailed request/response schemas and examples

2. **OpenAPI JSON Specification**
   - URL: `http://localhost:8000/openapi.json`
   - Raw OpenAPI/Swagger JSON specification
   - Can be imported into tools like Postman:
     1. Open Postman
     2. Click "Import" button
     3. Choose "Raw text" or "Paste raw text"
     4. Paste the JSON content from the openapi.json URL
     5. Click "Import"

## Available Endpoints

### Authentication
- `POST /token` - Get authentication token

### Members
- `POST /members/` - Create new member
- `GET /members/` - Get all members
- `DELETE /members/{member_id}` - Soft delete a single member by ID

### Feedback
- `POST /feedback/` - Create new feedback
- `GET /feedback/` - Get all active feedbacks
- `DELETE /feedback/{feedback_id}` - Soft delete a single feedback by ID

## Running the Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file (example):
```
MEMBER_SERVICE_URL=http://localhost:8002
FEEDBACK_SERVICE_URL=http://localhost:8001
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Run the service:
```bash
uvicorn app.main:app --reload --port 8000
```

## Testing

### From the project root

Run all gateway unit and integration tests using the Makefile:
```bash
make test-gateway
```

This will ensure the correct PYTHONPATH is set for the `shared` module and all tests are discovered.

### Manually (from gateway-service directory)

If running manually, set the PYTHONPATH to include the project root:
```bash
PYTHONPATH=..:. python3 -m pytest tests/test_main.py tests/test_integration.py -v
```

---

- The test suite covers both unit and integration scenarios.
- Skipped tests for bulk deletion have been removed for safety and data integrity.
- Make sure the `shared` directory is present at the project root for all imports to work. 