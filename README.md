# LocalRAG Vision

**LocalRAG Vision** is a local-first, multimodal Document Intelligence platform designed for absolute data sovereignty. It allows organizations to interact with sensitive text, image, audio, and video data using generative AI without ever leaving their secure local perimeter.

## 🚀 Key Features
- **Multimodal RAG**: Seamlessly query across PDF, Images, Audio, and Video.
- **Privacy First**: 100% Local processing; air-gapped capable.
- **Precision Indexing**: Powered by Docling, ImageBind, and Late Chunking.
- **Verifiable Citations**: Temporal and visual seeking for complete attribution.

## 📂 Documentation
- [Product Requirements Document (PRD)](docs/PRD.md)
- [Low-Level Design (LLD)](docs/LLD.md)
- [Docker Command Standard](.agent/rules/docker-commands.md)

## 🛠 Tech Stack
- **Engine**: Ollama (Llama 3, LLaVA)
- **Orchestration**: LangChain / LlamaIndex
- **Vector DB**: LanceDB, ChromaDB
- **UI**: Vercel AI SDK, shadcn/ui

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- NVIDIA Container Toolkit (for GPU acceleration)

### Setup & Run
1. **Initial Setup** (Pull models & build):
   ```bash
   ./rag.sh setup
   ```
2. **Start Services**:
   ```bash
   ./rag.sh up
   ```
3. **Access**:
   - Web UI (Direct): `http://localhost:3000`
   - Application (Proxy): `http://localhost`
   - API Docs: `http://localhost/docs` or `http://localhost:8000/docs`

---
*Built with Antigravity BMAD Framework.*
