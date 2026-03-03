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

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "paperflow": {
      "command": "npx",
      "args": ["-y", "paperflow-mcp"]
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

## Why Not Just Send PDFs Directly to Claude?

| | Direct PDF (vision) | With PaperFlow MCP |
|---|---|---|
| **Token cost** | ~$0.15-0.40 per paper | ~$0.02-0.05 per paper |
| **LaTeX equations** | Broken / garbled | Perfect `$...$` and `$$...$$` |
| **Multi-column** | Scrambled reading order | Correct paragraph flow |
| **Tables** | Cells merged, structure lost | Clean Markdown tables |
| **Citations** | Plain text [1] | Linked footnotes [^1] with full references |
| **Speed** | Slow (vision processing) | Fast (text processing) |

## What Gets Preserved

- **LaTeX math**: `\alpha + \beta^2` → `$\alpha + \beta^2$`
- **Display equations**: Properly wrapped in `$$...$$` blocks
- **Tables**: Converted to GitHub-flavored Markdown pipe tables
- **Citations**: `[1, 2, 3]` → `[^1][^2][^3]` with full reference entries
- **Figure/table references**: Linked to captions
- **Document structure**: Title, authors, date in YAML frontmatter

## Limits

- Free: 5 pages per document, 3 documents per day
- Need more? API & batch processing available: support@paperflowing.com

## How It Works
