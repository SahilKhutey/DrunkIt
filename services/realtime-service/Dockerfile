FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install uv && apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY ../_common/pyproject.toml /tmp/_common/pyproject.toml
RUN uv pip install --system /tmp/_common -e .
COPY . .
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8012/health || exit 1
EXPOSE 8012
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8012"]
