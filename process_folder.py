import os
import glob
from config import forest_values
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from gdal_calc import separate_rasters_by_color
import rasterio
from merge_rasters import polygonize_raster, generalize_vector, merge_shapefiles, apply_mean_filter, merge_rasters, threshold_raster, remove_isolated_pixels

def process_input_folder(input_folder, output_folder, color_values, forest_values):
    global_raster_file = glob.glob(os.path.join(input_folder, "*.tif"))[0]

    # Step 2: Separate all color values into separate rasters
    separate_rasters_by_color(global_raster_file, output_folder, color_values)

    # Step 3: Merge forest color values into single raster
    forest_raster_files = [os.path.join(output_folder, f"{color}_global.tif") for color in forest_values]
    merged_forest_output = "forest_global.tif"
    merge_rasters(forest_raster_files, output_folder, merged_forest_output)

    # Step 4: Blur all files (landcover colors and the merged forest color layer)
    for color_value in color_values:
        if color_value in forest_values:
            input_file = os.path.join(output_folder, "forest_global.tif")
        else:
            input_file = os.path.join(output_folder, f"{color_value}_global.tif")

        output_file = os.path.join(output_folder, f"{color_value}_blurred.tif")
        sigma = 1  # Adjust the filter size as needed
        block_size = 1024  # Adjust the block size as needed
        apply_mean_filter(input_file, output_file, sigma, block_size)

    # Step 5: Threshold all files (landcover colors and merged forest color)
    for color_value in color_values:
        input_file = os.path.join(output_folder, f"{color_value}_blurred.tif")
        output_file = os.path.join(output_folder, f"{color_value}_thresholded.tif")
        threshold_raster(input_file, output_file)

    # Step 6: Polygonize all files (landcover colors and merged forest color)
    for color_value in color_values:
        input_file = os.path.join(output_folder, f"{color_value}_thresholded.tif")
        output_file = os.path.join(output_folder, f"{color_value}_polygonized.shp")
        polygonize_raster(input_file, output_file, color_value)
