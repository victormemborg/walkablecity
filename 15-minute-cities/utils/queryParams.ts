import type { MapView } from "@/types/mapTypes";

/**
 * The default view when opening the map without query parametrs.
 * Currently set to the center of Copenhagen.
 */
const DEFAULT_VIEW: MapView = {
  center: {
    lat: 55.6761,
    lon: 12.5683,
  },
  zoom: 11,
};

/**
 * Parses a string value into a finite float, returning a fallback value if the input is invalid or not provided.
 * @param value The string value to parse as a float.
 * @param fallback The fallback value to return if the input is invalid or not provided.
 * @returns The parsed float value or the fallback value.
 */
function parseFiniteFloat(value: string | null, fallback: number): number {
  if (!value) {
    return fallback;
  }

  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

/**
 * Parses a string value into a finite integer, returning a fallback value if the input is invalid or not provided.
 * @param value The string value to parse as an integer.
 * @param fallback The fallback value to return if the input is invalid or not provided.
 * @returns The parsed integer value or the fallback value.
 */
function parseFiniteInt(value: string | null, fallback: number): number {
  if (!value) {
    return fallback;
  }

  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

/**
 * Parses the map view parameters from the URL search parameters, providing default values if any parameters are missing or invalid.
 * @param searchParams The URLSearchParams object containing the query parameters to parse.
 * @returns The parsed MapView object with the center coordinates and zoom level.
 */
export function parseMapView(searchParams: URLSearchParams): MapView {
  return {
    center: {
      lat: parseFiniteFloat(searchParams.get("lat"), DEFAULT_VIEW.center.lat),
      lon: parseFiniteFloat(searchParams.get("lon"), DEFAULT_VIEW.center.lon),
    },
    zoom: parseFiniteInt(searchParams.get("zoom"), DEFAULT_VIEW.zoom),
  };
}
