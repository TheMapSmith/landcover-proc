import os
import sys
sys.path.append("rasterproc/Lib/site-packages")

from config import input_folder, output_folder, color_values
from process_folder import process_input_folder

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def main():
    # Step 1: Separate global landcover raster into separate rasters by class
    # Step 2: Simplify and generalize each class raster
    process_input_folder(input_folder, output_folder, all_color_values, forest_color_values)

if __name__ == "__main__":
    # Step 0: Start a multi-threaded parallel process
    main()