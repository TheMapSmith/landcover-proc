import os
import glob
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from separate_rasters import separate_rasters_by_color
from merge_rasters import simplify_and_generalize

def process_input_folder(input_folder, output_folder, color_values):
    global_raster_file = glob.glob(os.path.join(input_folder, "*.tif"))[0]

    # Step 1: Separate global landcover raster into separate rasters by class
    separate_rasters_by_color(global_raster_file, output_folder, color_values)

    # Step 2: Simplify and generalize each class raster
    for color_value in color_values:
        color_file = os.path.join(output_folder, f"{color_value}_global.tif")
        simplified_output_file = os.path.join(output_folder, f"{color_value}_simplified.tif")
        
        # Output each band raster to a TIF
        with open(color_file, "rb") as src_tif:
            with open(simplified_output_file, "wb") as dst_tif:
                dst_tif.write(src_tif.read())

        # Take the output TIF and pass it to the simplify function
        simplify_and_generalize(simplified_output_file, simplified_output_file)
