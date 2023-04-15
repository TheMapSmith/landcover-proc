import os
from osgeo import gdal

def resample_raster(input_file, output_file, target_resolution):
    # Open the input raster
    input_ds = gdal.Open(input_file)
    input_gt = input_ds.GetGeoTransform()

    # Calculate the new x and y resolution based on the target resolution
    xres = input_gt[1] * target_resolution
    yres = input_gt[5] * target_resolution

    # Resample raster using gdal.Warp()
    resample_alg = 'near'
    ds = gdal.Warp(output_file, input_file, xRes=xres, yRes=yres, resampleAlg=resample_alg)
    ds = None


input_file = "source_folder/PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
output_file = "input_folder/landcover_resampled_10km.tif"
target_resolution = 100  # 30km, adjust this value based on your desired resolution
resample_raster(input_file, output_file, target_resolution)
