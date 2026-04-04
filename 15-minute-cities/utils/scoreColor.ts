import type { ScoreRange } from "../types/mapTypes";
import type { ExpressionSpecification } from "maplibre-gl";

export const MAX_SCORE_RANGE: ScoreRange = [0, 100000];

/**
 * Generates a MapLibre expression for interpolating colors based on score values.
 *
 * See: https://maplibre.org/maplibre-style-spec/expressions/
 * @param currentRange The current score range to use for color interpolation.
 * @returns An array representing the MapLibre expression for color interpolation.
 */
function colorInterpolate(currentRange: ScoreRange): ExpressionSpecification {
    const minSpreadFraction = 0.05;
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
    ] as ExpressionSpecification;
}

/**
 * Generates a MapLibre expression for interpolating colors based on score values.
 * This version is intended for color blind users and should use a color scheme that is distinguishable for common types of color blindness.
 *
 * See: https://maplibre.org/maplibre-style-spec/expressions/
 * @param currentRange The current score range to use for color interpolation.
 * @returns An array representing the MapLibre expression for color interpolation.
 */
function colorInterpolateColorBlind(currentRange: ScoreRange): ExpressionSpecification {
    const minSpreadFraction = 0.05;
    const globalSpread = MAX_SCORE_RANGE[1] - MAX_SCORE_RANGE[0];
    const minSpread = globalSpread * minSpreadFraction;
    const mid = (currentRange[0] + currentRange[1]) / 2;
    const halfSpread = Math.max((currentRange[1] - currentRange[0]) / 2, minSpread / 2);
    const min = Math.max(MAX_SCORE_RANGE[0], mid - halfSpread);
    const max = Math.min(MAX_SCORE_RANGE[1], mid + halfSpread);

    // Based on the Okabe-Ito colorblind palette shown in:
    // https://thenode.biologists.com/data-visualization-with-flying-colors/research/
    return [
        "interpolate", ["linear"],
        ["get", "score"],
        min, "#D55E00",
        min + (max - min) * 0.33, "#E69F00",
        min + (max - min) * 0.66, "#56B4E9",
        max, "#009E73"
    ] as ExpressionSpecification;
}

/**
 * Returns a MapLibre expression for color interpolation based on the given score range and color blind mode.
 * @param currentRange The current score range to use for color interpolation.
 * @param colorBlindMode false for default mode, true for color blind mode
 * @returns An array representing the MapLibre expression for color interpolation.
 */
export function getColorExpression(currentRange: ScoreRange, colorBlindMode: boolean) {
    return colorBlindMode ? colorInterpolateColorBlind(currentRange) : colorInterpolate(currentRange);
}