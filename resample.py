import os
from osgeo import gdal

def resample_raster(input_file, output_file, resolution):
    print(f"Resampling {input_file} to {output_file} with {resolution}m resolution using majority resampling method...")

    # Open input raster
    src_ds = gdal.Open(input_file)

    # Calculate new dimensions based on the target resolution
    src_gt = src_ds.GetGeoTransform()
    width = int((src_gt[1] * src_ds.RasterXSize) / resolution)
    height = int((src_gt[5] * src_ds.RasterYSize) / abs(resolution))

    # Resample raster using majority resampling method
    resampling_method = gdal.GRA_Mode
    resampled_ds = gdal.Warp(output_file, src_ds,
                             width=width,
                             height=height,
                             resampleAlg=resampling_method,
                             options=["COMPRESS=LZW"])

    # Close datasets
    resampled_ds = None
    src_ds = None

    print("Resampling complete.")

input_file = "source_folder/PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
output_file = "input_folder/landcover_resampled_30km.tif"
resolution = 30000  # 30km resolution

resample_raster(input_file, output_file, resolution)
