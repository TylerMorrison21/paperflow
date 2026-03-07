# PaperFlow MCP Server

**Let Claude actually understand academic PDFs — not just look at them.**

When you send a PDF directly to Claude, it uses vision to "read" page images.
This is slow, expensive, and breaks on:
- LaTeX equations (rendered as pixels, not parseable math)
- Multi-column layouts (reading order gets scrambled)
- Tables (structure lost, cells merged incorrectly)
- Citations and references (no linking, no context)

PaperFlow converts your PDF to clean, structured Markdown *before* Claude sees it.
Claude gets text instead of images — **~80% fewer tokens, significantly better analysis.**

## Quick Start

Choose the config for your OS and add it to `claude_desktop_config.json`.

Windows:
```json
{
  "mcpServers": {
    "paperflow": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "paperflow-mcp@0.1.5"]
    }
  }
}
```

Mac/Linux:
```json
{
  "mcpServers": {
    "paperflow": {
      "command": "npx",
      "args": ["-y", "paperflow-mcp@0.1.5"]
    }
  }
}
```

Restart Claude Desktop. That's it.

## How to Use

Just talk to Claude naturally:

- "Summarize this paper" + attach PDF
- "What methodology does this paper use?" + attach PDF
- "Compare the results in these two papers" + attach PDFs
- "Convert https://arxiv.org/pdf/2301.00001.pdf and extract the key findings"

Claude will automatically call PaperFlow to convert the PDF,
then analyze the structured Markdown. You never leave the conversation.

For very large PDFs, the MCP server now returns a preview plus `job_id` first,
then streams markdown in chunks via `get_markdown_chunk` to avoid Claude chat length errors.
For scanned/image-only PDFs, PaperFlow now auto-retries with OCR. If OCR still cannot extract usable text,
the tool returns a clear conversion failure instead of fabricated markdown.

If Claude Desktop truncates attachment bytes, `paperflow-mcp@0.1.5` now returns actionable recovery steps.
You can also bypass attachment transport by passing a local path in `source`, e.g.:
- `C:\Users\you\Desktop\paper.pdf`
- `file:///C:/Users/you/Desktop/paper.pdf`

## What happens when AI reads your PDF directly

| Content Type | Direct PDF (vision) | Via PaperFlow |
|---|---|---|
| **Equations** | Seen as images — can't reason or verify | Parsed as LaTeX — fully computable |
| **Multi-column** | Sentences from different columns interleaved | Correct reading order preserved |
| **Tables** | Numbers without structure | Markdown tables with rows and columns |
| **Citations [1,2]** | Plain text, no connection to references | Linked footnotes [^1][^2] with sources |
| **Token cost** | ~50k tokens/paper | ~20k tokens/paper |

## What Gets Preserved

- **LaTeX math**: `\alpha + \beta^2` → `$\alpha + \beta^2$`
- **Display equations**: Properly wrapped in `$$...$$` blocks
- **Tables**: Converted to GitHub-flavored Markdown pipe tables
- **Citations**: `[1, 2, 3]` → `[^1][^2][^3]` with full reference entries
- **Figure/table references**: Linked to captions
- **Document structure**: Title, authors, date in YAML frontmatter

## Limits

- Free trial: 15 pages per document, 3 documents/day, up to 100 total converted pages per email
- Need more? Email support@paperflowing.com and your `PAPERFLOW_EMAIL` can be added to Pro

## Verify Token Savings

Use the built-in benchmark kit to prove savings on your own workload:

```bash
cp benchmark/results.template.csv benchmark/results.csv
npm run bench:report
```

For full instructions, see `benchmark/README.md`.

## How It Works
