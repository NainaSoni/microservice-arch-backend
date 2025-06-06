# Docker Compose commands for microservices

# Build all services without using cache
build:
	@echo "Building all services without cache..."
	docker compose build --no-cache

# Build a specific service without using cache
# Usage: make build-service SERVICE=service-name
build-service:
	@echo "Building $(SERVICE) without cache..."
	docker compose build --no-cache $(SERVICE)

# Start all services in detached mode
up:
	@echo "Starting all services in detached mode..."
	docker compose up -d

# Start a specific service in detached mode
# Usage: make up-service SERVICE=service-name
up-service:
	@echo "Starting $(SERVICE) in detached mode..."
	docker compose up -d $(SERVICE)

# Stop and remove all containers
down:
	@echo "Stopping and removing all containers..."
	docker compose down

# Stop and remove a specific service
# Usage: make down-service SERVICE=service-name
down-service:
	@echo "Stopping and removing $(SERVICE)..."
	docker compose stop $(SERVICE)
	docker compose rm -f $(SERVICE)

# Restart all services
restart:
	@echo "Restarting all services..."
	docker compose restart

# Restart a specific service
# Usage: make restart-service SERVICE=service-name
restart-service:
	@echo "Restarting $(SERVICE)..."
	docker compose restart $(SERVICE)

# View logs of all services
logs:
	@echo "Viewing logs of all services..."
	docker compose logs -f

# View logs of a specific service
# Usage: make logs-service SERVICE=service-name
logs-service:
	@echo "Viewing logs of $(SERVICE)..."
	docker compose logs -f $(SERVICE)

# Rebuild and restart all services
rebuild:
	@echo "Rebuilding and restarting all services..."
	make down
	make build
	make up

# Rebuild and restart a specific service
# Usage: make rebuild-service SERVICE=service-name
rebuild-service:
	@echo "Rebuilding and restarting $(SERVICE)..."
	make down-service SERVICE=$(SERVICE)
	make build-service SERVICE=$(SERVICE)
	make up-service SERVICE=$(SERVICE)

# Show status of all containers
ps:
	@echo "Showing status of all containers..."
	docker compose ps

# Show status of a specific service
# Usage: make ps-service SERVICE=service-name
ps-service:
	@echo "Showing status of $(SERVICE)..."
	docker compose ps $(SERVICE)

# Run tests in member service
test-member:
	@echo "Running tests in member service..."
	docker compose exec -e PYTHONPATH=/app member-service pytest tests/ -v

# Run tests in feedback service
test-feedback:
	@echo "Running tests in feedback service..."
	docker compose exec -e PYTHONPATH=/app feedback-service pytest tests/ -v

# Clean up all containers, images, and volumes
clean:
	@echo "Cleaning up all containers, images, and volumes..."
	docker compose down -v
	docker system prune -f

# Help command to show all available commands
help:
	@echo "Available commands:"
	@echo "  make build              - Build all services without cache"
	@echo "  make build-service      - Build a specific service without cache"
	@echo "  make up                 - Start all services in detached mode"
	@echo "  make up-service         - Start a specific service in detached mode"
	@echo "  make down               - Stop and remove all containers"
	@echo "  make down-service       - Stop and remove a specific service"
	@echo "  make restart            - Restart all services"
	@echo "  make restart-service    - Restart a specific service"
	@echo "  make logs               - View logs of all services"
	@echo "  make logs-service       - View logs of a specific service"
	@echo "  make rebuild            - Rebuild and restart all services"
	@echo "  make rebuild-service    - Rebuild and restart a specific service"
	@echo "  make ps                 - Show status of all containers"
	@echo "  make ps-service         - Show status of a specific service"
	@echo "  make test-member        - Run tests in member service"
	@echo "  make test-feedback      - Run tests in feedback service"
	@echo "  make clean              - Clean up all containers, images, and volumes"
	@echo "  make help               - Show this help message"

# Default target
.DEFAULT_GOAL := help 