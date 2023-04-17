import os
import glob
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from gdal_calc import separate_rasters_by_color
from merge_rasters import polygonize_raster, generalize_vector, merge_shapefiles, apply_mean_filter, merge_rasters

def process_input_folder(input_folder, output_folder, color_values):
    global_raster_file = glob.glob(os.path.join(input_folder, "*.tif"))[0]

    # Step 1: Separate global landcover raster into separate rasters by class
    separate_rasters_by_color(global_raster_file, output_folder, color_values)

    # Step 2: Polygonize and generalize each class raster
    for color_value in color_values:
        color_file = os.path.join(output_folder, f"{color_value}_global.tif")
        blurred_output = os.path.join(output_folder, f"{color_value}_blurred.tif")
        shapefile_output = os.path.join(output_folder, f"{color_value}_polygonized.shp")
        generalized_output = os.path.join(output_folder, f"{color_value}_generalized.shp")

        # apply mean filter
        sigma = 2  # Adjust the filter size as needed
        block_size = 1024  # Adjust the block size as needed
        apply_mean_filter(color_file, blurred_output, sigma, block_size)

    # merge the forest rasters 
    input_files = [os.path.join(output_folder, f"{color}_blurred.tif") for color in color_values]
    merged_blurred_output = os.path.join(output_folder, "merged_raster_blurred.tif")
    merge_rasters(input_files, merged_blurred_output)

    # Calculate threshold value (half of the max value)
    with rasterio.open(merged_blurred_output) as src:
        max_value = src.read(1).max()
    threshold_value = max_value * 0.5

    # Threshold the merged raster
    thresholded_raster = os.path.join(output_folder, "thresholded_raster.tif")
    threshold_raster(merged_blurred_output, thresholded_raster, threshold_value)

    # Polygonize the thresholded raster
    polygonized_output = os.path.join(output_folder, "polygonized.shp")
    polygonize_raster(thresholded_raster, polygonized_output, 'value')

    # Generalize the polygonized shapefile
    # generalize_vector(shapefile_output, generalized_output, color_value)
    print("we are not generalizing the polygons any more")

    # Step 3: Merge all the generalized shapefiles into one output file
    merged_output_file = os.path.join(output_folder, "merged_output.shp")
    # merge_shapefiles(output_folder, merged_output_file, color_values)
    print("we are not merging the shapefiles any more")
