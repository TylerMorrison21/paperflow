# PaperFlow MCP Server

`paperflow-mcp` lets Claude Desktop send PDFs to a self-hosted PaperFlow backend and get back structured Markdown that is easier to reason over than raw PDF vision output.

## What Changed

`paperflow-mcp@0.3.1` is aligned with the new PaperFlow workflow:

- it targets your self-hosted PaperFlow backend
- it can discover which parsers are available on that backend
- it auto-selects the best available parser by default
- it returns a token-saving summary by default instead of dumping full markdown into chat

Default backend URL:

```text
http://localhost:8000
```

## Why Use It

When Claude reads PDFs directly with vision, it loses structure:

- LaTeX equations become pixels
- multi-column reading order breaks
- tables lose row and column structure
- citations become dead text

PaperFlow converts that output into structured Markdown first, then Claude can analyze a cleaner representation.

## Recommended Setup

```bash
git clone https://github.com/TylerMorrison21/paperflow
cd paperflow
cp .env.example .env
pip install -r requirements.txt
uvicorn api.main:app --port 8000
```

Then point the MCP server at that backend.

## Claude Desktop Config

Windows:

```json
{
  "mcpServers": {
    "paperflow": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "paperflow-mcp@0.3.1"],
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
      "args": ["-y", "paperflow-mcp@0.3.1"],
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
- `PAPERFLOW_MARKER_API_KEY`: optional Datalab.to API key for using `marker_api` through MCP

Restart Claude Desktop after updating the config.

## Install

```bash
npm install -g paperflow-mcp
```

## Best Parser Logic

The MCP server can choose a parser for the user instead of making them remember backend details.

Supported parser modes for `convert_pdf`:

- `auto` (default): prefer `marker_local`, then `marker_api`, then `paddleocr_vl`, then `pymupdf`
- `best`: prefer highest-quality output
- `local`: prefer local parsers first
- `fast`: prefer the fastest local path
- explicit parser id: `pymupdf`, `paddleocr_vl`, `marker_api`, `marker_local`

If you want MCP to use `marker_api`, set `PAPERFLOW_MARKER_API_KEY` in the MCP server environment so the backend receives your personal Datalab key.

Use `list_parsers` first if you want to see exactly what your backend has configured.

## Token-Saving Behavior

By default, `convert_pdf` returns `response_mode="summary"`:

- title / authors / top headings when available
- parser used
- markdown size
- direct backend URLs for markdown and package download
- a short preview

This keeps Claude context smaller while still giving you precise converted output.
Use `get_markdown_chunk` only when you need more of the document.

You can also request:

- `response_mode="preview"` for a longer preview
- `response_mode="full"` to inline the markdown when it is short enough

## Usage

Ask Claude normally:

- "Use PaperFlow to convert this PDF"
- "Use PaperFlow with the best parser on this paper"
- "Use PaperFlow in fast mode on this local PDF"
- "List my available PaperFlow parsers first"

You can also bypass attachment transport with:

- an absolute local path like `C:\Users\you\Desktop\paper.pdf`
- a `file:///` path
- a direct PDF URL

## Tools

### `convert_pdf`

Inputs:

- `source`: PDF URL, base64 PDF payload, or absolute local PDF path
- `filename`: optional display filename
- `parser`: optional parser choice or shortcut (`auto`, `best`, `local`, `fast`)
- `response_mode`: optional mode (`summary`, `preview`, `full`)
- `inline_limit`: optional max inline markdown size

### `list_parsers`

Returns:

- configured and non-configured backend parsers
- setup notes from the backend
- MCP parser shortcut guidance

### `get_markdown_chunk`

Use this when the markdown is too large for one chat response.

Inputs:

- `job_id`
- `start`
- `length`

## Behavior Notes

- `convert_pdf` now defaults to a compact summary to save chat tokens
- full markdown stays available through `get_markdown_chunk`
- the MCP server stores recent markdown in memory and can also refetch by `job_id`
- if attachment bytes are truncated by Claude Desktop, the tool returns recovery instructions
- if the backend is down, the tool tells the user how to start it locally

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
