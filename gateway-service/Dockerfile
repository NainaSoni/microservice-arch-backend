FROM python:3.8-slim

WORKDIR /app

# # Set PYTHONPATH to include the current directory
# ENV PYTHONPATH=/app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt && pip install uvicorn

# COPY . .

# # CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 


COPY gateway-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn

# Copy the shared directory
COPY shared ./shared

# Copy the service files
COPY gateway-service/app ./app

ENV PYTHONPATH="/app:/app/shared:/app/.."

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 