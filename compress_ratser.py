import os
from osgeo import gdal

def compress_raster(input_file, output_file):
    print(f"Compressing {input_file} to {output_file} using LZW compression...")

    # Open input raster
    src_ds = gdal.Open(input_file)

    # Compress raster using LZW compression
    compressed_ds = gdal.Translate(output_file, src_ds,
                                   options=gdal.TranslateOptions(creationOptions=["COMPRESS=LZW"]))

    # Close datasets
    compressed_ds = None
    src_ds = None

    print("Compression complete.")

input_file = "source_folder/landcover_resampled_100km.tif"
output_file = "input_folder/landcover_compressed_100km.tif"

compress_raster(input_file, output_file)