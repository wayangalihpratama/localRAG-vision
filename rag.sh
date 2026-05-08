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
  "ollama")
    shift
    docker compose exec ollama ollama "$@"
    ;;
  "setup")
    echo "Setting up LocalRAG Vision..."
    docker compose up -d ollama
    echo "Waiting for Ollama to start..."
    sleep 5
    echo "Pulling models (Llama3, LLaVA)..."
    docker compose exec ollama ollama pull llama3
    docker compose exec ollama ollama pull llava
    docker compose up -d
    echo "Setup complete. Services running at http://localhost:3000 (UI) and http://localhost:8000 (API)"
    ;;
  *)
    echo "Usage: ./rag.sh {up|down|logs|backend|frontend|ollama|setup}"
    exit 1
    ;;
esac
