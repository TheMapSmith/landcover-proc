import os
import numpy as np
from osgeo import gdal

def separate_rasters_by_color(input_file, output_folder, color_values, resampling_factor=1):
    print("Separating rasters by color...")
    try:
        # Open the input raster file
        src_ds = gdal.Open(input_file)
        src_band = src_ds.GetRasterBand(1)
        x_size, y_size = src_ds.RasterXSize, src_ds.RasterYSize
        print(f"Input raster dimensions: {x_size} x {y_size}")

        # Define resampled dimensions
        x_resampled_size = int(x_size / resampling_factor)
        y_resampled_size = int(y_size / resampling_factor)

        # Define block size and number of blocks
        block_size = 1024
        n_blocks_x = int(np.ceil(x_resampled_size / block_size))
        n_blocks_y = int(np.ceil(y_resampled_size / block_size))

        # Create output rasters
        output_rasters = {}
        for color_value in color_values:
            output_file = os.path.join(output_folder, f"{color_value}_global.tif")
            driver = gdal.GetDriverByName("GTiff")
            dst_ds = driver.Create(output_file, x_resampled_size, y_resampled_size, 1, gdal.GDT_Float32, options=['COMPRESS=LZW'])
            dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
            dst_ds.SetProjection(src_ds.GetProjection())
            output_rasters[color_value] = dst_ds.GetRasterBand(1)
            output_rasters[color_value].SetNoDataValue(np.nan)

        # Loop through the raster in blocks
        for i in range(n_blocks_x):
            for j in range(n_blocks_y):
                print(f"Processing block: {i}, {j}")
                x_start = i * block_size * resampling_factor
                y_start = j * block_size * resampling_factor

                x_block_size = min(block_size * resampling_factor, x_size - x_start)
                y_block_size = min(block_size * resampling_factor, y_size - y_start)

                src_array = src_band.ReadAsArray(x_start, y_start, x_block_size, y_block_size)

                if resampling_factor > 1:
                    src_array = src_array[::resampling_factor, ::resampling_factor]

                for color_value in color_values:
                    mask = np.where(src_array == color_value, color_value, np.nan).astype(np.float32)
                    output_rasters[color_value].WriteArray(mask, x_start // resampling_factor, y_start // resampling_factor)

        # Clean up
        for color_value in output_rasters:
            output_rasters[color_value] = None

        src_band, src_ds = None, None
        print("Separation of rasters by color complete.")

    except Exception as e:
        print(f"Error occurred during processing: {e}")
