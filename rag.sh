#!/bin/bash

# LocalRAG Vision Docker Wrapper

COMMAND=$1

case $COMMAND in
  "up")
    docker compose up --build
    ;;
  "down")
    docker compose down
    ;;
  "logs")
    docker compose logs -f
    ;;
  "backend")
    shift
    docker compose exec backend "$@"
    ;;
  "frontend")
    shift
    docker compose exec frontend "$@"
    ;;
  "setup")
    echo "Setting up LocalRAG Vision..."
    docker compose up -d
    echo "Setup complete. Services running at http://localhost:3000 (UI/API/Docs)"
    ;;
  *)
    echo "Usage: ./rag.sh {up|down|logs|backend|frontend|setup}"
    exit 1
    ;;
esac
