FROM python:3.8-slim

WORKDIR /app

COPY feedback-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn

COPY feedback-service/app ./app
COPY feedback-service/tests ./tests
COPY shared ./shared

ENV PYTHONPATH="/app:/app/shared:/app/.."

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"] 