# Small, non-root image for the SRE demo app.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Run as an unprivileged user.
RUN useradd --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8080

# One worker + threads: the Prometheus client keeps metrics in process memory,
# so a single worker keeps counters consistent. Scale with replicas instead.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:app"]
