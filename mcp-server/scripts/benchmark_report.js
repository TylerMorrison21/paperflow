#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    const next = text[i + 1];

    if (inQuotes) {
      if (ch === '"' && next === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        cell += ch;
      }
      continue;
    }

    if (ch === '"') {
      inQuotes = true;
      continue;
    }

    if (ch === ",") {
      row.push(cell);
      cell = "";
      continue;
    }

    if (ch === "\n") {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
      continue;
    }

    if (ch === "\r") {
      continue;
    }

    cell += ch;
  }

  if (cell.length > 0 || row.length > 0) {
    row.push(cell);
    rows.push(row);
  }

  if (!rows.length) return [];

  const headers = rows[0].map((h) => h.trim());
  return rows
    .slice(1)
    .filter((r) => r.some((c) => c.trim().length > 0))
    .map((r, idx) => {
      const obj = {};
      headers.forEach((h, i) => {
        obj[h] = (r[i] ?? "").trim();
      });
      obj.__row = idx + 2;
      return obj;
    });
}

function toNumber(v) {
  if (v === undefined || v === null || v === "") return NaN;
  const n = Number(v);
  return Number.isFinite(n) ? n : NaN;
}

function median(values) {
  if (!values.length) return NaN;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) return (sorted[mid - 1] + sorted[mid]) / 2;
  return sorted[mid];
}

function pct(n) {
  if (!Number.isFinite(n)) return "n/a";
  return `${(n * 100).toFixed(1)}%`;
}

function num(n, digits = 1) {
  if (!Number.isFinite(n)) return "n/a";
  return n.toFixed(digits);
}

function pickStats(rows) {
  const inTok = rows.map((r) => toNumber(r.input_tokens)).filter(Number.isFinite);
  const outTok = rows.map((r) => toNumber(r.output_tokens)).filter(Number.isFinite);
  const totalTok = rows
    .map((r) => toNumber(r.input_tokens) + toNumber(r.output_tokens))
    .filter(Number.isFinite);
  const latency = rows.map((r) => toNumber(r.latency_seconds)).filter(Number.isFinite);
  const quality = rows.map((r) => toNumber(r.quality_score)).filter(Number.isFinite);
  const successCount = rows.filter((r) => String(r.success).toLowerCase() === "true").length;

  return {
    count: rows.length,
    successRate: rows.length ? successCount / rows.length : NaN,
    medianInput: median(inTok),
    medianOutput: median(outTok),
    medianTotal: median(totalTok),
    medianLatency: median(latency),
    medianQuality: median(quality),
  };
}

function pairedComparisons(rows) {
  const byCase = new Map();

  rows.forEach((r) => {
    const caseId = r.case_id;
    if (!caseId) return;
    if (!byCase.has(caseId)) byCase.set(caseId, {});
    const item = byCase.get(caseId);
    const mode = String(r.mode).toLowerCase();
    if (mode === "vision" || mode === "mcp") item[mode] = r;
  });

  const paired = [];
  for (const [caseId, pair] of byCase.entries()) {
    if (!pair.vision || !pair.mcp) continue;
    paired.push({ caseId, vision: pair.vision, mcp: pair.mcp });
  }

  const inputSavings = [];
  const totalSavings = [];
  const latencyDelta = [];
  const qualityDelta = [];

  paired.forEach(({ vision, mcp }) => {
    const vIn = toNumber(vision.input_tokens);
    const mIn = toNumber(mcp.input_tokens);
    if (Number.isFinite(vIn) && Number.isFinite(mIn) && vIn > 0) {
      inputSavings.push((vIn - mIn) / vIn);
    }

    const vTot = toNumber(vision.input_tokens) + toNumber(vision.output_tokens);
    const mTot = toNumber(mcp.input_tokens) + toNumber(mcp.output_tokens);
    if (Number.isFinite(vTot) && Number.isFinite(mTot) && vTot > 0) {
      totalSavings.push((vTot - mTot) / vTot);
    }

    const vLat = toNumber(vision.latency_seconds);
    const mLat = toNumber(mcp.latency_seconds);
    if (Number.isFinite(vLat) && Number.isFinite(mLat)) {
      latencyDelta.push(mLat - vLat);
    }

    const vQ = toNumber(vision.quality_score);
    const mQ = toNumber(mcp.quality_score);
    if (Number.isFinite(vQ) && Number.isFinite(mQ)) {
      qualityDelta.push(mQ - vQ);
    }
  });

  return {
    pairedCount: paired.length,
    medianInputSavings: median(inputSavings),
    medianTotalSavings: median(totalSavings),
    medianLatencyDelta: median(latencyDelta),
    medianQualityDelta: median(qualityDelta),
  };
}

function evaluate(statsMcp, pairedStats) {
  const criteria = [
    {
      name: "Median input token savings >= 50%",
      ok:
        Number.isFinite(pairedStats.medianInputSavings) &&
        pairedStats.medianInputSavings >= 0.5,
    },
    {
      name: "Median quality delta (MCP - Vision) >= 0",
      ok:
        Number.isFinite(pairedStats.medianQualityDelta) &&
        pairedStats.medianQualityDelta >= 0,
    },
    {
      name: "MCP failure rate <= 5%",
      ok:
        Number.isFinite(statsMcp.successRate) &&
        1 - statsMcp.successRate <= 0.05,
    },
  ];

  return {
    criteria,
    pass: criteria.every((c) => c.ok),
  };
}

function printModeStats(name, stats) {
  console.log(`\n${name.toUpperCase()} (${stats.count} runs)`);
  console.log(`- Success rate: ${pct(stats.successRate)}`);
  console.log(`- Median input tokens: ${num(stats.medianInput, 0)}`);
  console.log(`- Median output tokens: ${num(stats.medianOutput, 0)}`);
  console.log(`- Median total tokens: ${num(stats.medianTotal, 0)}`);
  console.log(`- Median latency (s): ${num(stats.medianLatency, 2)}`);
  console.log(`- Median quality score: ${num(stats.medianQuality, 2)}`);
}

function main() {
  const fileArg = process.argv[2];
  if (!fileArg) {
    console.error("Usage: node scripts/benchmark_report.js <csv_file>");
    process.exit(1);
  }

  const filePath = path.resolve(process.cwd(), fileArg);
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  const csvText = fs.readFileSync(filePath, "utf8");
  const rows = parseCsv(csvText);
  if (!rows.length) {
    console.error("No data rows found.");
    process.exit(1);
  }

  const modes = rows.reduce((acc, r) => {
    const mode = String(r.mode || "").toLowerCase();
    if (!acc[mode]) acc[mode] = [];
    acc[mode].push(r);
    return acc;
  }, {});

  const visionRows = modes.vision || [];
  const mcpRows = modes.mcp || [];

  const visionStats = pickStats(visionRows);
  const mcpStats = pickStats(mcpRows);
  const pairedStats = pairedComparisons(rows);
  const evalResult = evaluate(mcpStats, pairedStats);

  console.log("PaperFlow MCP Savings Benchmark");
  console.log(`Source file: ${filePath}`);
  console.log(`Total rows: ${rows.length}`);
  console.log(`Paired cases (vision + mcp): ${pairedStats.pairedCount}`);

  printModeStats("vision", visionStats);
  printModeStats("mcp", mcpStats);

  console.log("\nPAIRED DELTAS (MCP vs Vision)");
  console.log(`- Median input token savings: ${pct(pairedStats.medianInputSavings)}`);
  console.log(`- Median total token savings: ${pct(pairedStats.medianTotalSavings)}`);
  console.log(`- Median latency delta (s): ${num(pairedStats.medianLatencyDelta, 2)}`);
  console.log(`- Median quality delta: ${num(pairedStats.medianQualityDelta, 2)}`);

  console.log("\nPASS/FAIL");
  evalResult.criteria.forEach((c) => {
    console.log(`- [${c.ok ? "PASS" : "FAIL"}] ${c.name}`);
  });
  console.log(`\nFINAL: ${evalResult.pass ? "PASS" : "FAIL"}`);
}

main();
