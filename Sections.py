import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import LineString
from pyproj import CRS
import os

# Define the Coordinate Reference System (CRS) using Well-Known Text (WKT)
def get_crs_custom():
    """
    Defines the custom CRS for generating topographic sections.
    Returns:
        CRS object: Custom CRS defined using WKT.
    """
    crs_wkt = """PROJCS["WGS_1984_ARC_System_Zone_01",
        GEOGCS["WGS 84",
        DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
        AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
        AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
        PROJECTION["Equirectangular"],
        PARAMETER["standard_parallel_1",22.94791772],
        PARAMETER["central_meridian",0],
        PARAMETER["false_easting",0],
        PARAMETER["false_northing",0],
        UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
        AXIS["Easting",EAST],
        AXIS["Northing",NORTH],
        AUTHORITY["ESRI","102421"]]"""
    return CRS.from_wkt(crs_wkt)

# Load the DEM (Digital Elevation Model)
def load_dem(dem_path):
    """
    Loads a DEM file and retrieves its array, transform, and resolution.

    Args:
        dem_path (str): Path to the DEM file.

    Returns:
        tuple: DEM array, transform, and pixel resolution.
    """
    with rasterio.open(dem_path) as dem_src:
        dem_transform = dem_src.transform
        dem_array = dem_src.read(1)
        dem_resolution = dem_transform[0]  # Pixel resolution (assumes square pixels)
    return dem_array, dem_transform, dem_resolution

# Extract elevations along a line from the DEM
def extract_elevations(line, dem_array, transform, dem_resolution):
    """
    Extracts elevation values along a line geometry from a DEM.

    Args:
        line (LineString): Line geometry.
        dem_array (ndarray): DEM data array.
        transform (Affine): Transformation matrix of the DEM.
        dem_resolution (float): Pixel resolution of the DEM.

    Returns:
        tuple: Distances and corresponding elevation values.
    """
    elevations = []
    distances = []

    # Calculate the number of points along the line based on resolution
    line_length = line.length
    num_points = int(np.ceil(line_length / dem_resolution))
    segment_length = line_length / (num_points - 1) if num_points > 1 else 0

    for i in range(num_points):
        point = line.interpolate(segment_length * i)  # Interpolate points along the line
        x, y = point.x, point.y

        # Convert geographic coordinates to raster indices
        col, row = ~transform * (x, y)
        row, col = int(round(row)), int(round(col))

        # Check if the point is within DEM bounds
        if 0 <= row < dem_array.shape[0] and 0 <= col < dem_array.shape[1]:
            elev = dem_array[row, col]
            elevations.append(elev)

            # Calculate cumulative distances
            if i == 0:
                distances.append(0)
            else:
                prev_point = line.interpolate(segment_length * (i - 1))
                prev_x, prev_y = prev_point.x, prev_point.y
                dist = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                distances.append(distances[-1] + dist)
        else:
            elevations.append(np.nan)  # Assign NaN for points outside DEM bounds
            distances.append(distances[-1] if distances else 0)

    return distances, elevations

# Process shapefile and generate topographic profiles
def process_profiles(shapefile_path, dem_path, output_dir):
    """
    Generates topographic profiles from input shapefile and DEM.

    Args:
        shapefile_path (str): Path to the shapefile containing line geometries.
        dem_path (str): Path to the DEM file.
        output_dir (str): Directory to save the generated profiles.
    """
    # Load custom CRS and DEM data
    crs_custom = get_crs_custom()
    dem_array, dem_transform, dem_resolution = load_dem(dem_path)
    gdf = gpd.read_file(shapefile_path)  # Load shapefile

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through each line in the shapefile
    for idx, row in gdf.iterrows():
        line = row.geometry
        if isinstance(line, LineString):
            distances, elevations = extract_elevations(line, dem_array, dem_transform, dem_resolution)

            # Prepare X, Y coordinates for profile
            x_coords = distances
            y_coords = elevations
            line_points = [(x, y) for x, y in zip(x_coords, y_coords) if not np.isnan(y)]

            # Get start and end points for profile closure
            x_start, y_start = line_points[0]
            x_end, y_end = line_points[-1]

            bottom = -2000  # Baseline elevation for profile closure

            # Add points to close the profile polygon
            line_points.extend([
                (x_end, bottom),
                (x_start, bottom),
                (x_start, y_start)
            ])

            # Create profile geometry
            profile_line = LineString(line_points)

            # Extract profile name from shapefile attribute
            profile_name = row['name']

            # Create GeoDataFrame to store profile
            profile_gdf = gpd.GeoDataFrame({
                'id': [idx],
                'name': [profile_name],
                'distance': [distances[-1] if distances else None],
                'elevation': [elevations[-1] if elevations else None],
                'geometry': [profile_line]
            }, geometry='geometry', crs=crs_custom)

            # Save the profile as a shapefile
            output_path = os.path.join(output_dir, f'{profile_name}.shp')
            profile_gdf.to_file(output_path)

            print(f"Profile {profile_name} generated with {len(line_points)} points.")

# Main script execution
if __name__ == "__main__":
    shapefile_path = 'Surface/Sections.shp'  # Input shapefile
    dem_path = 'Raster/cdmx.tif'  # Input DEM
    output_dir = 'Topography' # cambiar despues a topography # Directory to save profiles
    process_profiles(shapefile_path, dem_path, output_dir)
