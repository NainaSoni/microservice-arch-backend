# Organization Management Microservices

This project consists of three microservices for managing organization feedback and members, with a gateway service for unified API access.

## Architecture

The project consists of three main services:

1. **Feedback Service**
   - Manages organization feedback
   - Handles CRUD operations for feedback
   - Uses PostgreSQL database

2. **Member Service**
   - Manages organization members
   - Handles CRUD operations for members
   - Uses PostgreSQL database

3. **Gateway Service**
   - Entry point for all API requests
   - Routes requests to appropriate microservices
   - Provides Swagger documentation
   - Authentication for feedback and members routes 
   - Include unit tests and integration tests for services 


## OpenAPI JSON Specification
   - URL: `http://localhost:8000/openapi.json`
   - Raw OpenAPI/Swagger JSON specification
   - Can be imported into tools like Postman:
     1. Open Postman
     2. Click "Import" button
     3. Choose "Raw text" or "Paste raw text"
     4. Paste the JSON content from the openapi.json URL
     5. Click "Import"


## Prerequisites

- Docker
- Docker Compose
- Python 3.8+

## Setup Instructions

1. Clone the repository:
```bash
  https://github.com/NainaSoni/microservice-arch-backend.git
  cd microservice-arch-backend
```

2. Create a `.env` file in the root directory with the following variables:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=organization_db
FEEDBACK_SERVICE_PORT=8001
MEMBER_SERVICE_PORT=8002
GATEWAY_SERVICE_PORT=8000

# Service URLs
MEMBER_SERVICE_URL=http://localhost:8002
FEEDBACK_SERVICE_URL=http://localhost:8001

# Authentication settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Build and start the services:
```bash
docker-compose build --no-cache && docker-compose up
```

## API Documentation

Once the services are running, you can access the Swagger documentation at:
```
http://localhost:8000/docs
```

## API Endpoints

### Get Authentication token 
- `POST /token`
Try with any seeded member in DB:

```json
    {
      "username": "johndoe",
      "password": "testpassword123"
    }

### Feedback Endpoints

- `POST /api/feedback`
  - Create new feedback
  - Request Body:
    ```json
    {
      "feedback": "Great team culture, clear communication, and strong support for growth."
    }
    ```

- `GET /api/feedback`
  - Get all non-deleted feedbacks

- `DELETE /api/feedback/{feedback_id}`
  - Soft delete a single feedback by ID

- `DELETE /api/feedback`
  - Soft delete all feedbacks


### Member Endpoints

- `POST /api/members`
  - Create new member
  - Request Body:
    ```json
    {
      "first_name": "John",
      "last_name": "Doe",
      "login": "john123",
      "avatar_url": "https://example.com/avatar.jpg",
      "followers": 120,
      "following": 35,
      "title": "Senior Developer",
      "email": "john@example.com",
      "password": "testpassword123"
    }
    ```

- `GET /api/members`
  - Get all non-deleted members (sorted by followers descending)

- `DELETE /api/members/{member_id}`
  - Soft delete a single member by ID


- `DELETE /api/members`
  - Soft delete all members

## Testing

Run all gateway unit and integration tests using the Makefile:
```bash
make test-gateway
```

## Project Features
- **Authentication**: JWT-based authentication for secure access to endpoints.
- **Exception Handling**: Custom exception handling to manage errors gracefully.
- **Basic Logging**: Logs are generated for various operations to help with debugging and monitoring.
- **Test Cases**: Comprehensive unit and integration tests to ensure reliability and correctness.

## Project Structure

```
.
├── .env
├── docker-compose.yml
├── README.md
├── feedback-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── config.py
│   │   └── seed.py
├── member-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── config.py
│   │   └── seed.py
└── gateway-service/
    ├── Dockerfile
    ├── requirements.txt
    ├── app/
    │   ├── main.py
    │   ├── schemas.py
    │   └── config.py
    └── tests/
        ├── test_main.py
        └── test_integration.py
        │   │   └── seed.py
└── shared/
    ├── auth.py
    ├── error_handling.py
    └── validator.py


```

## Database Management

The project includes pgAdmin for database management. You can access it at:
```
http://localhost:5050
```

### pgAdmin Setup

1. Login to pgAdmin:
   - Email: `admin@admin.com`
   - Password: `admin`

2. Add Feedback Database Server:
   - Right-click on "Servers" → "Register" → "Server"
   - General tab:
     - Name: `Feedback DB`
   - Connection tab:
     - Host: `feedback-db`
     - Port: `5432`
     - Database: `feedback_db`
     - Username: `postgres` (or your POSTGRES_USER from .env)
     - Password: (your POSTGRES_PASSWORD from .env)

3. Add Member Database Server:
   - Right-click on "Servers" → "Register" → "Server"
   - General tab:
     - Name: `Member DB`
   - Connection tab:
     - Host: `member-db`
     - Port: `5432`
     - Database: `member_db`
     - Username: `postgres` (or your POSTGRES_USER from .env)
     - Password: (your POSTGRES_PASSWORD from .env)

### Viewing Data

1. Using pgAdmin UI:
   - Expand the server
   - Expand "Databases"
   - Expand your database
   - Expand "Schemas" → "public" → "Tables"
   - Right-click on any table (e.g., "members" or "feedbacks")
   - Select "View/Edit Data" → "All Rows"

2. Using Query Tool:
   - Click the "Query Tool" button (magnifying glass icon)
   - Write your SQL query, for example:
     ```sql
     -- View all active members
     SELECT * FROM members WHERE is_deleted = false;
     
     -- View all active feedbacks
     SELECT * FROM feedbacks WHERE is_deleted = false;
     ```
   - Click "Execute" (or press F5) 