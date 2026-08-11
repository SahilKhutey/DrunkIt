FROM python:3.11-slim as builder

WORKDIR /app
RUN pip install --no-cache-dir hatchling uv

COPY services/_common /app/services/_common
RUN pip install --no-cache-dir -e /app/services/_common

COPY services/identity-service /app/services/identity-service
WORKDIR /app/services/identity-service
RUN pip install --no-cache-dir .

EXPOSE 8001
CMD ["uvicorn", "identity_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
