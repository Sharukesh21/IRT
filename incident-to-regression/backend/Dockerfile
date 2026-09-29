# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install hatchling && pip install -e .
COPY app/ ./app/

# Stage 2: Runtime  
FROM python:3.12-slim AS runtime
WORKDIR /app
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/app ./app
COPY alembic/ ./alembic/
COPY alembic.ini ./
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
