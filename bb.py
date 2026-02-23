import os
from pathlib import Path
from PIL import Image
import mercantile
import subprocess

# ----------------- CONFIGURATION ------------------
tiles_folder = "./tiles"  # folder with your PNG tiles
output_folder = "./output"  # where to save georeferenced GeoTIFFs
os.makedirs(output_folder, exist_ok=True)

# ----------------- PROCESS ------------------
# Loop through all PNG tiles
for png_file in Path(tiles_folder).glob("*.png"):
    # Extract z, x, y from filename assuming z_x_y.png
    filename = png_file.stem  # no extension
    try:
        z, x, y = map(int, filename.split("_"))
    except ValueError:
        print(f"⚠️ Skipping invalid file name: {png_file.name}")
        continue

    # Get bounding box in WGS84
    bbox = mercantile.bounds(x, y, z)  # west, south, east, north
    west, south, east, north = bbox.west, bbox.south, bbox.east, bbox.north

    # Verify tile dimensions
    with Image.open(png_file) as img:
        width, height = img.size

    print(f"🗺️ Processing {png_file.name}: {west:.5f}, {south:.5f}, {east:.5f}, {north:.5f}")

    # Build output file name
    output_tif = Path(output_folder) / f"{z}_{x}_{y}.tif"

    # GDAL translate command to georeference and convert to GeoTIFF
    cmd = [
        "gdal_translate",
        "-of", "GTiff",
        "-a_ullr", str(west), str(north), str(east), str(south),
        "-a_srs", "EPSG:4326",
        str(png_file),
        str(output_tif)
    ]

    # Run the command
    subprocess.run(cmd, check=True)

print("✅ Done georeferencing all tiles!")
