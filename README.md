# 📄 PDF Extraction & Indexing MCP Plugin

This is an MCP-compatible plugin for extracting text from PDFs, indexing content into a vector store (FAISS), and querying with natural language. Now includes automatic summarization of each indexed document.

## ✨ Features

- Extract text from local or remote (URL) PDFs.
- Automatically summarize the content during indexing.
- Store and query content via FAISS vector search using OpenAI embeddings.
- Retrieve relevant text chunks or full-document summaries.
- Optionally filter by file path or URL when querying.

## 🧰 Available Tools

### `extract-pdf-contents`

Extract and index content from a **local** PDF file.

- **Input**:
  ```json
  {
    "pdf_path": "path/to/file.pdf",
    "pages": "1,2,3" // Optional: comma-separated page numbers
  }
  ```
- **Output**: Confirmation message on successful indexing and summarization.

---

### `extract-pdf-from-url`

Download, extract, and index content from a **remote PDF**.

- **Input**:
  ```json
  {
    "pdf_url": "https://example.com/file.pdf",
    "pages": "1-3,5" // Optional
  }
  ```
- **Output**: Confirmation message on successful indexing and summarization.

---

### `query-indexed-pdf`

Query the indexed PDF content and return relevant text chunks.

- **Input**:
  ```json
  {
    "query": "What are the main findings?",
    "pdf_path": "path/to/file.pdf",   // Optional
    "pdf_url": "https://example.com/file.pdf" // Optional
  }
  ```
- **Output**: Up to 5 relevant chunks of text from the indexed document.

---

### `full-text-summary`

Return the **summary** generated for a previously indexed PDF.

- **Input**:
  ```json
  {
    "pdf_path": "path/to/file.pdf" // or
    "pdf_url": "https://example.com/file.pdf"
  }
  ```
- **Output**: Generated summary string from document metadata.

## 🚀 Quickstart

### 🛠️ Requirements

- Python 3.10+
- Dependencies: installed via Poetry (`poetry install`)
- OpenAI-compatible embedding server (set via `OPENAI_API_BASE`)
- Environment variables:
  - `OPENAI_API_KEY`: your OpenAI key or compatible local proxy key
  - `OPENAI_API_BASE`: `http://localhost:65534` (for dev), `http://localmodel:65534` (for production)

You can define these in a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-proj-1234567890
OPENAI_API_BASE=http://localhost:65534
NODE_ENV=development
```

---

### 🧪 Claude Desktop Setup

#### On macOS:
`~/Library/Application\ Support/Claude/claude_desktop_config.json`

#### On Windows:
`%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers</summary>

  ```json
  "mcpServers": {
    "pdf_extraction": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/xraywu/Workspace/pdf_extraction",
        "run",
        "pdf_extraction"
      ]
    }
  }
  ```
</details> 

<details> 
  <summary>Published Servers</summary>

  ```json
  "mcpServers": {
    "pdf_extraction": {
      "command": "uvx",
      "args": [
        "pdf_extraction"
      ]
    }
  }
  ```
</details>

---

## 🧠 Internals

This server uses:
- `langchain.embeddings.OpenAIEmbeddings` for embedding text
- `langchain.vectorstores.FAISS` for vector search
- `RecursiveCharacterTextSplitter` to prepare text chunks
- Async-based PDF fetching with `aiohttp`
- Temporary file handling with `tempfile` and `os`