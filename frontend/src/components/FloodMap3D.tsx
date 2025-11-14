import React, { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { GeoJsonLayer } from '@deck.gl/layers';
import Map from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface FloodMap3DProps {
  geojson: GeoJSON.FeatureCollection;
  initialViewState?: {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch: number;
    bearing: number;
  };
}

interface TooltipState {
  x: number;
  y: number;
  content: string;
  visible: boolean;
}

const MAPBOX_ACCESS_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

// Helper function to extract all coordinates from a GeoJSON geometry
function extractCoordinates(geometry: GeoJSON.Geometry): number[][] {
  const coords: number[][] = [];

  if (!geometry) return coords;

  switch (geometry.type) {
    case 'Point':
      coords.push((geometry as GeoJSON.Point).coordinates);
      break;
    case 'LineString':
      (geometry as GeoJSON.LineString).coordinates.forEach(c => coords.push(c));
      break;
    case 'Polygon':
      // Polygon: Array of LinearRing coordinates. First element is exterior ring, others are interior rings (holes).
      (geometry as GeoJSON.Polygon).coordinates.forEach(linearRing => {
        linearRing.forEach(c => coords.push(c));
      });
      break;
    case 'MultiPoint':
      (geometry as GeoJSON.MultiPoint).coordinates.forEach(c => coords.push(c));
      break;
    case 'MultiLineString':
      (geometry as GeoJSON.MultiLineString).coordinates.forEach(line => {
        line.forEach(c => coords.push(c));
      });
      break;
    case 'MultiPolygon':
      // MultiPolygon: Array of Polygon coordinates.
      (geometry as GeoJSON.MultiPolygon).coordinates.forEach(polygon => {
        polygon.forEach(linearRing => {
          linearRing.forEach(c => coords.push(c));
        });
      });
      break;
    case 'GeometryCollection':
      (geometry as GeoJSON.GeometryCollection).geometries.forEach(geom => {
        coords.push(...extractCoordinates(geom));
      });
      break;
  }
  return coords;
}

const FloodMap3D: React.FC<FloodMap3DProps> = ({ geojson, initialViewState }) => {
  const [viewState, setViewState] = useState({
    longitude: initialViewState?.longitude || 0,
    latitude: initialViewState?.latitude || 0,
    zoom: initialViewState?.zoom || 10,
    pitch: initialViewState?.pitch || 45,
    bearing: initialViewState?.bearing || 0,
  });
  const [tooltip, setTooltip] = useState<TooltipState>({ x: 0, y: 0, content: '', visible: false });

  useEffect(() => {
    // Calculate bounding box and center the map on the GeoJSON data
    if (geojson && geojson.features.length > 0) {
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      let hasValidCoords = false;

      geojson.features.forEach(feature => {
        if (feature.geometry) {
          const featureCoords = extractCoordinates(feature.geometry);
          featureCoords.forEach(coord => {
            if (coord.length >= 2) { // Ensure it's a valid [longitude, latitude] pair
              minX = Math.min(minX, coord[0]);
              minY = Math.min(minY, coord[1]);
              maxX = Math.max(maxX, coord[0]);
              maxY = Math.max(maxY, coord[1]);
              hasValidCoords = true;
            }
          });
        }
      });

      if (hasValidCoords) {
        const centerLongitude = (minX + maxX) / 2;
        const centerLatitude = (minY + maxY) / 2;

        // Simple zoom calculation based on bounding box extent
        const longitudeDelta = maxX - minX;
        const latitudeDelta = maxY - minY;
        const maxDelta = Math.max(longitudeDelta, latitudeDelta);

        let zoom = 10; // Default zoom
        if (maxDelta > 0) {
          // Heuristic for zoom level. Adjust constants as needed for desired fit.
          zoom = Math.min(15, Math.max(5, 12 - Math.log2(maxDelta)));
        }

        setViewState(prev => ({
          ...prev,
          longitude: centerLongitude,
          latitude: centerLatitude,
          zoom: zoom,
        }));
      }
    }
  }, [geojson]);

  const layers = [
    new GeoJsonLayer({
      id: 'geojson-layer',
      data: geojson,
      filled: true,
      extruded: true,
      getElevation: f => f.properties?.flood_depth * 100 || 0, // Scale depth for visualization
      getFillColor: [0, 100, 200, 160], // Blue color for water
      getLineColor: [0, 0, 0, 0],
      pickable: true,
      autoHighlight: true,
      onHover: ({ object, x, y }) => {
        if (object && object.properties?.flood_depth !== undefined) {
          setTooltip({
            x,
            y,
            content: `Flood Depth: ${object.properties.flood_depth.toFixed(2)}m`,
            visible: true,
          });
        } else {
          setTooltip({ ...tooltip, visible: false });
        }
      },
      onDrag: () => setTooltip({ ...tooltip, visible: false }), // Hide tooltip on drag
      onClick: () => setTooltip({ ...tooltip, visible: false }), // Hide tooltip on click
    }),
  ];

  if (!MAPBOX_ACCESS_TOKEN) {
    return <div className="text-red-500 p-4">Mapbox Access Token is not set. Please configure VITE_MAPBOX_ACCESS_TOKEN in your .env file.</div>;
  }

  return (
    <div className="relative w-full h-[500px] rounded-lg overflow-hidden">
      <DeckGL
        initialViewState={viewState}
        controller={true}
        layers={layers}
        onViewStateChange={({ viewState }) => {
          setViewState(viewState);
          setTooltip({ ...tooltip, visible: false }); // Hide tooltip when map moves
        }}
      >
        <Map
          mapboxAccessToken={MAPBOX_ACCESS_TOKEN}
          mapStyle="mapbox://styles/mapbox/streets-v11"
          reuseMaps
        />
      </DeckGL>
      {tooltip.visible && (
        <div
          className="absolute bg-white text-gray-800 p-2 rounded-md shadow-lg pointer-events-none z-50"
          style={{ left: tooltip.x + 10, top: tooltip.y + 10 }}
        >
          {tooltip.content}
        </div>
      )}
    </div>
  );
};

export default FloodMap3D;
