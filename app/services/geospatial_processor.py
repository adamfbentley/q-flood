import logging
import io
import json
import rasterio
from rasterio.errors import RasterioIOError
from shapely.geometry import box
import fiona
import geopandas as gpd
from jsonschema import validate, ValidationError
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class GeospatialProcessorService:
    def __init__(self):
        pass

    def validate_geospatial_data(self, file_content: bytes, file_type: str, job_id: str) -> bool:
        """
        Performs comprehensive validation of geospatial data based on its inferred MIME type.
        """
        logger.info(f"[{job_id}] Starting validation for file type: {file_type}")

        if file_type in ("image/tiff", "application/geotiff"): # GeoTIFF
            try:
                with rasterio.open(io.BytesIO(file_content)) as src:
                    if not src.crs:
                        logger.warning(f"[{job_id}] GeoTIFF validation warning: No CRS found.")
                    if src.count == 0:
                        logger.error(f"[{job_id}] GeoTIFF validation failed: No raster bands found.")
                        return False
                    logger.info(f"[{job_id}] GeoTIFF validation successful. Bands: {src.count}, CRS: {src.crs}")
                    return True
            except RasterioIOError as e:
                logger.error(f"[{job_id}] GeoTIFF validation failed due to RasterioIOError: {e}", exc_info=True)
                return False
            except Exception as e:
                logger.error(f"[{job_id}] GeoTIFF validation failed due to unexpected error: {e}", exc_info=True)
                return False
        elif file_type == "application/zip": # Common for Shapefiles
            try:
                # Fiona can open zip files directly if they contain a shapefile
                with fiona.open(io.BytesIO(file_content)) as src:
                    if not src.driver:
                        logger.error(f"[{job_id}] Shapefile validation failed: Could not determine driver.")
                        return False
                    if len(src) == 0:
                        logger.warning(f"[{job_id}] Shapefile validation warning: No features found.")
                    logger.info(f"[{job_id}] Shapefile validation successful. Driver: {src.driver}, CRS: {src.crs}")
                    return True
            except fiona.errors.DriverError as e:
                logger.error(f"[{job_id}] Shapefile validation failed due to Fiona DriverError: {e}", exc_info=True)
                return False
            except Exception as e:
                logger.error(f"[{job_id}] Shapefile validation failed due to unexpected error: {e}", exc_info=True)
                return False
        elif file_type == "application/json":
            try:
                data = json.loads(file_content.decode('utf-8'))
                # Define a simple schema for expected config parameters
                config_schema = {
                    "type": "object",
                    "properties": {
                        "grid_resolution": {"type": "integer", "minimum": 1},
                        "conversion_factor": {"type": "number", "minimum": 0},
                        "base_elevation": {"type": "number"},
                        "water_level_offset": {"type": "number"},
                        "flood_threshold": {"type": "number", "minimum": 0}
                    },
                    "additionalProperties": True # Allow other parameters
                }
                validate(instance=data, schema=config_schema)
                logger.info(f"[{job_id}] JSON config file validation successful.")
                return True
            except json.JSONDecodeError as e:
                logger.error(f"[{job_id}] JSON config file validation failed: Invalid JSON format: {e}", exc_info=True)
                return False
            except ValidationError as e:
                logger.error(f"[{job_id}] JSON config file validation failed: Schema mismatch: {e.message}", exc_info=True)
                return False
            except Exception as e:
                logger.error(f"[{job_id}] JSON config file validation failed due to unexpected error: {e}", exc_info=True)
                return False
        elif file_type == "text/plain":
            try:
                # For plain text, assume it might contain a single integer for grid_resolution
                content_str = file_content.decode('utf-8').strip()
                if content_str.isdigit() and int(content_str) > 0:
                    logger.info(f"[{job_id}] Plain text file validation successful: Contains a valid integer.")
                    return True
                else:
                    logger.error(f"[{job_id}] Plain text file validation failed: Content is not a positive integer.")
                    return False
            except Exception as e:
                logger.error(f"[{job_id}] Plain text file validation failed due to unexpected error: {e}", exc_info=True)
                return False
        else:
            logger.warning(f"[{job_id}] Validation failed: Unsupported file type '{file_type}'.")
            return False

    def preprocess_geospatial_data(self, file_content: bytes, file_type: str, job_id: str, parameters: dict) -> tuple[bytes, str]:
        """
        Pre-processes geospatial data to extract relevant features and convert to a standardized JSON format.
        """
        logger.info(f"[{job_id}] Starting pre-processing for file type: {file_type}")
        preprocessed_metadata = {
            "job_id": job_id,
            "original_file_type": file_type,
            "timestamp": datetime.now().isoformat(),
            "extracted_parameters": {}
        }

        if file_type in ("image/tiff", "application/geotiff"):
            try:
                with rasterio.open(io.BytesIO(file_content)) as src:
                    preprocessed_metadata["extracted_parameters"] = {
                        "bounds": src.bounds._asdict(),
                        "width": src.width,
                        "height": src.height,
                        "resolution": src.res,
                        "crs": src.crs.to_wkt() if src.crs else None,
                        "nodata": src.nodata,
                        "count": src.count
                    }
                    if src.count > 0:
                        band1 = src.read(1)
                        if np.issubdtype(band1.dtype, np.number):
                            preprocessed_metadata["extracted_parameters"]["mean_value_band1"] = float(np.nanmean(band1)) # Use nanmean to handle nodata

                    if 'grid_resolution' not in parameters and src.width > 0 and src.height > 0:
                        # Example heuristic: use the smaller dimension divided by a factor
                        preprocessed_metadata["extracted_parameters"]["grid_resolution"] = max(1, min(src.width, src.height) // 5) 
                        logger.info(f"[{job_id}] Derived grid_resolution {preprocessed_metadata['extracted_parameters']['grid_resolution']} from GeoTIFF dimensions.")

                logger.info(f"[{job_id}] GeoTIFF pre-processing successful. Extracted metadata: {preprocessed_metadata['extracted_parameters']}")

            except RasterioIOError as e:
                logger.error(f"[{job_id}] GeoTIFF pre-processing failed due to RasterioIOError: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"[{job_id}] GeoTIFF pre-processing failed due to unexpected error: {e}", exc_info=True)

        elif file_type == "application/json":
            try:
                data = json.loads(file_content.decode('utf-8'))
                preprocessed_metadata["extracted_parameters"].update(data)
                logger.info(f"[{job_id}] Parsed JSON config file. Extracted parameters: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"[{job_id}] JSON config file pre-processing failed: Invalid JSON format: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"[{job_id}] Error processing JSON config file: {e}", exc_info=True)

        elif file_type == "text/plain":
            try:
                grid_res = int(file_content.decode('utf-8').strip())
                preprocessed_metadata["extracted_parameters"]["grid_resolution"] = grid_res
                logger.info(f"[{job_id}] Parsed plain text config file. Extracted grid_resolution: {grid_res}")
            except ValueError:
                logger.warning(f"[{job_id}] Could not parse plain text config file as integer. Content: '{file_content.decode('utf-8')[:50]}...'")
            except Exception as e:
                logger.error(f"[{job_id}] Error processing plain text config file: {e}", exc_info=True)

        elif file_type == "application/zip": # Shapefile
            # For shapefiles, pre-processing might involve extracting bounding box, feature count, etc.
            try:
                # Using geopandas to read the shapefile from bytes
                # geopandas.read_file can take a path to a zip or a file-like object
                # For in-memory zip, we need to use a virtual file system or save to temp
                # A simpler approach for metadata extraction without full file system interaction:
                with fiona.open(io.BytesIO(file_content)) as src:
                    bounds = src.bounds # (minx, miny, maxx, maxy)
                    preprocessed_metadata["extracted_parameters"]["bounds"] = {
                        "left": bounds[0], "bottom": bounds[1], "right": bounds[2], "top": bounds[3]
                    }
                    preprocessed_metadata["extracted_parameters"]["feature_count"] = len(src)
                    preprocessed_metadata["extracted_parameters"]["crs"] = src.crs.to_wkt() if src.crs else None
                    logger.info(f"[{job_id}] Shapefile pre-processing successful. Extracted metadata: {preprocessed_metadata['extracted_parameters']}")
            except Exception as e:
                logger.error(f"[{job_id}] Shapefile pre-processing failed: {e}", exc_info=True)

        else:
            logger.warning(f"[{job_id}] No specific pre-processing implemented for file type '{file_type}'. Returning generic metadata.")

        # Merge job parameters into extracted parameters, prioritizing extracted
        merged_parameters = {**parameters, **preprocessed_metadata["extracted_parameters"]}
        preprocessed_metadata["extracted_parameters"] = merged_parameters

        return json.dumps(preprocessed_metadata, indent=2).encode('utf-8'), "application/json"
