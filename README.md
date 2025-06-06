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

## Prerequisites

- Docker
- Docker Compose
- Python 3.8+

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a `.env` file in the root directory with the following variables:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=organization_db
FEEDBACK_SERVICE_PORT=8001
MEMBER_SERVICE_PORT=8002
GATEWAY_SERVICE_PORT=8000
```

3. Build and start the services:
```bash
docker-compose up --build
```

## API Documentation

Once the services are running, you can access the Swagger documentation at:
```
http://localhost:8000/docs
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

## API Endpoints

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
      "email": "john@example.com"
    }
    ```

- `GET /api/members`
  - Get all non-deleted members (sorted by followers descending)

- `DELETE /api/members`
  - Soft delete all members

## Database Seeding

The services come with pre-seeded data for testing purposes. The seeding is automatically performed when the containers start up.

## Testing

To run tests for all services:

```bash
# Run tests for feedback service local
cd /Users/nainasoni/Documents/Workspace/microservice-arch-backend/feedback-service && python3 -m pytest tests/
# Run tests for feedback service on docker
docker compose exec -e PYTHONPATH=/app:/app/shared:/app/.. feedback-service pytest tests/ -v


# Run tests for member service local
cd /Users/nainasoni/Documents/Workspace/microservice-arch-backend/member-service && python3 -m pytest tests/
# Run tests for member service on docker
docker compose exec -e PYTHONPATH=/app:/app/shared:/app/.. member-service pytest tests/ -v
```

## Project Structure

```
.
├── docker-compose.yml
├── .env
├── feedback-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   └── tests/
├── member-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   └── tests/
└── gateway-service/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── __init__.py
        ├── main.py
        └── routes.py
``` 