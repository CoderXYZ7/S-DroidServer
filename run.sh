#!/bin/bash

# Default to port 3357 if not set
PORT=${PORT:-3357}

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn is not installed."
    exit 1
fi

# Optional: Activate virtualenv if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Launch FastAPI app
exec uvicorn main:app --reload --host 0.0.0.0 --port "$PORT"
