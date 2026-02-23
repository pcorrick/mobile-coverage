import os
import argparse
import subprocess
import json
from pathlib import Path
import re

def download():
    # === CONFIGURATION ===
    base_url = "https://6e867df0-tiles.spatialbuzz.net/tiles/opt_au-v060/styles/opt_au_v060_4g/"  # Base URL
    png_dir = Path("downloaded_png")           # Where PNG files go

    # === ENSURE OUTPUT DIRECTORIES EXIST ===
    png_dir.mkdir(parents=True, exist_ok=True)

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
            tile_fn = f"{z}_{x}_{y}"

            png_path = png_dir / f"{tile_fn}.png"

            full_url = base_url + f"{z}/{x}/{y}.png"

            # Download PBF if not already present
            if not png_path.exists():
                print(f"📥 Downloading: {full_url}")
                try:
                    subprocess.run(["wget", "-q", "-O", str(png_path), full_url], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to download {full_url} with exit code {e.returncode}")
                    continue

            else:
                print(f"✅ Already downloaded: {png_path}")


def main():

    download()

if __name__ == "__main__":
    main()
