/**
 * Defines the structure of the map view, including the center coordinates and zoom level.
 */
export type MapView = {
    center: {
        lat: number;
        lon: number;
    };
    zoom: number;
}

/**
 * 
 */
export type ScoreRange = [min: number, max: number];