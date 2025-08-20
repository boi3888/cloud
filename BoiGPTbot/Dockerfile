# Dockerfile for Cloud Run (Python 3.11)
FROM python:3.11-slim

# Avoid prompts
ENV PYTHONUNBUFFERED=1         PIP_NO_CACHE_DIR=1         PORT=8080

WORKDIR /app

# Install deps
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Expose port (Cloud Run uses $PORT)
EXPOSE 8080

# Run webhook server (PTB run_webhook listens on 0.0.0.0:$PORT)
CMD ["python", "-u", "webhook.py"]
