import type { ScoreRange } from "../types/mapTypes";
import type { ExpressionSpecification } from "maplibre-gl";

// Must be synced with score range in current pmtiles.
// Check the latest dagster run that materialized the
// 'scored_nodes' asset to find upper bound. TODO: A 
// more robust way of syncing these values would be nice.
export const MAX_SCORE_RANGE: ScoreRange = { min: 0, max: 46000 }; // 45899 + 101 buffer
const MIN_SPREAD_FRACTION: number = 0.1;

/**
 * Clamps spread of {@link range} to some minimum {@link fraction} of {@link within}s spread.
 * @param range The ScoreRange to clamp.
 * @param within The ScoreRange to clamp to.
 * @param fraction The minimum fraction of {@link within} that can be returned
 * @returns {ScoreRange} {@link range} if spread({@link range}) > (spread({@link within}) * {@link fraction}), otherwise (spread({@link within}) * {@link fraction}) centered on midpoint of {@link range}
 */
function clampMinSpread(
    range: ScoreRange, 
    within: ScoreRange = MAX_SCORE_RANGE, 
    fraction: number = MIN_SPREAD_FRACTION
): ScoreRange {
    const maxSpread = within.max - within.min;
    const minSpread = maxSpread * fraction;
    const mid = (range.min + range.max) / 2;
    const halfSpread = Math.max((range.max - range.min) / 2, minSpread / 2);
    const min = Math.max(within.min, mid - halfSpread);
    const max = Math.min(within.max, mid + halfSpread);

    return {min: min, max: max};
}

/**
 * Generates a MapLibre expression for interpolating colors based on score values.
 *
 * See: https://maplibre.org/maplibre-style-spec/expressions/
 * @param currentRange The current score range to use for color interpolation.
 * @returns An array representing the MapLibre expression for color interpolation.
 */
function colorInterpolate(currentRange: ScoreRange): ExpressionSpecification {
    const {min, max} = clampMinSpread(currentRange);

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
    const {min, max} = clampMinSpread(currentRange);

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