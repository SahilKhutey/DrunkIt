FROM python:3.12-slim

WORKDIR /app

# psycopg2 needs libpq at build time; python3-dev+gcc cover any package
# that needs to compile. Kept minimal and removed from the final layer
# isn't attempted here — this is a straightforward single-stage build,
# appropriate for an MVP; revisit multi-stage/slimming before this
# matters for image size or attack surface.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Runs migrations before starting the app, so a fresh container always
# comes up against an up-to-date schema. AUTO_CREATE_TABLES should be
# left "false" (the image's default via docker-compose.yml) since this
# CMD is now the authoritative migration path.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
