# ── Stage 1: dependency installation ─────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies into an isolated prefix so the final image stays lean
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL org.opencontainers.image.title="demo-app"
LABEL org.opencontainers.image.description="Flask status page + MQTT random-value publisher"
LABEL org.opencontainers.image.authors="Stefan Klikovits"

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Run as non-root for improved container security
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser src/ src/

# ── Default environment variables ─────────────────────────────────────────────
# These are the lowest-priority defaults; override via -e flags or a .env file.
ENV DEMO_WEB_HOST=0.0.0.0       \
    DEMO_WEB_PORT=5000           \
    DEMO_COLOR=#2563eb           \
    DEMO_MQTT_HOST=localhost      \
    DEMO_MQTT_PORT=1883          \
    DEMO_MQTT_USER=""            \
    DEMO_MQTT_PASS=""            \
    DEMO_MQTT_TOPIC=demo/values  \
    DEMO_MQTT_INTERVAL=5

EXPOSE 5000

USER appuser

ENTRYPOINT ["python", "app.py"]
# All --flags can be appended after the image name, e.g.:
#   docker run demo-app --color "#16a34a" --mqtt-topic prod/sensors/temp
