# MCP Savings Benchmark

Use this benchmark to test whether PaperFlow MCP actually saves money and keeps answer quality.

## Goal

Run paired tests on the same paper+prompt:
- `vision`: direct PDF usage
- `mcp`: PaperFlow conversion first, then answer on markdown

## CSV format

Create your own `benchmark/results.csv` by copying `benchmark/results.template.csv`.
Use the same columns and replace the placeholder rows with your real runs:

- `case_id`: shared id for a paired comparison (example: `p1_q1`)
- `mode`: `vision` or `mcp`
- `paper_id`: short paper label (example: `p1`)
- `pdf_url`: source pdf url
- `pages`: page count
- `prompt_id`: short prompt id (example: `q1`)
- `prompt`: exact prompt text (must be identical across pair)
- `input_tokens`: model input tokens for that run
- `output_tokens`: model output tokens for that run
- `latency_seconds`: end-to-end time
- `quality_score`: manual score 1-5 (same rubric for all runs)
- `success`: `true` or `false`
- `notes`: optional notes
- `timestamp`: ISO8601 timestamp

## Run report

From `mcp-server/`:

```bash
npm run bench:report
```

Or test with example data:

```bash
npm run bench:report:template
```

## Pass criteria

The report marks PASS only if all are true:

1. Median input token savings >= 50%
2. Median quality delta (MCP - Vision) >= 0
3. MCP failure rate <= 5%

## Recommended test size

- Minimum: 20 paired cases
- Better: 40 paired cases across mixed paper types (math-heavy, table-heavy, messy formatting)
