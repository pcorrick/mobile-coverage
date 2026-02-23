import os
import argparse
import subprocess
import json
from pathlib import Path
import re

def download(token):
    # === CONFIGURATION ===
    # url_file = "tile-urls-z7.txt"            # Input URL list
    base_url = "https://services.gcm.telstra.com.au/arcgis/rest/services/Hosted/Mob_4g_hh/VectorTileServer/tile/"  # Base URL for PBF files
    output_dir = Path("output_geojsons")       # Where individual GeoJSONs go
    pbf_dir = Path("downloaded_pbf")           # Where PBF files go

    # === ENSURE OUTPUT DIRECTORIES EXIST ===
    output_dir.mkdir(parents=True, exist_ok=True)
    pbf_dir.mkdir(parents=True, exist_ok=True)

    # Define the zoom and range for x and y coordinates
    z = 8
    x_min = 208
    y_min = 138

    x_max = 220
    y_max = 155


    # === PROCESS EACH TILE ===
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            # Construct the URL for each tile
            tile_fn = f"{z}_{y}_{x}"

            pbf_path = pbf_dir / f"{tile_fn}.pbf"
            geojson_path = output_dir / f"{tile_fn}.geojson"

            full_url = base_url + f"{z}/{y}/{x}.pbf"  + f"?token={token}"

            # Download PBF if not already present
            if not pbf_path.exists():
                print(f"📥 Downloading: {full_url}")
                try:
                    subprocess.run(["wget", "-q", "-O", str(pbf_path), full_url], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to download {full_url} with exit code {e.returncode}")
                    continue

                # check if the file is empty
                if os.path.getsize(pbf_path) > 0:
                    convertPbf(pbf_path, geojson_path, z, y, x)
                else:
                    os.remove(pbf_path)
            else:
                print(f"✅ Already downloaded: {pbf_path}")



def convertPbf(pbf_path, geojson_path, z, y, x):
        layer_name = "retail_4g_hh_700"          # Set your layer name here
        merged_geojson = Path("merged.geojson")    # Output merged file

        # Convert PBF to GeoJSON
        print(f"🌐 Converting {pbf_path} to GeoJSON...")
        try:
            with open(geojson_path, "w") as out_f:
                subprocess.run(
                    ["vt2geojson", "--layer", layer_name, str(pbf_path),"-z", str(z), "-x", str(x), "-y", str(y)],
                    stdout=out_f,
                    check=True
                )
        except subprocess.CalledProcessError:
            print(f"❌ vt2geojson failed for {pbf_path}")

        features = []

        # Load and collect features
        with open(geojson_path) as f:
            gj = json.load(f)
            features.extend(gj.get("features", []))

        # === WRITE GEOJSON FILE ===
        print(f"📝 Writing GeoJSON: {geojson_path}")
        with open(geojson_path, "w") as f:
            json.dump({
                "type": "FeatureCollection",
                "features": features
            }, f)


        # === WRITE MERGED FILE ===
        #print(f"📝 Writing merged GeoJSON: {merged_geojson}")
        #with open(merged_geojson, "w") as f:
        #    json.dump({
        #        "type": "FeatureCollection",
        #        "features": features
        #    }, f)

        #print("✅ Done! Merged file created.")

def main():
    # === ARGUMENT PARSER ===
    parser = argparse.ArgumentParser("Telstra-PBF-Downloader")
    parser.add_argument("token", help="Token from Telstra site")
    args = parser.parse_args()

    if args.token == "":
        print("Error: No token provided.")
        sys.exit(1)

    download(args.token)

if __name__ == "__main__":
    main()