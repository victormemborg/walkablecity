/**
 * Defines the structure of the map view, including the center coordinates and zoom level.
 */
export interface MapView {
    center: {
        lat: number;
        lon: number;
    };
    zoom: number;
}