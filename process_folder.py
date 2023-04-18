import os
import glob
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from gdal_calc import separate_rasters_by_color
import rasterio
from merge_rasters import polygonize_raster, generalize_vector, merge_shapefiles, apply_mean_filter, merge_rasters, threshold_raster

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
    forest_values= [111, 113, 112, 114, 115, 116, 121, 123, 122, 124, 125, 126]
    input_files = [os.path.join(output_folder, f"{color}_blurred.tif") for color in forest_values]
    merged_blurred_output = os.path.join(output_folder, "forest_blurred.tif")
    merge_rasters(input_files, output_folder, merged_blurred_output)

    # Color values that need thresholding
    threshold_colors = [20, 30, 90, 100, 60, 40, 50, 70, 80, 200]
    threshold_colors.append("forest")  # Adding the merged forest raster

    # Apply threshold_raster for each color value
    for color in threshold_colors:
        input_file = os.path.join(output_folder, f"{color}_blurred.tif")
        output_file = os.path.join(output_folder, f"{color}_thresholded.tif")
        threshold_raster(input_file, output_file)

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
