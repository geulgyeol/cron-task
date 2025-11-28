FROM ghcr.io/astral-sh/uv:bookworm-slim

# Copy the project into the image
COPY . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "main.py"]