import type { ScoreRange } from "@/types/mapTypes";
import { getColorPalette } from "./scoreColor";

type LegendEntry = {
  color: string;
  label: string;
  upperBound: number;
  lowerBound: number;
}

/**
 * Builds steps for the legend based on the scoring range and the color palette (amount of steps is determined by the length of the color palette). 
 * Each step includes a color, a label describing the score range it represents, and the upper and lower bounds of that range.
 * Probably a bit overengineered, but it allows for changing the score range and color palette without manually having to adjust the legend over and over again.
 * @param currentRange The score range to use for building the legend.
 * @param colorBlindMode false for default mode, true for color blind mode.
 * @returns a legendentry array with the color, label, and upper/lower bounds for each step in the legend.
 */
export function buildLegend(currentRange: ScoreRange, colorBlindMode: boolean): LegendEntry[] {
  const palette = getColorPalette(colorBlindMode);
  const stepSize = (currentRange[1] - currentRange[0]) / palette.length;

  return palette.map((color, index) => {
    const upperBound = currentRange[1] - stepSize * index;
    const lowerBound = index < palette.length - 1
      ? currentRange[1] - stepSize * (index + 1)
      : currentRange[0];

    let label: string;
    if (index === 0) {
        label = `> ${lowerBound} m`;
    } else {
        label = `${lowerBound} - ${upperBound} m`;
    }

    return { color, label, upperBound, lowerBound };
  });
}