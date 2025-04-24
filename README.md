# PDF Extraction MCP Server

An MCP-compatible server to extract, index, and semantically search content from PDF files (local or from a URL) using **OpenAI embeddings** and **FAISS vector search**.

## Features

- Extracts and indexes PDF content (supports local files and remote URLs).
- Semantic search over extracted content using `text-embedding-ada-002`.
- OCR fallback for scanned/image-based PDFs (if implemented in `PDFExtractor`).
- Uses LangChain, FAISS, and OpenAI's embedding API.
- Fully compatible with Claude Desktop via MCP.

---

## 🔧 Tools

### 1. `extract-pdf-contents`

Extract and index contents from a **local PDF file**.

- **Arguments**:
  - `"pdf_path"` (required): Local path to the PDF file.
  - `"pages"` (optional): Comma-separated page numbers (e.g., `"1,2,5"`). Negative indexing supported (e.g., `-1` for the last page).
- **Features**:
  - Fast local PDF parsing
  - Semantic indexing for query support
  - OCR fallback (if supported by your `PDFExtractor`)

---

### 2. `extract-pdf-from-url`

Download, extract, and index contents from a **PDF URL**.

- **Arguments**:
  - `"pdf_url"` (required): URL pointing to a PDF file.
  - `"pages"` (optional): Comma-separated page numbers to extract. Negative indexing supported.
- **Features**:
  - Downloads and temporarily stores PDF
  - Supports same extraction/indexing pipeline as local tool

---

### 3. `query-indexed-pdf`

Query a previously indexed PDF with a semantic search prompt.

- **Arguments**:
  - `"query"` (required): Natural language query to retrieve relevant chunks.
- **Features**:
  - Uses FAISS + OpenAI embeddings to find semantically similar content
  - Returns top-5 matched chunks

---

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