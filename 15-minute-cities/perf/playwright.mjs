/**
* This script has been rewritten from using k6 to playwright to get more accurate timings of tiles.
* The rewrite has mainly been done by recording tests and using AI, therefore there might be some rough edges.
*/

import fs from "fs";
import path from "path";
import { chromium } from "playwright";

const baseUrl = process.env.BASE_URL || "https://walkablecity.app";
const summaryPath = process.env.PLAYWRIGHT_SUMMARY_MD_PATH || "benchmark-results/summary.md";
const requestTimeoutMs = 30_000;
const settleIdleMs = 750;
const settleTimeoutMs = 15_000;

const cities = [
  { id: "copenhagen", lat: 55.6761, lon: 12.5683 },
  { id: "aarhus", lat: 56.1629, lon: 10.2039 },
  { id: "odense", lat: 55.4038, lon: 10.4024 },
  { id: "fredensborg", lat: 55.9784, lon: 12.4 },
];

const zooms = [8, 11, 14, 17];

const scenarios = cities.flatMap((city) =>
  zooms.map((zoom) => ({ id: `${city.id}_z${zoom}`, lat: city.lat, lon: city.lon, zoom }))
);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function isTileRequest(url) {
  return url.includes("/tiles/");
}

async function waitForTileSettling(tracker) {
  const start = Date.now();
  while (Date.now() - start < settleTimeoutMs) {
    if (tracker.observed > 0 && tracker.pending === 0 && Date.now() - tracker.lastActivity >= settleIdleMs) {
      return;
    }
    await sleep(100);
  }
  throw new Error("Tile requests did not settle in time");
}

async function runScenario(browser, scenario) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  page.setDefaultTimeout(requestTimeoutMs);

  const starts = new Map();
  const tileDurations = [];
  const tracker = { observed: 0, pending: 0, lastActivity: Date.now() };

  page.on("request", (req) => {
    if (!isTileRequest(req.url())) return;
    tracker.observed++;
    tracker.pending++;
    tracker.lastActivity = Date.now();
    starts.set(req, Date.now());
  });

  const onDone = (req) => {
    if (!isTileRequest(req.url())) return;
    const start = starts.get(req);
    if (start != null) tileDurations.push(Date.now() - start);
    starts.delete(req);
    tracker.pending = Math.max(0, tracker.pending - 1);
    tracker.lastActivity = Date.now();
  };

  page.on("requestfinished", onDone);
  page.on("requestfailed", onDone);

  const pageStart = Date.now();
  const response = await page.goto(`${baseUrl}?lat=${scenario.lat}&lon=${scenario.lon}&zoom=${scenario.zoom}`, {
    waitUntil: "domcontentloaded",
    timeout: requestTimeoutMs,
  });

  if (!response?.ok()) throw new Error(`Page load failed: ${scenario.id}`);

  await page.waitForSelector(".leaflet-container", { state: "visible" });
  await waitForTileSettling(tracker);

  const pageDuration = Date.now() - pageStart;
  await context.close();

  return { pageDuration, tileDurations };
}

function formatMarkdown(results) {
  const lines = [
    "## Playwright benchmark",
    "Benchmarked against: " + baseUrl,
    "Zoom levels benchmarked: " + zooms.join(", ") +
    "",
    "| Scenario | Page (ms) | Tile count | Tile avg (ms) | Tile max (ms) |",
    "|----------|-----------|------------|---------------|---------------|",
  ];

  for (const r of results) {
    const avg = r.tileDurations.length
      ? (r.tileDurations.reduce((a, b) => a + b, 0) / r.tileDurations.length).toFixed(1)
      : "0.0";
    const max = r.tileDurations.length ? Math.max(...r.tileDurations).toFixed(1) : "0.0";

    lines.push(`| ${r.id} | ${r.pageDuration.toFixed(1)} | ${r.tileDurations.length} | ${avg} | ${max} |`);
  }

  return lines.join("\n");
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const results = [];

  for (const scenario of scenarios) {
    const result = await runScenario(browser, scenario);
    results.push({ id: scenario.id, ...result });
  }

  await browser.close();

  const markdown = formatMarkdown(results);
  console.log(markdown);

  fs.mkdirSync(path.dirname(summaryPath), { recursive: true });
  fs.writeFileSync(summaryPath, `${markdown}\n`, "utf8");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
