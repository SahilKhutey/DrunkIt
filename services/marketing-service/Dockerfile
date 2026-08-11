FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install uv && apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY services/marketing-service/pyproject.toml ./
COPY services/_common /tmp/_common
RUN uv pip install --system /tmp/_common -e .

COPY services/marketing-service/app ./app
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8024/health || exit 1
EXPOSE 8024
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8024"]
