from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from .pdf_extractor import PDFExtractor
import aiohttp
import tempfile
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

# MCP Server
server = Server("pdf_extraction")

# Initialize global FAISS index
faiss_index = None
stored_docs = []

# Set your OpenAI API key and base URL
node_env = os.getenv("NODE_ENV", "development")
os.environ["OPENAI_API_KEY"] = "sk-proj-1234567890"
os.environ["OPENAI_API_BASE"] = "http://localmodel:65534" if node_env == "production" else "http://localhost:65534"

# Utility function to build FAISS index with metadata and generate summaries
async def build_faiss_index(text: str, metadata: dict):
    global faiss_index, stored_docs
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(text)

    # Generate summary for the whole document
    summary = await generate_summary(text)

    # Include summary in metadata
    metadata["summary"] = summary

    stored_docs = [Document(page_content=t, metadata=metadata) for t in texts]
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.environ["OPENAI_API_KEY"],
        openai_api_base=os.environ["OPENAI_API_BASE"],
    )
    faiss_index = FAISS.from_documents(stored_docs, embeddings)

# Function to generate summary using OpenAI model
async def generate_summary(text: str) -> str:
    prompt = "Summarize the following document:\n\n{text}"
    template = PromptTemplate(input_variables=["text"], template=prompt)
    llm = OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"],
                openai_api_base=os.environ["OPENAI_API_BASE"], 
                model="gpt-4o")

    chain = LLMChain(llm=llm, prompt=template)
    summary = await chain.apredict(text=text)
    return summary

# Tools
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="extract-pdf-contents",
            description="Extract and index content from a local PDF. Provide page numbers as comma-separated string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string"},
                    "pages": {"type": "string"},
                },
                "required": ["pdf_path"],
            },
        ),
        types.Tool(
            name="extract-pdf-from-url",
            description="Download, extract, and index content from a PDF URL. Provide page numbers as comma-separated string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_url": {"type": "string"},
                    "pages": {"type": "string"},
                },
                "required": ["pdf_url"],
            },
        ),
        types.Tool(
            name="query-indexed-pdf",
            description="Query the previously indexed PDF and return relevant text chunks. Optionally, filter by file path or URL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "pdf_path": {"type": "string", "optional": True},
                    "pdf_url": {"type": "string", "optional": True},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="full-text-summary",
            description="Retrieve full text of a previously indexed PDF for summarization or other purposes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "optional": True},
                    "pdf_url": {"type": "string", "optional": True},
                },
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if not arguments:
        raise ValueError("Missing arguments")

    extractor = PDFExtractor()

    if name == "extract-pdf-contents":
        pdf_path = arguments.get("pdf_path")
        pages = arguments.get("pages")
        if not pdf_path:
            raise ValueError("Missing file path")

        text = extractor.extract_content(pdf_path, pages)
        metadata = {"pdf_path": pdf_path}
        await build_faiss_index(text, metadata)
        return [types.TextContent(type="text", text="PDF content indexed successfully. Summary included.")]

    elif name == "extract-pdf-from-url":
        pdf_url = arguments.get("pdf_url")
        pages = arguments.get("pages")
        if not pdf_url:
            raise ValueError("Missing PDF URL")

        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to download PDF: {response.status}")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(await response.read())
                    tmp_path = tmp_file.name

        try:
            text = extractor.extract_content(tmp_path, pages)
            metadata = {"pdf_url": pdf_url}
            await build_faiss_index(text, metadata)
        finally:
            os.remove(tmp_path)

        return [types.TextContent(type="text", text="Remote PDF content indexed successfully. Summary included.")]

    elif name == "query-indexed-pdf":
        query = arguments.get("query")
        pdf_path = arguments.get("pdf_path")
        pdf_url = arguments.get("pdf_url")
        
        if not query:
            raise ValueError("Missing query")
        if faiss_index is None:
            raise ValueError("No indexed PDF content available")

        # Filter by pdf_path or pdf_url if provided
        docs = faiss_index.similarity_search(query, k=5)
        if pdf_path:
            docs = [doc for doc in docs if doc.metadata.get("pdf_path") == pdf_path]
        if pdf_url:
            docs = [doc for doc in docs if doc.metadata.get("pdf_url") == pdf_url]
        
        return [types.TextContent(type="text", text="\n\n".join([doc.page_content for doc in docs]))]

    elif name == "full-text-summary":
        pdf_path = arguments.get("pdf_path")
        pdf_url = arguments.get("pdf_url")
        
        if pdf_path:
            docs = [doc for doc in stored_docs if doc.metadata.get("pdf_path") == pdf_path]
        elif pdf_url:
            docs = [doc for doc in stored_docs if doc.metadata.get("pdf_url") == pdf_url]
        else:
            raise ValueError("Either pdf_path or pdf_url must be provided.")

        # Return the summary from the metadata
        summaries = [doc.metadata.get("summary") for doc in docs if doc.metadata.get("summary")]
        return [types.TextContent(type="text", text="\n\n".join(summaries))]

    else:
        raise ValueError(f"Unknown tool: {name}")

# Run the server
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf_extraction",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
