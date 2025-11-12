import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import FloodMap3D from './FloodMap3D';
import 'mapbox-gl/dist/mapbox-gl.css'; // Mock this if it causes issues in tests

// Mock DeckGL and Map components to avoid actual rendering issues in JSDOM
vi.mock('@deck.gl/react', () => ({
  __esModule: true,
  default: vi.fn(({ children }) => <div data-testid="deckgl-mock">{children}</div>),
}));
vi.mock('@deck.gl/layers', () => ({
  GeoJsonLayer: vi.fn(() => ({ id: 'mock-geojson-layer' })),
}));
vi.mock('react-map-gl', () => ({
  __esModule: true,
  default: vi.fn(() => <div data-testid="mapbox-mock"></div>),
}));

describe('FloodMap3D', () => {
  // Mock environment variable for Mapbox token
  beforeEach(() => {
    vi.stubEnv('VITE_MAPBOX_ACCESS_TOKEN', 'test-token');
  });

  const mockGeojson: GeoJSON.FeatureCollection = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        properties: { flood_depth: 1.5 },
        geometry: {
          type: 'Polygon',
          coordinates: [
            [
              [-74.01, 40.70],
              [-74.00, 40.70],
              [-74.00, 40.71],
              [-74.01, 40.71],
              [-74.01, 40.70]
            ]
          ]
        }
      },
      {
        type: 'Feature',
        properties: { flood_depth: 2.0 },
        geometry: {
          type: 'Point',
          coordinates: [-73.99, 40.72]
        }
      },
      {
        type: 'Feature',
        properties: { flood_depth: 0.5 },
        geometry: {
          type: 'MultiPolygon',
          coordinates: [
            [
              [
                [-74.05, 40.65],
                [-74.04, 40.65],
                [-74.04, 40.66],
                [-74.05, 40.66],
                [-74.05, 40.65]
              ]
            ],
            [
              [
                [-74.03, 40.67],
                [-74.02, 40.67],
                [-74.02, 40.68],
                [-74.03, 40.68],
                [-74.03, 40.67]
              ]
            ]
          ]
        }
      }
    ]
  };

  it('renders without crashing when Mapbox token is set', () => {
    render(<FloodMap3D geojson={mockGeojson} />);
    expect(screen.getByTestId('deckgl-mock')).toBeInTheDocument();
    expect(screen.getByTestId('mapbox-mock')).toBeInTheDocument();
  });

  it('displays an error message if Mapbox token is not set', () => {
    vi.stubEnv('VITE_MAPBOX_ACCESS_TOKEN', ''); // Unset token for this test
    render(<FloodMap3D geojson={mockGeojson} />);
    expect(screen.getByText(/Mapbox Access Token is not set/i)).toBeInTheDocument();
  });

  it('passes geojson data to GeoJsonLayer', () => {
    render(<FloodMap3D geojson={mockGeojson} />);
    // Check if GeoJsonLayer was called with the correct data
    expect(require('@deck.gl/layers').GeoJsonLayer).toHaveBeenCalledWith(
      expect.objectContaining({
        data: mockGeojson,
        extruded: true,
        getElevation: expect.any(Function),
        getFillColor: [0, 100, 200, 160],
        pickable: true,
        autoHighlight: true,
        onHover: expect.any(Function)
      })
    );
  });

  // Note: Testing onHover behavior (tooltip state update) with mocked DeckGL/Map
  // is challenging without a full DOM environment or more sophisticated mocks.
  // This test verifies the onHover prop is passed.
});
