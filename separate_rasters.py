import os
import numpy as np
from osgeo import gdal

def separate_rasters_by_color(input_file, output_folder, color_values):
    print("Separating rasters by color...")

    # Open the input raster file
    src_ds = gdal.Open(input_file)
    src_band = src_ds.GetRasterBand(1)
    src_array = src_band.ReadAsArray()

    # Loop through each color value and create a new raster for that value
    for color_value in color_values:
        print(f"Processing color value: {color_value}")

        # Create a mask for the current color value
        mask = np.where(src_array == color_value, 1, 0).astype(np.uint8)

        # Create the output raster file
        output_file = os.path.join(output_folder, f"{color_value}_global.tif")
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(output_file, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)

        # Copy the geotransform and projection from the source raster
        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
        dst_ds.SetProjection(src_ds.GetProjection())

        # Write the mask data to the output raster
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(mask)

        # Clean up
        dst_band, dst_ds = None, None

    # Clean up
    src_band, src_ds = None, None
    print("Separation of rasters by color complete.")
