# Dataset Hydrogeological Units in Mexico Basin
This dataset contains Hydrogeological Sections created with Python and Qgis in the Mexico Basin.

## Tabla de Contenidos
1. [Installation](#installation)
2. [Usage](#usage)
3. [Project Structure](#project-structure)
4. [LICENSE](#license)
5. [Contact](#contact)

## Installation

  ### Clone the repository
  git clone https://github.com/Nauj29/Mexico_Basin.git

  ### Navigate to the project directory
  cd Mexico_Basin

  ### Install the dependencies
  pip install -r requirements.txt

## Usage
  This dataset is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. It can be used for academic and research purposes only. Commercial use is not allowed without prior permission from the authors.

  ### Python Script for Creating Topographic Sections
  The `Sections.py` script extracts elevation data along designated lines and produces topographic profiles from a Digital Elevation Model (DEM) and specified line shapefiles.

  ### How to use
  This script can be used directly or as a library.

    1. **Set Input Paths**: Modify the paths in the script to point to your input shapefile and DEM file.
    2. **Run the Script**: Execute the script using Python.
       ```bash
       python Sections.py```
	   
  ### Python Script for Compute Azimuth and Dip direction
  The `Azimuth.py` script computes Azimuth and Dip direction of Faults from Shapefile type line.

  ### How to use
  This script can be used directly or as a library.

    1. **Set Input Paths**: Modify the path in the script to point to your input shapefile.
    2. **Run the Script**: Execute the script using Python.
       ```bash
       Azimuth.py```

## Project Structure
  ```plaintext
  Mexico_Basin/
  │
  ├── Graphics_and_sources/      # Images and geological charts used as inputs and figures in the paper
  ├── Hydrogeological_Units/
  │   ├── lineal/               # Line shapefiles for hydrogeological units
  │   ├── Polygon/              # Polygon shapefiles for hydrogeological units
  │
  ├── Surface/                  # Surface-related data or shapefiles
  ├── Topography/               # DEM or topography data
  │
  ├── Sections.py               # Python script for processing sections
  ├── Azimuth.py                 # Python script for compute Azimut and Dip_direction
  ├── README.md                 # Instructions file
  ├── requirements.txt          # Project dependencies
  ├── LICENSE                   # File License

  ```
## LICENSE
  Creative Commons Attribution 4.0 International License

  You are free to:
  - Share — copy and redistribute the material in any medium or format
  - Adapt — remix, transform, and build upon the material

  Under the following terms:
  - Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses   you or your use. [DOI:10.5281/zenodo.13852434](https://doi.org/10.5281/zenodo.13852434)


## Contact
jcmontanoc@comunidad.unam.mx

