import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import LineString
from pyproj import CRS
import os

# Defining CRS using WKT
def get_crs_custom():
    '''Definition of the Georeferencing System for Sections Generation '''
    crs_wkt = (
        'PROJCS["WGS_1984_ARC_System_Zone_01",'
        'GEOGCS["WGS 84",'
        'DATUM["WGS_1984",'
        'SPHEROID["WGS 84",6378137,298.257223563,'
        'AUTHORITY["EPSG","7030"]],'
        'AUTHORITY["EPSG","6326"]],'
        'PRIMEM["Greenwich",0,'
        'AUTHORITY["EPSG","8901"]],'
        'UNIT["degree",0.0174532925199433,'
        'AUTHORITY["EPSG","9122"]],'
        'AUTHORITY["EPSG","4326"]],'
        'PROJECTION["Equirectangular"],'
        'PARAMETER["standard_parallel_1",22.94791772],'
        'PARAMETER["central_meridian",0],'
        'PARAMETER["false_easting",0],'
        'PARAMETER["false_northing",0],'
        'UNIT["metre",1,'
        'AUTHORITY["EPSG","9001"]],'
        'AXIS["Easting",EAST],'
        'AXIS["Northing",NORTH],'
        'AUTHORITY["ESRI","102421"]]'
    )
    return CRS.from_string(crs_wkt)

def load_dem(dem_path):
    '''Function to Load DEM'''

    with rasterio.open(dem_path) as dem_src:
        dem_transform = dem_src.transform
        dem_array = dem_src.read(1)
        dem_resolution = dem_transform[0]
    return dem_array, dem_transform, dem_resolution

def extract_elevations(line, dem_array, transform, dem_resolution):
    '''Fuction to extract elevations'''

    elevations = []
    distances = []
    
    line_length = line.length
    num_points = int(np.ceil(line_length / dem_resolution))
    segment_length = line_length / (num_points - 1) if num_points > 1 else 0
    
    for i in range(num_points):
        point = line.interpolate(segment_length * i)
        x, y = point.x, point.y
        
        col, row = ~transform * (x, y)
        row, col = int(round(row)), int(round(col))
        
        if 0 <= row < dem_array.shape[0] and 0 <= col < dem_array.shape[1]:
            elev = dem_array[row, col]
            elevations.append(elev)
            
            if i == 0:
                distances.append(0)
            else:
                prev_point = line.interpolate(segment_length * (i - 1))
                prev_x, prev_y = prev_point.x, prev_point.y
                dist = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                distances.append(distances[-1] + dist)
        else:
            elevations.append(np.nan)
            distances.append(distances[-1] if distances else 0)
    
    return distances, elevations

def process_profiles(shapefile_path, dem_path, output_dir):
    '''Fuction to create topographic sections'''

    crs_custom = get_crs_custom()
    dem_array, dem_transform, dem_resolution = load_dem(dem_path)
    gdf = gpd.read_file(shapefile_path)

    os.makedirs(output_dir, exist_ok=True)

    for idx, row in gdf.iterrows():
        line = row.geometry
        if isinstance(line, LineString):
            distances, elevations = extract_elevations(line, dem_array, dem_transform, dem_resolution)
            
            # Create X,Y coordinates for sections
            x_coords = distances
            y_coords = elevations
            
            # Crear coordenadas X, Y
            line_points = [(x, y) for x, y in zip(x_coords, y_coords) if not np.isnan(y)]

            # Get the start and end points
            x_start, y_start = line_points[0]
            x_end, y_end = line_points[-1]

            bottom = -2000
            
            # Add the extra points
            line_points.extend([
                (x_end, bottom),
                (x_start, bottom),
                (x_start, y_start)
            ])

            # Create line geometry with X, Y coordinates
            profile_line = LineString(line_points)

            # Get profile name from 'name' attribute
            profile_name = row['name']  
            
            # Create a GeoDataFrame to store the profile
            profile_gdf = gpd.GeoDataFrame({
                'id': [idx],
                'name': [profile_name],
                'distance': [distances[-1] if distances else None],
                'elevation': [elevations[-1] if elevations else None],
                'geometry': [profile_line]
            }, geometry='geometry', crs=crs_custom)
            
            # Save the shapefile
            output_path = os.path.join(output_dir, f'{profile_name}.shp')
            profile_gdf.to_file(output_path)
            
            print(f"Perfil {profile_name} generado con {len(line_points)} puntos.")

if __name__ == "__main__":
    shapefile_path = r'E:\UNAM\Doctorado\4_semestre\Gempy\Metodologia\Gemgis\prueba1\Perfiles.shp'
    dem_path = r'E:\UNAM\Doctorado\4_semestre\Gempy\Metodologia\Gemgis\Planta\cdmx.tif'
    output_dir = r'E:\UNAM\Doctorado\4_semestre\Gempy\Metodologia\Gemgis\Perfiles'
    process_profiles(shapefile_path, dem_path, output_dir)
