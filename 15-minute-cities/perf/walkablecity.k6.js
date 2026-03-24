import http from "k6/http";
import { sleep } from "k6";

const baseUrl = __ENV.BASE_URL || "https://walkablecity.app";
const iterations = Number(__ENV.K6_ITERATIONS || 5);

export const options = {
  vus: 1,
  iterations,
};

export default function () {
  http.get(`${baseUrl}/`);
  http.get(`${baseUrl}/tiles/scored_grids_pmtiles_p5/6/34/20`);
  http.get(`${baseUrl}/tiles/scored_grids_pmtiles_p6/11/1095/641`);
  http.get(`${baseUrl}/tiles/scored_grids_pmtiles_p7/14/8763/5128`);
  http.get(`${baseUrl}/tiles/scored_edges_pmtiles_p0/15/17527/10256`);

  sleep(1);
}

export function handleSummary(data) {
  const markdown = `
## k6 benchmark

Target: ${baseUrl}

| Metric | Value |
|------|------|
| Requests | ${data.metrics.http_reqs.values.count} |
| Avg latency | ${data.metrics.http_req_duration.values.avg.toFixed(1)} ms |
| p95 latency | ${data.metrics.http_req_duration.values["p(95)"].toFixed(1)} ms |
`;

  const output = { stdout: markdown };

  if (__ENV.K6_SUMMARY_MD_PATH) {
    output[__ENV.K6_SUMMARY_MD_PATH] = markdown;
  }

  return output;
}