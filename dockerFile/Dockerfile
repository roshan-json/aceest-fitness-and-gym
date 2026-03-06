FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Install build dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy application source
COPY src/ /app/src/
WORKDIR /app/src

# Expose port and run with gunicorn for production
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
