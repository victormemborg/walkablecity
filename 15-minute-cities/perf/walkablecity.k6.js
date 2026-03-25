import http from "k6/http";
import { check, sleep } from "k6";

const baseUrl = __ENV.BASE_URL || "https://walkablecity.app";

const cities = [
  { id: "copenhagen", lat: 55.6761, lon: 12.5683 },
  { id: "aarhus", lat: 56.1629, lon: 10.2039 },
  { id: "odense", lat: 55.4038, lon: 10.4024 },
  { id: "fredensborg", lat: 55.9784, lon: 12.4 },
];

const zooms = [6, 11, 14, 15];

const scenarios = cities.flatMap((city) =>
  zooms.map((zoom) => ({
    id: `${city.id}_z${zoom}`,
    lat: city.lat,
    lon: city.lon,
    zoom,
  }))
);

export const options = {
  vus: 1,
  iterations: Number(__ENV.K6_ITERATIONS || 5),
  thresholds: Object.fromEntries(
    scenarios.map(({ id }) => [`http_req_duration{name:${id}}`, []])
  ),
};

export default function () {
  for (const { id, lat, lon, zoom } of scenarios) {
    const res = http.get(`${baseUrl}?lat=${lat}&lon=${lon}&zoom=${zoom}`, {
      tags: { name: id },
    });
    check(res, { [`${id} 200`]: (r) => r.status === 200 });
  }
  sleep(1);
}

export function handleSummary(data) {
  const { avg, "p(95)": p95 } = data.metrics.http_req_duration.values;
  const total = data.metrics.http_reqs.values.count;

  const header = "| Scenario | Zoom | Avg (ms) | p95 (ms) |";
  const divider = "|----------|------|----------|----------|";
  const rows = scenarios
    .map(({ id, zoom }) => {
      const v = data.metrics[`http_req_duration{name:${id}}`]?.values;
      return v ? `| ${id} | ${zoom} | ${v.avg.toFixed(1)} | ${v["p(95)"].toFixed(1)} |` : null;
    })
    .filter(Boolean)
    .join("\n");

  const md = `
## k6 benchmark — ${baseUrl}

${header}
${divider}
${rows}

**Total requests:** ${total} | **Avg:** ${avg.toFixed(1)} ms | **p95:** ${p95.toFixed(1)} ms
`;

  const output = { stdout: md };
  if (__ENV.K6_SUMMARY_MD_PATH) {
    output[__ENV.K6_SUMMARY_MD_PATH] = md;
  }
  return output;
}