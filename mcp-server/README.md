# PaperFlow MCP Server

`paperflow-mcp` lets Claude Desktop send PDFs to a self-hosted PaperFlow-compatible backend.

## Breaking Change

`paperflow-mcp@0.2.1` no longer targets the old hosted backend.

You must provide your own backend URL through `PAPERFLOW_API_URL`.
If you do nothing, the MCP server assumes your backend is running at:

```text
http://localhost:8000
```

## What It Does

When Claude reads PDFs directly with vision, it loses structure:

- LaTeX equations become pixels
- multi-column reading order breaks
- tables lose row and column structure
- citations become dead text

PaperFlow converts that output into structured Markdown before Claude analyzes it.

## Self-Host the Backend

Example:

```bash
git clone https://github.com/TylerMorrison21/paperflow
cd paperflow
cp .env.example .env
# Add your parser credentials or swap in a local parser
uvicorn api.main:app --port 8000
```

## Claude Desktop Config

Windows:

```json
{
  "mcpServers": {
    "paperflow": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "paperflow-mcp@0.2.1"],
      "env": {
        "PAPERFLOW_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

macOS / Linux:

```json
{
  "mcpServers": {
    "paperflow": {
      "command": "npx",
      "args": ["-y", "paperflow-mcp@0.2.1"],
      "env": {
        "PAPERFLOW_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

Optional environment variables:

- `PAPERFLOW_API_URL`: backend base URL, default `http://localhost:8000`
- `PAPERFLOW_EMAIL`: email value sent to the backend, default `mcp@paperflow.local`
- `PAPERFLOW_TIMEOUT_MS`: conversion timeout in milliseconds

Restart Claude Desktop after updating the config.

## Install

```bash
npm install -g paperflow-mcp
```

## Usage

Ask Claude normally:

- "Summarize this paper" and attach a PDF
- "Compare these two papers" and attach both PDFs
- "Convert https://arxiv.org/pdf/2301.00001.pdf and extract key findings"

You can also bypass attachment transport with:

- an absolute local path like `C:\Users\you\Desktop\paper.pdf`
- a `file:///` path
- a direct PDF URL

## Tools

### `convert_pdf`

Inputs:

- `source`: PDF URL, base64 PDF payload, or absolute local PDF path
- `filename`: optional display filename
- `inline_limit`: optional max inline markdown size

### `get_markdown_chunk`

Use this when the markdown is too large for one chat response.

Inputs:

- `job_id`
- `start`
- `length`

## Behavior Notes

- Large conversions return a preview plus `job_id`
- `get_markdown_chunk` can fetch the rest incrementally
- If attachment bytes are truncated by Claude Desktop, the tool returns recovery instructions
- If the MCP process restarts, it can refetch markdown from your backend by `job_id`

## Local Development

```bash
cd mcp-server
npm install
npm start
```

## Benchmark

```bash
cp benchmark/results.template.csv benchmark/results.csv
npm run bench:report
```
