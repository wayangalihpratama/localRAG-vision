# Feature Specification: Document Ingestion & Retrieval Pipeline 🚀

**Author**: John (Product Manager)
**Status**: Draft (Pending Approval)
**Date**: 2026-05-08

## 1. Summary
The Document Ingestion & Retrieval Pipeline is the core engine of LocalRAG Vision. It transforms raw, unstructured multi-format documents (PDF, DOCX, TXT) into a high-fidelity, searchable knowledge base. By utilizing **Docling**, we ensure that structural elements like tables, headers, and hierarchy are preserved, which is essential for accurate downstream reasoning.

## 2. User Stories
- **US.1**: As a researcher, I want to upload complex PDFs with tables so that I can query specific data points within those tables accurately.
- **US.2**: As a security officer, I want to search through my documents using both keywords (e.g., specific serial numbers) and semantic meaning (e.g., "power failure incidents") so that I don't miss critical information.
- **US.3**: As a developer, I want my document ingestion to happen in the background so that the UI remains responsive even when processing large files.

## 3. Functional Requirements (FR)

| ID | Feature | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR.1** | Multi-format Upload | API endpoint to accept PDF, DOCX, and TXT files. | Must |
| **FR.2** | Structural Extraction | Use **Docling** to convert documents into structured Markdown/JSON. | Must |
| **FR.3** | Async Processing | Offload document parsing and embedding to **Celery + Redis** workers. | Must |
| **FR.4** | Hybrid Search | Implement **LanceDB** with both Vector (Semantic) and BM25 (Keyword) indexing. | Must |
| **FR.5** | Chunking Strategy | Implement **Parent-Document Retrieval** (small chunks for search, larger context for LLM). | Should |
| **FR.6** | Progress Tracking | API to query the ingestion status (Pending, Processing, Completed, Failed). | Must |

## 4. Technical Specifications

### 4.1. Ingestion Workflow
1. **Upload**: File is saved to **MinIO** (S3 Storage).
2. **Task Queue**: Ingestion task is pushed to **Redis**.
3. **Structural Extraction**: Celery worker pulls the file and runs **Docling** to generate a `DoclingDocument`.
4. **Structural Chunking**: Use Docling's hierarchy tree to split text into "Semantic Blocks" (e.g., specific sections or full tables).
5. **Embedding**: Blocks are embedded using a local model (via Ollama).
6. **Indexing**: Chunks and vectors are stored in **LanceDB** with a Full-Text Search (FTS) index enabled.

### 4.2. Search Workflow
1. **Query**: User submits a natural language query.
2. **Dual-Retrieval**:
   - **Vector Search**: Semantic lookup for conceptual matches.
   - **FTS Search (BM25)**: Lexical lookup for exact matches (IDs, serial numbers).
3. **RRF Fusion**: Merge results using Reciprocal Rank Fusion (RRF) to produce a unified relevance score.
4. **Context Assembly**: Retrieved blocks are formatted with citations for the LLM.

## 5. UI/UX Requirements
- **Upload Dashboard**: Drag-and-drop zone with progress bars for each file.
- **Search Interface**: Real-time results showing snippets of matching documents.
- **Citations**: Clickable references in the LLM response that link back to the source snippet.

## 6. Security & Constraints
- **100% Local**: No data can leave the Docker network.
- **Resource Management**: Limit worker concurrency to prevent GPU/CPU exhaustion during heavy ingestion.

## 7. Acceptance Criteria (AC)
- [ ] Successful extraction of a 5-page PDF with at least 2 tables using Docling.
- [ ] Search results return the correct document when querying a unique serial number found in the text.
- [ ] Background workers successfully process documents without blocking the main API thread.
- [ ] LanceDB persistent storage survives container restarts.
