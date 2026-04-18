# Multi-stage Dockerfile
# - builder: creates a virtualenv and installs requirements
# - test: runs pytest inside the environment (docker build --target test will run tests)
# - runtime: minimal runtime image with installed venv copied from builder

FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv

RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
	&& pip install --no-cache-dir -r /app/requirements.txt

# Copy source into builder so tests can import the package
COPY src/ /app/src/

FROM builder AS test
WORKDIR /app/src
# Run the test suite during the image build for the 'test' target
RUN pytest -q

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv

# Copy virtualenv from builder
COPY --from=builder $VENV_PATH $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

WORKDIR /app/src
COPY src/ /app/src/

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
