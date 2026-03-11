#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DEFAULT_API_URL = 'http://localhost:8000';
const API_BASE_URL = normalizeApiBaseUrl(process.env.PAPERFLOW_API_URL || DEFAULT_API_URL);
const MCP_EMAIL = 'mcp@paperflow.local';
const USER_EMAIL = (process.env.PAPERFLOW_EMAIL || MCP_EMAIL).trim().toLowerCase();
const POLL_INTERVAL = 3_000;
const DEFAULT_TIMEOUT = 360_000;
const parsedTimeout = Number.parseInt(process.env.PAPERFLOW_TIMEOUT_MS || '', 10);
const TIMEOUT = Number.isFinite(parsedTimeout) && parsedTimeout > 0 ? parsedTimeout : DEFAULT_TIMEOUT;
const MAX_INLINE_CHARS = 18_000;
const PREVIEW_CHARS = 2_000;
const SUMMARY_PREVIEW_CHARS = 1_200;
const DEFAULT_CHUNK_SIZE = 12_000;
const MAX_CHUNK_SIZE = 18_000;
const MIN_CHUNK_SIZE = 500;
const TRUNCATED_PDF_HINT_BYTES = 20_000;
const STORE_TTL_MS = 30 * 60 * 1_000;
const MAX_STORE_ITEMS = 32;
const PARSER_CACHE_TTL_MS = 30_000;
const markdownStore = new Map();
let parserCatalogCache = {
  fetchedAt: 0,
  parsers: null,
};

const server = new Server(
  { name: 'paperflow-mcp', version: '0.3.1' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'convert_pdf',
      description:
        'Convert PDFs to structured Markdown through a self-hosted PaperFlow backend. ' +
        'Defaults to a token-efficient summary and auto-selects the best available parser.',
      inputSchema: {
        type: 'object',
        properties: {
          source: {
            type: 'string',
            description:
              'URL of the PDF (starting with http:// or https://) ' +
              'or base64-encoded PDF content, or an absolute local PDF file path ' +
              '(e.g. C:\\\\docs\\\\paper.pdf or file:///C:/docs/paper.pdf).',
          },
          filename: {
            type: 'string',
            description:
              'Optional display filename (e.g. "paper.pdf"). ' +
              'Defaults to "paper.pdf".',
          },
          parser: {
            type: 'string',
            description:
              'Optional parser choice. Use "auto" (default), "best", "local", "fast", ' +
              'or an explicit parser id such as "pymupdf", "marker_api", "marker_local", or "mineru".',
          },
          response_mode: {
            type: 'string',
            description:
              'Optional output mode: "summary" (default, saves chat tokens), "preview", or "full".',
          },
          inline_limit: {
            type: 'integer',
            description:
              'Optional max characters to inline in this tool response. ' +
              `Default ${MAX_INLINE_CHARS}.`,
          },
        },
        required: ['source'],
      },
    },
    {
      name: 'list_parsers',
      description:
        'List which PaperFlow parsers are currently configured on the connected backend, ' +
        'including the recommended default and quick setup notes.',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'get_markdown_chunk',
      description:
        'Fetch a chunk from a converted markdown document by job_id. ' +
        'Use this when the full conversion is too large for one chat message.',
      inputSchema: {
        type: 'object',
        properties: {
          job_id: {
            type: 'string',
            description: 'The job_id returned by convert_pdf.',
          },
          start: {
            type: 'integer',
            description: 'Start character offset (0-based). Default 0.',
          },
          length: {
            type: 'integer',
            description:
              `Number of characters to return. Default ${DEFAULT_CHUNK_SIZE}, ` +
              `max ${MAX_CHUNK_SIZE}.`,
          },
        },
        required: ['job_id'],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const args = request.params.arguments ?? {};

  if (request.params.name === 'convert_pdf') {
    return handleConvertPdf(args);
  }

  if (request.params.name === 'list_parsers') {
    return handleListParsers();
  }

  if (request.params.name === 'get_markdown_chunk') {
    return handleGetMarkdownChunk(args);
  }

  throw new Error(`Unknown tool: ${request.params.name}`);
});

async function handleConvertPdf(args) {
  const {
    source: rawSource,
    filename = 'paper.pdf',
    parser: rawParser,
    response_mode: rawResponseMode,
    inline_limit,
  } = args;

  if (typeof rawSource !== 'string' || !rawSource.trim()) {
    return text('Missing required input: source (PDF URL, absolute local PDF path, or base64 content).');
  }

  const inlineLimit = clampInt(inline_limit, MAX_INLINE_CHARS, 2_000, 100_000);
  const responseMode = normalizeResponseMode(rawResponseMode);
  const parserPreference = typeof rawParser === 'string' && rawParser.trim()
    ? rawParser.trim().toLowerCase()
    : 'auto';

  const source = rawSource.trim();
  const isUrl = source.startsWith('http://') || source.startsWith('https://');
  const isDataUri = source.startsWith('data:application/pdf;base64,');
  const localPath = normalizeLocalPdfPath(source);
  const isLocalPath = Boolean(localPath);

  let pdfBuffer;
  let likelyTruncatedInput = false;

  if (isUrl) {
    console.error(`[paperflow] Fetching PDF from URL: ${source}`);
    let res;
    try {
      res = await fetch(source);
    } catch (error) {
      return text(`Could not download PDF from ${source}. Check the URL and try again.`);
    }
    if (!res.ok) {
      return text(`Could not download PDF from ${source}. Check the URL and try again.`);
    }
    pdfBuffer = Buffer.from(await res.arrayBuffer());
  } else if (isLocalPath) {
    console.error(`[paperflow] Reading local PDF: ${localPath}`);
    try {
      pdfBuffer = await fs.readFile(localPath);
    } catch (error) {
      return text(`Could not read local PDF from ${localPath}. Check the path and try again.`);
    }
    if (!pdfBuffer.length) {
      return text(`Local PDF at ${localPath} is empty.`);
    }
  } else {
    console.error('[paperflow] Decoding base64 PDF');
    const base64Payload = isDataUri ? source.split(',', 2)[1] : source;
    if (!base64Payload) {
      return text('Invalid base64 PDF input.');
    }
    const normalizedBase64 = base64Payload.replace(/\s+/g, '');
    if (!looksLikeBase64(normalizedBase64)) {
      return text(
        [
          'PaperFlow could not decode the PDF bytes from this attachment.',
          'The payload appears malformed or truncated before reaching MCP.',
          '',
          'How to fix:',
          '1. Use a local file path in source (recommended): "C:\\\\path\\\\to\\\\file.pdf"',
          '2. Or provide a direct PDF URL in source.',
          '3. Or start a new chat, re-attach the file, and ask: "Use paperflow convert_pdf on this attachment now."',
        ].join('\n')
      );
    }
    pdfBuffer = Buffer.from(normalizedBase64, 'base64');
    if (!pdfBuffer.length) {
      return text('Invalid base64 PDF input.');
    }
    likelyTruncatedInput = pdfBuffer.length < TRUNCATED_PDF_HINT_BYTES;
  }

  console.error(`[paperflow] PDF size: ${pdfBuffer.length} bytes`);
  if (pdfBuffer.length < 4096) {
    console.error(`[paperflow] Warning: very small PDF payload (${pdfBuffer.length} bytes)`);
  }

  let selectedParser;
  try {
    selectedParser = await resolveParserSelection(parserPreference);
  } catch (error) {
    return text(error instanceof Error ? error.message : String(error));
  }

  console.error(`[paperflow] Submitting to backend: ${API_BASE_URL} parser=${selectedParser.id}`);
  let jobId;
  try {
    const form = new FormData();
    form.append('file', new Blob([pdfBuffer], { type: 'application/pdf' }), filename);
    form.append('email', USER_EMAIL);
    form.append('parser', selectedParser.id);

    const submitRes = await fetch(`${API_BASE_URL}/api/submit`, {
      method: 'POST',
      body: form,
    });

    if (submitRes.status === 429) {
      const data = await submitRes.json().catch(() => ({}));
      return text(
        data.detail ||
        'PaperFlow backend rejected the request with 429. Check your self-hosted limits and try again.'
      );
    }

    if (submitRes.status === 400) {
      const data = await submitRes.json().catch(() => ({}));
      return text(data.detail || 'Submission rejected by the PaperFlow backend (400).');
    }

    if (!submitRes.ok) {
      return text(backendUnavailableText());
    }

    const body = await submitRes.json();
    jobId = body.job_id;
    console.error(`[paperflow] Job submitted: ${jobId}`);
  } catch (error) {
    return text(backendUnavailableText());
  }

  console.error('[paperflow] Polling for result...');
  const deadline = Date.now() + TIMEOUT;

  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL);

    let statusRes;
    try {
      statusRes = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/status`);
    } catch (error) {
      return text(backendUnavailableText());
    }

    if (!statusRes.ok) {
      return text(backendUnavailableText());
    }

    const status = await statusRes.json().catch(() => ({}));
    console.error(`[paperflow] Status: ${status.status}`);

    if (status.status === 'failed') {
      const reason = typeof status.error === 'string' && status.error.trim()
        ? status.error.trim()
        : 'PaperFlow failed to convert this PDF.';
      const truncationAdvice = likelyTruncatedInput
        ? [
            '',
            `Possible cause: attachment bytes received by MCP were unusually small (${pdfBuffer.length} bytes).`,
            'Claude Desktop can sometimes truncate attachment payloads.',
            '',
            'Retry options:',
            '1. Use local file path in source (recommended): "C:\\\\path\\\\to\\\\file.pdf"',
            '2. Use a direct PDF URL in source.',
            '3. Start a new chat and re-attach before calling convert_pdf.',
          ].join('\n')
        : '';
      return text(
        [
          'PaperFlow conversion failed.',
          reason,
          truncationAdvice,
          '',
          'Do not fabricate markdown content when conversion fails.',
          'Ask the user for a clearer scan or a text-layer PDF.',
        ].join('\n')
      );
    }

    if (status.status === 'done') {
      break;
    }
  }

  if (Date.now() >= deadline) {
    return text(
      `PDF processing timed out after ${Math.round(TIMEOUT / 1000)} seconds. ` +
      'The file may be too complex. Try a shorter document.'
    );
  }

  console.error(`[paperflow] Fetching result for job ${jobId}`);
  let markdown;
  try {
    const resultRes = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/result`);
    if (!resultRes.ok) {
      return text(backendUnavailableText());
    }
    markdown = await resultRes.text();
  } catch (error) {
    return text(backendUnavailableText());
  }

  console.error('[paperflow] Result received, preparing output');

  const sourceLabel = isUrl ? source : isLocalPath ? localPath : filename;
  const resultUrl = `${API_BASE_URL}/api/jobs/${jobId}/result`;
  const packageUrl = `${API_BASE_URL}/api/jobs/${jobId}/package`;
  saveMarkdown(jobId, markdown, sourceLabel, {
    parserId: selectedParser.id,
    parserLabel: selectedParser.label,
    resultUrl,
    packageUrl,
  });

  let output;
  if (responseMode === 'full' && markdown.length <= inlineLimit) {
    output = [
      '---',
      `Source: ${sourceLabel}`,
      `Job ID: ${jobId}`,
      `Parser: ${selectedParser.label}`,
      `Backend: ${API_BASE_URL}`,
      'Converted by: PaperFlow',
      'Note: LaTeX formulas use $...$ and $$...$$ syntax. Citations are [^N] footnotes.',
      '---',
      '',
      markdown,
    ].join('\n');
  } else {
    output = buildCondensedOutput({
      jobId,
      sourceLabel,
      markdown,
      parserLabel: selectedParser.label,
      resultUrl,
      packageUrl,
      responseMode,
      inlineLimit,
    });
  }

  return text(output);
}

async function handleListParsers() {
  let parsers;
  try {
    parsers = await fetchParserCatalog({ forceRefresh: true });
  } catch (error) {
    return text(
      error instanceof Error
        ? error.message
        : `Could not list parsers from ${API_BASE_URL}.`
    );
  }

  const configured = parsers.filter((parser) => parser.configured);
  if (!configured.length) {
    return text(
      [
        `Backend: ${API_BASE_URL}`,
        'No parsers are configured on this PaperFlow backend.',
        '',
        'Recommended fixes:',
        '1. Install PyMuPDF locally for the easiest free path.',
        '2. Or add DATALAB_API_KEY for Marker API.',
        '3. Or install marker_single / mineru for self-hosted parsers.',
      ].join('\n')
    );
  }

  const lines = [
    `Backend: ${API_BASE_URL}`,
    'Configured PaperFlow parsers:',
    '',
  ];

  for (const parser of parsers) {
    lines.push(
      `- ${parser.label} [${parser.id}] - ${parser.configured ? 'configured' : 'not configured'}`
    );
    lines.push(`  Speed/quality: ${parser.speed} / ${parser.quality}`);
    lines.push(`  Setup: ${parser.setup}`);
    if (parser.default) {
      lines.push('  Default backend parser: yes');
    }
  }

  lines.push('');
  lines.push('MCP parser shortcuts:');
  lines.push('- auto: best available quality with minimal user setup');
  lines.push('- best: prefer marker_local -> marker_api -> mineru -> pymupdf');
  lines.push('- local: prefer marker_local -> pymupdf -> mineru');
  lines.push('- fast: prefer pymupdf -> marker_local -> mineru -> marker_api');

  return text(lines.join('\n'));
}

async function handleGetMarkdownChunk(args) {
  const { job_id: rawJobId, start, length } = args;

  if (typeof rawJobId !== 'string' || !rawJobId.trim()) {
    return text('Missing required input: job_id.');
  }

  const jobId = rawJobId.trim();
  const chunkStart = clampInt(start, 0, 0, Number.MAX_SAFE_INTEGER);
  const chunkSize = clampInt(length, DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE);

  const record = await getStoredMarkdown(jobId);
  if (!record) {
    return text(
      `No markdown found for job_id "${jobId}". ` +
      'Run convert_pdf first, then fetch chunks in the same Claude session.'
    );
  }

  const total = record.markdown.length;
  if (chunkStart >= total) {
    return text(
      `Start offset ${chunkStart} is past the end of markdown (${total} chars). ` +
      `Use a start value between 0 and ${Math.max(total - 1, 0)}.`
    );
  }

  const end = Math.min(chunkStart + chunkSize, total);
  const chunk = record.markdown.slice(chunkStart, end);
  const hasMore = end < total;

  const output = [
    '---',
    `Job ID: ${jobId}`,
    `Source: ${record.sourceLabel}`,
    record.parserLabel ? `Parser: ${record.parserLabel}` : null,
    `Range: ${chunkStart}-${end} / ${total} characters`,
    record.resultUrl ? `Direct markdown URL: ${record.resultUrl}` : null,
    record.packageUrl ? `Direct package URL: ${record.packageUrl}` : null,
    `Has more: ${hasMore ? 'yes' : 'no'}`,
    hasMore
      ? `Next call: {"job_id":"${jobId}","start":${end},"length":${chunkSize}}`
      : 'End of document reached.',
    '---',
    '',
    chunk,
  ].filter(Boolean).join('\n');

  return text(output);
}

function normalizeLocalPdfPath(input) {
  if (typeof input !== 'string') return null;
  const value = input.trim();
  if (!value) return null;

  if (value.startsWith('file://')) {
    try {
      return fileURLToPath(value);
    } catch (error) {
      return null;
    }
  }

  if (/^[a-zA-Z]:[\\/]/.test(value)) {
    return path.normalize(value);
  }

  if (value.startsWith('\\\\')) {
    return value;
  }

  if (value.startsWith('/')) {
    return value;
  }

  return null;
}

function normalizeApiBaseUrl(input) {
  const value = typeof input === 'string' ? input.trim() : '';
  if (!value) return DEFAULT_API_URL;
  return value.replace(/\/+$/, '');
}

function looksLikeBase64(value) {
  if (typeof value !== 'string' || !value) return false;
  if (value.length % 4 !== 0) return false;
  return /^[A-Za-z0-9+/]*={0,2}$/.test(value);
}

function backendUnavailableText() {
  return (
    `Could not connect to the PaperFlow backend at ${API_BASE_URL}. ` +
    'Check PAPERFLOW_API_URL and make sure your self-hosted backend is running. ' +
    'Typical local start: uvicorn api.main:app --port 8000'
  );
}

function text(str) {
  return { content: [{ type: 'text', text: str }] };
}

function clampInt(value, fallback, min, max) {
  const n = Number.isFinite(value) ? Math.floor(value) : Number.parseInt(value, 10);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, n));
}

function saveMarkdown(jobId, markdown, sourceLabel, meta = {}) {
  pruneStore();
  markdownStore.set(jobId, {
    markdown,
    sourceLabel,
    parserId: meta.parserId || '',
    parserLabel: meta.parserLabel || '',
    resultUrl: meta.resultUrl || '',
    packageUrl: meta.packageUrl || '',
    createdAt: Date.now(),
    lastAccess: Date.now(),
  });
  pruneStore();
}

async function getStoredMarkdown(jobId) {
  pruneStore();
  const cached = markdownStore.get(jobId);
  if (cached) {
    cached.lastAccess = Date.now();
    return cached;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/jobs/${jobId}/result`);
    if (!res.ok) return null;
    const markdown = await res.text();
    if (!markdown) return null;
    const record = {
      markdown,
      sourceLabel: '(from backend cache)',
      parserId: '',
      parserLabel: '',
      resultUrl: `${API_BASE_URL}/api/jobs/${jobId}/result`,
      packageUrl: `${API_BASE_URL}/api/jobs/${jobId}/package`,
      createdAt: Date.now(),
      lastAccess: Date.now(),
    };
    markdownStore.set(jobId, record);
    pruneStore();
    return record;
  } catch (error) {
    return null;
  }
}

function normalizeResponseMode(value) {
  const normalized = typeof value === 'string' ? value.trim().toLowerCase() : '';
  if (normalized === 'full' || normalized === 'preview') {
    return normalized;
  }
  return 'summary';
}

async function fetchParserCatalog({ forceRefresh = false } = {}) {
  const now = Date.now();
  if (!forceRefresh && parserCatalogCache.parsers && now - parserCatalogCache.fetchedAt < PARSER_CACHE_TTL_MS) {
    return parserCatalogCache.parsers;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/parsers`);
  } catch (error) {
    throw new Error(backendUnavailableText());
  }

  if (!response.ok) {
    throw new Error(backendUnavailableText());
  }

  const payload = await response.json().catch(() => ({}));
  const parsers = Array.isArray(payload.parsers) ? payload.parsers : [];
  parserCatalogCache = { fetchedAt: now, parsers };
  return parsers;
}

async function resolveParserSelection(preference) {
  const parsers = await fetchParserCatalog();
  const configured = parsers.filter((parser) => parser && parser.configured);

  if (!configured.length) {
    throw new Error(
      'No PaperFlow parsers are configured on the backend. Install PyMuPDF locally, ' +
      'or add DATALAB_API_KEY, or install marker_single / mineru.'
    );
  }

  const explicit = configured.find((parser) => parser.id === preference);
  if (explicit) {
    return explicit;
  }

  const knownButUnavailable = parsers.find((parser) => parser.id === preference);
  if (knownButUnavailable && !knownButUnavailable.configured) {
    throw new Error(
      `Parser "${preference}" is known but not configured on this backend. ${knownButUnavailable.setup}`
    );
  }

  if (preference && !['auto', 'best', 'local', 'fast'].includes(preference)) {
    const known = parsers.map((parser) => parser.id).join(', ');
    throw new Error(
      `Unknown parser "${preference}". Use auto, best, local, fast, or one of: ${known}.`
    );
  }

  const ranking = getParserRanking(preference || 'auto');
  for (const parserId of ranking) {
    const match = configured.find((parser) => parser.id === parserId);
    if (match) {
      return match;
    }
  }

  return configured[0];
}

function getParserRanking(preference) {
  if (preference === 'local') {
    return ['marker_local', 'pymupdf', 'mineru', 'marker_api'];
  }
  if (preference === 'fast') {
    return ['pymupdf', 'marker_local', 'mineru', 'marker_api'];
  }
  if (preference === 'best') {
    return ['marker_local', 'marker_api', 'mineru', 'pymupdf'];
  }
  return ['marker_local', 'marker_api', 'pymupdf', 'mineru'];
}

function buildCondensedOutput({
  jobId,
  sourceLabel,
  markdown,
  parserLabel,
  resultUrl,
  packageUrl,
  responseMode,
  inlineLimit,
}) {
  const previewChars = responseMode === 'preview' ? PREVIEW_CHARS : SUMMARY_PREVIEW_CHARS;
  const preview = markdown.slice(0, Math.min(previewChars, inlineLimit));
  const summary = summarizeMarkdown(markdown);
  const lines = [
    '---',
    `Source: ${sourceLabel}`,
    `Job ID: ${jobId}`,
    `Parser: ${parserLabel}`,
    `Markdown size: ${markdown.length} characters`,
    `Backend: ${API_BASE_URL}`,
    `Direct markdown URL: ${resultUrl}`,
    `Direct package URL: ${packageUrl}`,
    `Response mode: ${responseMode}`,
    'Converted by: PaperFlow',
    '---',
    '',
  ];

  if (summary.title) {
    lines.push(`Title: ${summary.title}`);
  }
  if (summary.authors.length) {
    lines.push(`Authors: ${summary.authors.join(', ')}`);
  }
  if (summary.date) {
    lines.push(`Date: ${summary.date}`);
  }
  if (summary.headings.length) {
    lines.push(`Top headings: ${summary.headings.join(' | ')}`);
  }

  lines.push('');
  if (responseMode === 'summary') {
    lines.push('Token-saving mode: returning a compact summary and short preview.');
  } else if (responseMode === 'preview') {
    lines.push('Preview mode: returning a larger preview without inlining the full markdown.');
  } else {
    lines.push('Requested full output was too large, so a preview is returned instead.');
  }
  lines.push(`Next chunk call: {"job_id":"${jobId}","start":0,"length":${DEFAULT_CHUNK_SIZE}}`);
  lines.push('');
  lines.push('Preview:');
  lines.push(preview);

  return lines.join('\n');
}

function summarizeMarkdown(markdown) {
  const frontmatter = extractFrontmatter(markdown);
  const title = frontmatter.title || extractFirstHeading(markdown);
  const authors = Array.isArray(frontmatter.authors)
    ? frontmatter.authors
    : frontmatter.authors
      ? [String(frontmatter.authors)]
      : [];
  const headings = extractTopHeadings(markdown);

  return {
    title,
    authors,
    date: frontmatter.date || '',
    headings,
  };
}

function extractFrontmatter(markdown) {
  if (!markdown.startsWith('---\n')) {
    return {};
  }

  const endIndex = markdown.indexOf('\n---\n', 4);
  if (endIndex === -1) {
    return {};
  }

  const block = markdown.slice(4, endIndex);
  const lines = block.split(/\r?\n/);
  const data = {};
  let currentKey = '';

  for (const line of lines) {
    const keyMatch = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (keyMatch) {
      const [, key, rawValue] = keyMatch;
      currentKey = key;
      const value = rawValue.trim().replace(/^['"]|['"]$/g, '');
      if (value) {
        data[key] = value;
      } else if (!data[key]) {
        data[key] = [];
      }
      continue;
    }

    const listMatch = line.match(/^\s*-\s+(.*)$/);
    if (listMatch && currentKey) {
      if (!Array.isArray(data[currentKey])) {
        data[currentKey] = [];
      }
      data[currentKey].push(listMatch[1].trim().replace(/^['"]|['"]$/g, ''));
    }
  }

  return data;
}

function extractFirstHeading(markdown) {
  const match = markdown.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : '';
}

function extractTopHeadings(markdown) {
  const headings = [];
  const regex = /^#{1,3}\s+(.+)$/gm;
  let match;

  while ((match = regex.exec(markdown)) && headings.length < 5) {
    const heading = match[1].trim();
    if (heading) {
      headings.push(heading);
    }
  }

  return headings;
}

function pruneStore() {
  const now = Date.now();
  for (const [jobId, record] of markdownStore.entries()) {
    if (now - record.createdAt > STORE_TTL_MS) {
      markdownStore.delete(jobId);
    }
  }

  if (markdownStore.size <= MAX_STORE_ITEMS) return;
  const entries = [...markdownStore.entries()]
    .sort((a, b) => a[1].lastAccess - b[1].lastAccess);

  for (const [jobId] of entries) {
    if (markdownStore.size <= MAX_STORE_ITEMS) break;
    markdownStore.delete(jobId);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[paperflow] MCP server started');
console.error(`[paperflow] API base URL: ${API_BASE_URL}`);
