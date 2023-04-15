import os
import glob
from osgeo import gdal
import numpy as np
from scipy.ndimage import uniform_filter

def apply_mean_filter(input_file, output_file, filter_size, block_size=1024):
    print(f"Applying mean filter to {input_file} with filter size = {filter_size}...")

    # Open input raster
    src_ds = gdal.Open(input_file)
    src_band = src_ds.GetRasterBand(1)

    # Create output raster
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(output_file, src_ds.RasterXSize, src_ds.RasterYSize, 1, src_band.DataType)
    out_ds.SetGeoTransform(src_ds.GetGeoTransform())
    out_ds.SetProjection(src_ds.GetProjection())
    out_band = out_ds.GetRasterBand(1)

    # Process the raster in blocks
    for i in range(0, src_ds.RasterYSize, block_size):
        for j in range(0, src_ds.RasterXSize, block_size):
            # Calculate actual block size for edge blocks
            actual_block_size_x = min(block_size, src_ds.RasterXSize - j)
            actual_block_size_y = min(block_size, src_ds.RasterYSize - i)

            # Read input block
            src_data = src_band.ReadAsArray(j, i, actual_block_size_x, actual_block_size_y)

            if src_data is not None:
                # Pad the edge blocks with zeros
                padded_data = np.pad(src_data, ((0, block_size - src_data.shape[0]), (0, block_size - src_data.shape[1])), mode='constant')

                # Apply mean filter
                mean_filtered_data = uniform_filter(padded_data, size=filter_size)

                # Write mean filtered data to output raster
                out_band.WriteArray(mean_filtered_data[:src_data.shape[0], :src_data.shape[1]], j, i)

    out_band.FlushCache()

    # Close datasets
    out_ds = None
    src_ds = None

    print(f"Mean filter applied and saved to {output_file}.")


input_folder = "output_folder/blur-pre"
output_folder = "output_folder/blur-pre/post"
filter_size = 5  # Adjust the filter size as needed
block_size = 1024  # Adjust the block size as needed

# Iterate through all TIFF files in the input folder
input_files = glob.glob(os.path.join(input_folder, "*.tif"))

for input_file in input_files:
    file_name = os.path.basename(input_file)
    output_file = os.path.join(output_folder, f"mean_filtered_{file_name}")
    apply_mean_filter(input_file, output_file, filter_size, block_size)
