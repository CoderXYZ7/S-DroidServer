#!/bin/bash

# Default to port 3357 if not set
PORT=${PORT:-3357}

# Help function
function help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -p PORT   Set the port (default: 3357)"
    echo "  -h        Show this help message"
}

# Parse command-line options
while getopts "p:h:i" opt; do
    case $opt in
        p) PORT=$OPTARG;;
        h) help; exit 0;;
        ?) echo "Invalid option: -$OPTARG"; exit 1;;
    esac
done

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
