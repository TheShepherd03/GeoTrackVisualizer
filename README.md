# GeoTrack Visualizer

A desktop application for visualizing geospatial tracking data with interactive features for exploring TIFF maps and GeoJSON point data.

![GeoTrack Visualizer Screenshot](screenshots/app_screenshot.png)

## Features

- **Interactive Map Visualization**: Display TIFF maps with GeoJSON point overlays
- **Directional Indicators**: Show bearing arrows for each tracking point based on "TN Bearing" attribute
- **Interactive Data Exploration**: Click on points to view all attributes, hover for quick info
- **Multiple Map Styles**: Choose between Default, Terrain, and Satellite visualization styles
- **Dark/Light Mode**: Toggle between dark and light themes for comfortable viewing
- **Attribute Table**: View all point data in a sortable, searchable table
- **Coordinate Reprojection**: Automatic handling of different coordinate systems

## Requirements

- Python 3.8+
- PyQt5
- Matplotlib
- Geopandas
- Rasterio
- NumPy

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/geotrack-visualizer.git
   cd geotrack-visualizer
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Click on the "Historical Tracking" button to start.

3. Select your TIFF and GeoJSON files when prompted.

4. Explore the data:
   - Use the toolbar to pan, zoom, and navigate the map
   - Click on points to see detailed attribute information
   - Hover over points to see quick tooltips
   - Use the table to view and sort all data points
   - Try different map styles from the dropdown menu
   - Toggle dark mode for comfortable viewing in low-light environments

## Data Format

### GeoJSON Requirements
The application expects GeoJSON files with point features. For directional indicators to work, each point should have a "TN Bearing" attribute that specifies the bearing in degrees.

Example GeoJSON structure:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [31.994103, -27.664135]
      },
      "properties": {
        "Signal Strength": 0.161,
        "Altitude": 323.1,
        "Date & Time": "20-11-2024 17:40:35",
        "Frequency": 148.034,
        "TN Bearing": 66.625
      }
    }
  ]
}
```

### TIFF Requirements
The application supports both single-band (grayscale) and RGB TIFF files. For best results, use georeferenced TIFF files with proper coordinate system information.

## Project Structure

- `main.py`: Main application code
- `requirements.txt`: Python dependencies
- `icons/`: Application icons
- `settings/`: Configuration files
- `screenshots/`: Application screenshots
- `data/`: Example data files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
