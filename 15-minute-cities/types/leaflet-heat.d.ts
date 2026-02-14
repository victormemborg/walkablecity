import "leaflet";

declare module "leaflet" {
  function heatLayer(
    latlngs: [number, number, number][], // [lat, lng, intensity]
    options?: {
      minOpacity?: number;   // minimum opacity the heat will start at
      maxZoom?: number;      // zoom level where points reach maximum intensity, defaults to map maxZoom
      max?: number;          // maximum point intensity, 1.0 by default
      radius?: number;       // radius of each "point" of the heatmap, 25 by default
      blur?: number;         // amount of blur, 15 by default
      gradient?: Record<number, string>; // color gradient config, e.g. {0.4: 'blue', 0.65: 'lime', 1: 'red'}
      pane?: string;         // map pane where the heat will be drawn, defaults to 'overlayPane'
    }
  ): L.Layer;
}
