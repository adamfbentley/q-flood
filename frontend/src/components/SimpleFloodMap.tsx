import React from 'react';

interface SimpleFloodMapProps {
  geojson: GeoJSON.FeatureCollection;
}

const SimpleFloodMap: React.FC<SimpleFloodMapProps> = ({ geojson }) => {
  // Extract flood depth data
  const features = geojson.features || [];
  
  if (features.length === 0) {
    return <div className="text-gray-500 p-4">No flood data to visualize.</div>;
  }

  // Find grid dimensions and max depth
  let maxRow = 0, maxCol = 0, maxDepth = 0;
  const grid: { [key: string]: number } = {};

  features.forEach((feature: any) => {
    const { row, col, flood_depth } = feature.properties || {};
    if (row !== undefined && col !== undefined && flood_depth !== undefined) {
      maxRow = Math.max(maxRow, row);
      maxCol = Math.max(maxCol, col);
      maxDepth = Math.max(maxDepth, flood_depth);
      grid[`${row},${col}`] = flood_depth;
    }
  });

  // Calculate statistics
  const totalCells = (maxRow + 1) * (maxCol + 1);
  const floodedCells = features.length;
  const avgDepth = features.reduce((sum: number, f: any) => sum + (f.properties?.flood_depth || 0), 0) / floodedCells;

  // Color function based on flood depth
  const getColor = (depth: number): string => {
    if (depth === 0) return '#f3f4f6'; // gray-100 for dry
    const intensity = Math.min(depth / maxDepth, 1);
    const r = Math.round(0 + intensity * 220); // Light blue to dark blue
    const g = Math.round(150 - intensity * 50);
    const b = Math.round(220 - intensity * 20);
    return `rgb(${r},${g},${b})`;
  };

  // Create grid visualization
  const cellSize = Math.min(600 / Math.max(maxRow + 1, maxCol + 1), 20);

  return (
    <div className="space-y-4">
      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-gray-600">Max Depth</div>
          <div className="text-2xl font-bold text-blue-600">{maxDepth.toFixed(2)}m</div>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-gray-600">Avg Depth</div>
          <div className="text-2xl font-bold text-blue-600">{avgDepth.toFixed(2)}m</div>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-gray-600">Flooded Cells</div>
          <div className="text-2xl font-bold text-blue-600">{floodedCells}</div>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-gray-600">Coverage</div>
          <div className="text-2xl font-bold text-blue-600">
            {((floodedCells / totalCells) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center space-x-4 text-sm">
        <span className="font-medium">Flood Depth:</span>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(0) }}></div>
          <span>Dry</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(maxDepth * 0.33) }}></div>
          <span>Low</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(maxDepth * 0.66) }}></div>
          <span>Medium</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(maxDepth) }}></div>
          <span>High ({maxDepth.toFixed(2)}m)</span>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="overflow-auto bg-gray-50 p-4 rounded-lg">
        <div
          className="grid gap-px bg-gray-300"
          style={{
            gridTemplateColumns: `repeat(${maxCol + 1}, ${cellSize}px)`,
            gridTemplateRows: `repeat(${maxRow + 1}, ${cellSize}px)`,
          }}
        >
          {Array.from({ length: maxRow + 1 }).map((_, row) =>
            Array.from({ length: maxCol + 1 }).map((_, col) => {
              const depth = grid[`${row},${col}`] || 0;
              return (
                <div
                  key={`${row},${col}`}
                  className="relative group"
                  style={{
                    backgroundColor: getColor(depth),
                    width: `${cellSize}px`,
                    height: `${cellSize}px`,
                  }}
                  title={depth > 0 ? `(${row},${col}): ${depth.toFixed(3)}m` : `(${row},${col}): Dry`}
                >
                  {/* Tooltip on hover */}
                  {depth > 0 && (
                    <div className="hidden group-hover:block absolute z-10 bg-white text-xs p-2 rounded shadow-lg pointer-events-none"
                         style={{ left: '100%', top: '0', whiteSpace: 'nowrap' }}>
                      <div>Position: ({row}, {col})</div>
                      <div className="font-bold text-blue-600">Depth: {depth.toFixed(3)}m</div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Info */}
      <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded">
        <p><strong>How to read this map:</strong></p>
        <ul className="list-disc ml-5 mt-1 space-y-1">
          <li>Each cell represents a grid point in your simulation</li>
          <li>Darker blue = deeper water</li>
          <li>Gray = dry land (no flooding)</li>
          <li>Hover over cells to see exact flood depth</li>
          <li>Grid dimensions: {maxRow + 1} × {maxCol + 1} = {totalCells} cells</li>
        </ul>
      </div>

      {/* Download suggestion */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <p className="text-sm text-yellow-800">
          <strong>💡 Tip:</strong> For interactive 3D visualization and real geographic mapping, download the GeoJSON file and open it in:
        </p>
        <ul className="list-disc ml-5 mt-2 text-sm text-yellow-700">
          <li><strong>QGIS</strong> (free desktop GIS software)</li>
          <li><strong>geojson.io</strong> (online viewer)</li>
          <li><strong>kepler.gl</strong> (advanced 3D visualization)</li>
        </ul>
      </div>
    </div>
  );
};

export default SimpleFloodMap;
