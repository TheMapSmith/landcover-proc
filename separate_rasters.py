import os
import numpy as np
from osgeo import gdal

def separate_rasters_by_color(input_file, output_folder, color_values):
    print("Separating rasters by color...")

    # Open the input raster file
    src_ds = gdal.Open(input_file)
    src_band = src_ds.GetRasterBand(1)
    x_size, y_size = src_ds.RasterXSize, src_ds.RasterYSize

    # Define block size and number of blocks
    block_size = 1024
    n_blocks_x = int(np.ceil(x_size / block_size))
    n_blocks_y = int(np.ceil(y_size / block_size))

    # Create an empty array for each output raster
    output_rasters = {}
    for color_value in color_values:
        output_rasters[color_value] = np.zeros((y_size, x_size), dtype=np.uint8)

    # Loop through the raster in blocks
    for i in range(n_blocks_x):
        for j in range(n_blocks_y):
            x_start = i * block_size
            y_start = j * block_size

            x_block_size = min(block_size, x_size - x_start)
            y_block_size = min(block_size, y_size - y_start)

            src_array = src_band.ReadAsArray(x_start, y_start, x_block_size, y_block_size)

            for color_value in color_values:
                mask = np.where(src_array == color_value, 1, 0).astype(np.uint8)
                output_rasters[color_value][y_start:y_start+y_block_size, x_start:x_start+x_block_size] = mask

    # Save the output rasters
    for color_value in color_values:
        print(f"Processing color value: {color_value}")

        output_file = os.path.join(output_folder, f"{color_value}_global.tif")
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(output_file, x_size, y_size, 1, gdal.GDT_Byte)

        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
        dst_ds.SetProjection(src_ds.GetProjection())

        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(output_rasters[color_value])

        # Clean up
        dst_band, dst_ds = None, None

    # Clean up
    src_band, src_ds = None, None
    print("Separation of rasters by color complete.")