import type { ScoreRange } from "../types/mapTypes";

export const MAX_SCORE_RANGE: ScoreRange = [0, 10000];

/**
 * Generates a MapLibre expression for interpolating colors based on score values.
 *
 * See: https://maplibre.org/maplibre-style-spec/expressions/
 * @param currentRange The current score range to use for color interpolation.
 * @returns An array representing the MapLibre expression for color interpolation.
 */
export function colorInterpolate(currentRange: ScoreRange) {
    const minSpreadFraction = 0.5;
    const globalSpread = MAX_SCORE_RANGE[1] - MAX_SCORE_RANGE[0];
    const minSpread = globalSpread * minSpreadFraction;
    const mid = (currentRange[0] + currentRange[1]) / 2;
    const halfSpread = Math.max((currentRange[1] - currentRange[0]) / 2, minSpread / 2);
    const min = Math.max(MAX_SCORE_RANGE[0], mid - halfSpread);
    const max = Math.min(MAX_SCORE_RANGE[1], mid + halfSpread);

    return [
        "interpolate", ["linear"],
        ["get", "score"],
        min, "#d73027",
        (min + max) / 2, "#f3f37d",
        max, "#1a9850"
    ];
}

export function colorInterpolateColorBlind(currentRange: ScoreRange) {
    // TODO
}