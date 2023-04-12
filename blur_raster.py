import os
import glob
from osgeo import gdal
import numpy as np
from scipy.ndimage import gaussian_filter

def apply_gaussian_blur(input_file, output_file, sigma, block_size=512):
    print(f"Applying Gaussian blur to {input_file} with sigma = {sigma}...")

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
            # Read input block
            src_data = src_band.ReadAsArray(j, i, block_size, block_size)

            # Apply Gaussian blur
            blurred_data = gaussian_filter(src_data, sigma=sigma)

            # Write blurred data to output raster
            out_band.WriteArray(blurred_data, j, i)

    out_band.FlushCache()

    # Close datasets
    out_ds = None
    src_ds = None

    print(f"Gaussian blur applied and saved to {output_file}.")

input_folder = "output_folder/blur-pre"
output_folder = "output_folder/blur-pre/post"
sigma = 2  # Adjust the sigma value as needed

# Iterate through all TIFF files in the input folder
input_files = glob.glob(os.path.join(input_folder, "*.tif"))

for input_file in input_files:
    file_name = os.path.basename(input_file)
    output_file = os.path.join(output_folder, f"blurred_{file_name}")
    apply_gaussian_blur(input_file, output_file, sigma)
