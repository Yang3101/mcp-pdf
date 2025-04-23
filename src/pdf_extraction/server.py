from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from .pdf_extractor import PDFExtractor
import aiohttp
import tempfile
import os

# MCP 服务器配置
server = Server("pdf_extraction")

# MCP 工具配置
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    Tools for PDF contents extraction
    """
    return [
        types.Tool(
            name="extract-pdf-contents",
            description="Extract contents from a local PDF file, given page numbers separated in comma. Negative page index number supported.",
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
            description="Download a PDF from a URL and extract content from it. Accepts page numbers as comma-separated string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_url": {"type": "string"},
                    "pages": {"type": "string"},
                },
                "required": ["pdf_url"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Tools for PDF content extraction
    """
    if not arguments:
        raise ValueError("Missing arguments")

    extractor = PDFExtractor()

    if name == "extract-pdf-contents":
        pdf_path = arguments.get("pdf_path")
        pages = arguments.get("pages")
        if not pdf_path:
            raise ValueError("Missing file path")

        extracted_text = extractor.extract_content(pdf_path, pages)
        return [types.TextContent(type="text", text=extracted_text)]

    elif name == "extract-pdf-from-url":
        pdf_url = arguments.get("pdf_url")
        pages = arguments.get("pages")
        if not pdf_url:
            raise ValueError("Missing PDF URL")

        # Download PDF to a temporary file
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to download PDF: {response.status}")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(await response.read())
                    tmp_path = tmp_file.name

        try:
            extracted_text = extractor.extract_content(tmp_path, pages)
        finally:
            os.remove(tmp_path)  # Clean up the temporary file

        return [types.TextContent(type="text", text=extracted_text)]

    else:
        raise ValueError(f"Unknown tool: {name}")


# 启动主函数
async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf_extraction",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )