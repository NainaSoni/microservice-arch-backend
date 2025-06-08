# Feedback Service

A microservice for managing feedback operations.

## API Documentation

The service provides OpenAPI/Swagger documentation in two formats:

1. **Interactive Swagger UI**
   - URL: `http://localhost:8003/docs`
   - Provides an interactive interface to explore and test all APIs
   - Includes detailed request/response schemas and examples

2. **OpenAPI JSON Specification**
   - URL: `http://localhost:8003/openapi.json`
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

### Feedback
- `POST /feedback/` - Create new feedback
- `GET /feedback/` - Get all active feedbacks
- `DELETE /feedback/` - Soft delete all feedbacks
- `DELETE /feedback/{feedback_id}` - Soft delete a single feedback by ID

## Running the Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env` file:
```
DATABASE_URL=postgresql://postgres:postgres@feedback-db:5432/feedback_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Run the service:
```bash
uvicorn app.main:app --reload --port 8003
```

## Testing

Run tests using pytest:
```bash
pytest
``` 