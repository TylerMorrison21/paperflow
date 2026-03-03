#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const BACKEND       = 'https://paperflow-production-daf5.up.railway.app';
const MCP_EMAIL     = 'mcp@paperflowing.com';
const POLL_INTERVAL = 3_000;    // ms between status polls
const TIMEOUT       = 120_000;  // ms before giving up

// ---------------------------------------------------------------------------
// Server setup
// ---------------------------------------------------------------------------
const server = new Server(
  { name: 'paperflow-mcp', version: '0.1.0' },
  { capabilities: { tools: {} } }
);

// ---------------------------------------------------------------------------
// Tool list
// ---------------------------------------------------------------------------
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'convert_pdf',
      description:
        'Convert academic PDFs to structured Markdown before feeding to Claude. ' +
        'Saves ~80% tokens vs sending raw PDF images. Preserves LaTeX equations ($...$, $$...$$), ' +
        'table structures, citation footnotes [^N], and cross-references that vision-based ' +
        'PDF reading destroys. Works with any PDF URL or attached file.',
      inputSchema: {
        type: 'object',
        properties: {
          source: {
            type: 'string',
            description:
              'URL of the PDF (starting with http:// or https://) ' +
              'or base64-encoded PDF content.',
          },
          filename: {
            type: 'string',
            description:
              'Optional display filename (e.g. "paper.pdf"). ' +
              'Defaults to "paper.pdf".',
          },
        },
        required: ['source'],
      },
    },
  ],
}));

// ---------------------------------------------------------------------------
// Tool execution
// ---------------------------------------------------------------------------
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== 'convert_pdf') {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const { source, filename = 'paper.pdf' } = request.params.arguments ?? {};
  const isUrl = source.startsWith('http://') || source.startsWith('https://');

  // -- 1. Resolve PDF bytes --------------------------------------------------
  let pdfBuffer;
  if (isUrl) {
    console.error(`[paperflow] Fetching PDF from URL: ${source}`);
    let res;
    try {
      res = await fetch(source);
    } catch (e) {
      return text(`Could not download PDF from ${source}. Check the URL and try again.`);
    }
    if (!res.ok) {
      return text(`Could not download PDF from ${source}. Check the URL and try again.`);
    }
    pdfBuffer = Buffer.from(await res.arrayBuffer());
  } else {
    console.error('[paperflow] Decoding base64 PDF');
    pdfBuffer = Buffer.from(source, 'base64');
  }

  console.error(`[paperflow] PDF size: ${pdfBuffer.length} bytes`);

  // -- 2. Submit to backend --------------------------------------------------
  console.error('[paperflow] Submitting to PaperFlow backend');
  let job_id;
  try {
    const form = new FormData();
    form.append(
      'file',
      new Blob([pdfBuffer], { type: 'application/pdf' }),
      filename
    );
    form.append('email', MCP_EMAIL);

    const submitRes = await fetch(`${BACKEND}/api/submit`, {
      method: 'POST',
      body: form,
    });

    if (submitRes.status === 429) {
      return text(
        'PaperFlow is at capacity. ' +
        'Free tier: 5 pages/doc, 3 docs/day. ' +
        'For higher limits: api@paperflowing.com'
      );
    }

    if (submitRes.status === 400) {
      const data = await submitRes.json().catch(() => ({}));
      return text(data.detail || 'Submission rejected by PaperFlow (400).');
    }

    if (!submitRes.ok) {
      return text('Could not connect to PaperFlow service. Try again in a moment.');
    }

    const body = await submitRes.json();
    job_id = body.job_id;
    console.error(`[paperflow] Job submitted: ${job_id}`);
  } catch (e) {
    return text('Could not connect to PaperFlow service. Try again in a moment.');
  }

  // -- 3. Poll for completion ------------------------------------------------
  console.error('[paperflow] Polling for result...');
  const deadline = Date.now() + TIMEOUT;

  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL);

    let statusRes;
    try {
      statusRes = await fetch(`${BACKEND}/api/jobs/${job_id}/status`);
    } catch (e) {
      return text('Could not connect to PaperFlow service. Try again in a moment.');
    }

    if (!statusRes.ok) {
      return text('Could not connect to PaperFlow service. Try again in a moment.');
    }

    const status = await statusRes.json().catch(() => ({}));
    console.error(`[paperflow] Status: ${status.status}`);

    if (status.status === 'done') break;
    // 'processing' → keep polling
  }

  if (Date.now() >= deadline) {
    return text(
      'PDF processing timed out after 120 seconds. ' +
      'The file may be too complex. Try a shorter document.'
    );
  }

  // -- 4. Fetch result -------------------------------------------------------
  console.error(`[paperflow] Fetching result for job ${job_id}`);
  let markdown;
  try {
    const resultRes = await fetch(`${BACKEND}/api/jobs/${job_id}/result`);
    if (!resultRes.ok) {
      return text('Could not connect to PaperFlow service. Try again in a moment.');
    }
    markdown = await resultRes.text();
  } catch (e) {
    return text('Could not connect to PaperFlow service. Try again in a moment.');
  }

  console.error('[paperflow] Result received, returning to Claude');

  // -- 5. Return with metadata header ----------------------------------------
  const sourceLabel = isUrl ? source : filename;
  const output = [
    '---',
    `Source: ${sourceLabel}`,
    'Converted by: PaperFlow (paperflowing.com)',
    'Note: LaTeX formulas use $...$ and $$...$$ syntax. Citations are [^N] footnotes.',
    '---',
    '',
    markdown,
  ].join('\n');

  return text(output);
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function text(str) {
  return { content: [{ type: 'text', text: str }] };
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[paperflow] MCP server started');
