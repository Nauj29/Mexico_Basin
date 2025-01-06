import geopandas as gpd
import math

def calculate_azimuth(line):
    """
    Calculates the azimuth of a line in degrees, measured clockwise from the north.

    Parameters:
        line (shapely.geometry.LineString): A LineString geometry representing the line.

    Returns:
        float: The azimuth angle in degrees (0-360°), or None if the geometry is invalid.
    """
    # Ensure the input geometry is of type LineString
    if line.geom_type == 'LineString':
        # Get the start and end coordinates of the line
        x1, y1 = line.coords[0]
        x2, y2 = line.coords[-1]
        
        # Compute the differences in the x and y coordinates
        dx = x2 - x1
        dy = y2 - y1
        
        # Calculate the azimuth in radians using atan2
        azimuth_rad = math.atan2(dy, dx)
        
        # Convert the azimuth to degrees
        azimuth_deg = math.degrees(azimuth_rad)
        
        # Adjust the azimuth to be measured from the north (clockwise)
        azimuth_deg = (90 - azimuth_deg) % 360
        
        return azimuth_deg
    return None  # Return None for invalid geometries

def calculate_dip_direction(azimuth, side_dip):
    """
    Determines the dip direction based on the azimuth and the side of the dip.

    Parameters:
        azimuth (float): The azimuth angle in degrees.
        side_dip (str): The side of the dip ('R' for right or 'L' for left).

    Returns:
        float: The dip direction in degrees (0-360°), or None if the input is invalid.
    """
    # Ensure the azimuth is valid
    if azimuth is None:
        return None

    # Adjust the azimuth based on the side of the dip
    if side_dip == 'R':  # Dip is on the right side
        dip_direction = (azimuth + 90) % 360
    elif side_dip == 'L':  # Dip is on the left side
        dip_direction = (azimuth - 90) % 360
    else:  # Invalid side_dip value
        dip_direction = None
    return dip_direction

def process_shapefile(input_shapefile):
    """
    Processes a shapefile to calculate and add azimuth and dip direction as new columns.

    Parameters:
        input_shapefile (str): The path to the input shapefile to be processed.

    Returns:
        None: Updates the input shapefile in place.
    """
    # Load the shapefile into a GeoDataFrame
    gdf = gpd.read_file(input_shapefile)

    # Check if the 'Side_Dip' field exists in the shapefile
    if 'Side_Dip' not in gdf.columns:
        print("The shapefile does not contain the 'Side_Dip' field.")
        return

    # Filter to include only LineString geometries
    gdf = gdf[gdf.geometry.geom_type == 'LineString']

    # Add a new column for azimuth, calculated for each geometry
    gdf['azimuth'] = gdf['geometry'].apply(lambda geom: calculate_azimuth(geom) if geom else None)

    # Add a new column for dip direction, calculated based on azimuth and 'Side_Dip'
    gdf['dip_direction'] = gdf.apply(
        lambda row: calculate_dip_direction(row['azimuth'], row['Side_Dip']) if row['azimuth'] is not None else None, 
        axis=1
    )

    # Save the updated GeoDataFrame back to the original shapefile
    gdf.to_file(input_shapefile)
    print(f"Shapefile updated with 'azimuth' and 'dip_direction' columns.")

# Main script execution
if __name__ == "__main__":
    # Specify the input shapefile path
    input_shapefile = "Surface/Faults.shp"  # Replace with the correct path to your shapefile
    
    # Process the shapefile to calculate and add azimuth and dip direction
    process_shapefile(input_shapefile)
