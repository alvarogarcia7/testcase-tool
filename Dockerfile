# Use a slim Python image and add common build tools
FROM python:3.14-slim

ARG APP_USER=user
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH=/home/$APP_USER/.local/bin:$PATH

# Install system deps and cleanup to keep image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl build-essential make git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y --no-install-recommends make

# Create app user and workdir
RUN useradd --create-home --shell /bin/bash $APP_USER
WORKDIR /app
RUN chown -R $APP_USER:$APP_USER /home/$APP_USER
RUN chown -R $APP_USER:$APP_USER /app
USER $APP_USER

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy Python dependency manifest and install if present
COPY --chown=$APP_USER:$APP_USER pyproject.toml ./

RUN uv sync

COPY --chown=$APP_USER:$APP_USER *.py ./

# Copy rest of the project
COPY --chown=$APP_USER:$APP_USER . /

# Default command is a lightweight no-op so the container stays up and you can override the command
CMD ["bash", "-c", "tail -f /dev/null"]
