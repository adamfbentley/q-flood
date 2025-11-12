import logging
import numpy as np
import geojson
from app.core.object_storage import MinioClient
import io
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class GISPostProcessorService:
    def __init__(self):
        self.minio_client = MinioClient()

    def _convert_solution_to_flood_depth(self, solution_vector: np.ndarray, parameters: dict) -> np.ndarray:
        """
        Converts the raw solver solution (e.g., pressure field) into flood depth.
        This conversion now incorporates basic hydrological parameters.
        """
        conversion_factor = parameters.get("conversion_factor", 0.1)
        base_elevation = parameters.get("base_elevation", 0.0) # Example: uniform base elevation
        water_level_offset = parameters.get("water_level_offset", 0.0) # Example: constant water level increase

        # Simulate flood depth calculation: solution contributes to water level above base elevation
        # Ensure non-negative depths
        flood_depth = solution_vector * conversion_factor + water_level_offset - base_elevation
        flood_depth[flood_depth < 0] = 0
        return flood_depth

    def _generate_geojson_from_flood_depth(self, flood_depth: np.ndarray, job_id: str, parameters: dict) -> dict:
        """
        Generates a GeoJSON FeatureCollection representing flood polygons.
        Each grid cell exceeding the flood threshold is represented by a square polygon.
        """
        grid_resolution = parameters.get("grid_resolution", 50)
        threshold = parameters.get("flood_threshold", 0.05) # Example threshold for flood depth

        features = []

        # Reshape the 1D solution vector back into a 2D grid for visualization
        try:
            grid_depth = flood_depth.reshape((grid_resolution, grid_resolution))
        except ValueError:
            logger.warning(f"[{job_id}] Flood depth vector size ({flood_depth.size}) does not match expected grid_resolution ({grid_resolution}x{grid_resolution}). Cannot reshape. Generating a point feature instead.")
            if flood_depth.size > 0:
                avg_depth = np.mean(flood_depth)
                point = geojson.Point((0, 0)) # Dummy coordinate
                feature = geojson.Feature(geometry=point, properties={"job_id": job_id, "average_flood_depth": float(avg_depth), "description": "Simplified point flood representation due to grid mismatch."})
                return geojson.FeatureCollection([feature])
            else:
                return geojson.FeatureCollection([])

        # Generate a square polygon for each flooded cell
        for r in range(grid_resolution):
            for c in range(grid_resolution):
                if grid_depth[r, c] > threshold:
                    # Define coordinates for the cell (assuming a simple 1x1 unit grid for visualization)
                    # Adjust these coordinates if a real-world extent is available
                    min_x, min_y = c, r
                    max_x, max_y = c + 1, r + 1

                    polygon = geojson.Polygon([[
                        (min_x, min_y),
                        (max_x, min_y),
                        (max_x, max_y),
                        (min_x, max_y),
                        (min_x, min_y)
                    ]])
                    properties = {
                        "job_id": job_id,
                        "row": r,
                        "col": c,
                        "flood_depth": float(grid_depth[r, c]),
                        "description": f"Flooded cell at ({r},{c})"
                    }
                    features.append(geojson.Feature(geometry=polygon, properties=properties))

        return geojson.FeatureCollection(features)

    def _generate_pdf_report(self, job_id: str, parameters: dict, geojson_path: str, solution_path: str, flood_depth: np.ndarray) -> bytes:
        """
        Generates a text-based PDF report with more detailed statistics and a simulated map.
        """
        grid_resolution = parameters.get("grid_resolution", 50)
        threshold = parameters.get("flood_threshold", 0.05)

        # Reshape flood_depth for map visualization, handle mismatch gracefully
        try:
            grid_depth = flood_depth.reshape((grid_resolution, grid_resolution))
        except ValueError:
            grid_depth = np.zeros((grid_resolution, grid_resolution)) # Fallback to empty grid for map
            logger.warning(f"[{job_id}] Could not reshape flood_depth for PDF map. Using empty grid.")

        # Calculate statistics
        max_depth = np.max(flood_depth) if flood_depth.size > 0 else 0.0
        min_depth = np.min(flood_depth) if flood_depth.size > 0 else 0.0
        avg_depth = np.mean(flood_depth) if flood_depth.size > 0 else 0.0
        flooded_cells_count = np.sum(flood_depth > threshold)
        total_cells = flood_depth.size
        flooded_percentage = (flooded_cells_count / total_cells * 100) if total_cells > 0 else 0.0

        # Generate ASCII art map
        map_lines = []
        map_lines.append("  " + "-" * (grid_resolution * 2 + 1))
        for r in range(grid_resolution):
            row_str = f"{r:2d}|"
            for c in range(grid_resolution):
                if grid_depth[r, c] > threshold:
                    row_str += " F"
                else:
                    row_str += " ."
            map_lines.append(row_str + " |")
        map_lines.append("  " + "-" * (grid_resolution * 2 + 1))
        map_lines.append("    " + " ".join([f"{i%10}" for i in range(grid_resolution)]))
        ascii_map = "\n".join(map_lines)

        report_content = f"""
Flood Simulation Report for Job ID: {job_id}
Generated On: {datetime.now().isoformat()}

Solver Type: {parameters.get('solver_type', 'N/A')}
Grid Resolution: {grid_resolution}x{grid_resolution}
Flood Threshold: {threshold:.2f}

Raw Solution Path: {solution_path}
GeoJSON Output Path: {geojson_path}

--- Flood Statistics ---
Max Flood Depth: {max_depth:.2f}
Min Flood Depth: {min_depth:.2f}
Average Flood Depth: {avg_depth:.2f}
Flooded Cells: {flooded_cells_count} / {total_cells} ({flooded_percentage:.2f}%)

--- Simulated Flood Map (F=Flooded, .=Dry) ---
{ascii_map}

--- Notes ---
This report provides a summary of the flood simulation job.
Detailed flood extent data is available in the GeoJSON file.
"""
        return report_content.encode('utf-8') # Return as bytes for consistency with file uploads

    def postprocess_solution(self, solution_path: str, job_id: str, parameters: dict) -> tuple[str, str]:
        """
        Downloads the raw solution, converts it to flood depth, generates GeoJSON,
        and creates a PDF report, then uploads them to object storage.
        """
        logger.info(f"[{job_id}] Starting GIS post-processing for solution: {solution_path}")

        # 1. Download raw solution (x) from object storage
        solution_data = self.minio_client.download_file(solution_path)
        solution_vector = np.load(io.BytesIO(solution_data))
        logger.info(f"[{job_id}] Loaded solution vector (shape: {solution_vector.shape}).")

        # 2. Convert solution to flood depth
        flood_depth = self._convert_solution_to_flood_depth(solution_vector, parameters)
        logger.info(f"[{job_id}] Converted solution to flood depth. Max depth: {np.max(flood_depth):.2f}")

        # 3. Generate GeoJSON
        geojson_data = self._generate_geojson_from_flood_depth(flood_depth, job_id, parameters)
        geojson_str = geojson.dumps(geojson_data, indent=2)

        geojson_object_name = f"jobs/{job_id}/results/flood_data_{uuid.uuid4()}.geojson"
        self.minio_client.upload_file(geojson_object_name, geojson_str.encode('utf-8'), len(geojson_str.encode('utf-8')), "application/geo+json")
        logger.info(f"[{job_id}] GeoJSON data saved to {geojson_object_name}")

        # 4. Generate PDF report (as a text file for now)
        pdf_content = self._generate_pdf_report(job_id, parameters, geojson_object_name, solution_path, flood_depth)

        pdf_object_name = f"jobs/{job_id}/results/flood_report_{uuid.uuid4()}.pdf"
        self.minio_client.upload_file(pdf_object_name, pdf_content, len(pdf_content), "application/pdf")
        logger.info(f"[{job_id}] PDF report saved to {pdf_object_name}")

        return geojson_object_name, pdf_object_name
