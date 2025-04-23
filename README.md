# PDF Extraction MCP Server

MCP server to extract contents from a PDF file (local or via URL).

## Components

### Tools

The server implements the following tools:

#### 1. `extract-pdf-contents`
Extract contents from a **local PDF file**.
- **Arguments**:
  - `"pdf_path"` (required): Local file path of the PDF.
  - `"pages"` (optional): Comma-separated page numbers to extract (e.g. `"1,2,5"`). Supports negative indexing (e.g. `-1` means the last page).
- **Features**:
  - Direct PDF text extraction
  - OCR fallback for image-based pages

#### 2. `extract-pdf-from-url`
Download a **PDF from a URL** and extract contents.
- **Arguments**:
  - `"pdf_url"` (required): URL of the PDF file.
  - `"pages"` (optional): Comma-separated page numbers to extract. Supports negative indexing.
- **Features**:
  - Automatically downloads and processes PDF from the internet
  - Same text extraction capabilities as the local file tool

---

## Quickstart

### Install

#### Claude Desktop

##### On macOS:
`~/Library/Application\ Support/Claude/claude_desktop_config.json`

##### On Windows:
`%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>

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
  <summary>Published Servers Configuration</summary>
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