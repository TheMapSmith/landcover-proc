import os
from osgeo import gdal, ogr, osr
import numpy as np
import rasterio
from rasterio.merge import merge
import cv2
from scipy import ndimage

def remove_isolated_pixels(input_file, output_file, filter_size):
    with rasterio.open(input_file) as src:
        src_data = src.read(1)
        src_profile = src.profile

    filtered_data = ndimage.median_filter(src_data, size=filter_size)

    with rasterio.open(output_file, 'w', **src_profile) as dst:
        dst.write(filtered_data, 1)

def threshold_raster(input_file, output_file):
    with rasterio.open(input_file) as src:
        src_data = src.read(1)
        max_value = src.read(1).max()
        threshold_value = max_value * 0.25

        # Threshold the raster
        thresholded_data = np.where(src_data >= threshold_value, src_data, src.nodata)

        # Save the thresholded raster
        profile = src.profile
        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(thresholded_data, 1)


def merge_rasters(input_files, output_folder, output_file):
    print("Merging rasters...")

    output_file_path = os.path.join(output_folder, output_file)

    # Set NoData value to a variable, for example, -9999
    nodata_value = -9999

    # Read the first raster and initialize an array to store the sum
    ds = gdal.Open(input_files[0])
    sum_array = ds.ReadAsArray().astype(np.float32)
    sum_array[sum_array == 0] = np.nan
    geotransform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    ds = None

    # Iterate over the rest of the rasters and add their values to the sum_array
    for input_file in input_files[1:]:
        ds = gdal.Open(input_file)
        data_array = ds.ReadAsArray().astype(np.float32)
        data_array[data_array == 0] = np.nan
        sum_array = np.nansum([sum_array, data_array], axis=0)
        ds = None

    # Replace NaN values with the NoData value
    sum_array[np.isnan(sum_array)] = nodata_value

    # Create the output raster file and write the sum_array
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(output_file_path, sum_array.shape[1], sum_array.shape[0], 1, gdal.GDT_Float32)
    out_ds.SetGeoTransform(geotransform)
    out_ds.SetProjection(projection)
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(nodata_value)
    out_band.WriteArray(sum_array)

    out_band.FlushCache()
    out_ds = None

    print("Merging rasters complete.")

def custom_gaussian_filter(in_array, ksize, sigma):
    blurred_array = cv2.GaussianBlur(in_array, (ksize, ksize), sigma)
    return blurred_array



def apply_mean_filter(input_file, output_file, sigma, no_data_value=0):
    print(f"Applying Gaussian filter to {input_file} with sigma = {sigma}...")

    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist.")
        return

    # Open input raster
    with rasterio.open(input_file) as src_ds:
        src_band = src_ds.read(1)  # Add this line to define src_band

        if src_band is not None:
            # Replace NoData values with NaN
            src_data_nan = src_band.astype(np.float32)
            src_data_nan[src_data_nan == no_data_value] = np.nan

            # Apply custom Gaussian filter
            ksize = int(16 * sigma) + 1
            gaussian_filtered_data = custom_gaussian_filter(src_data_nan, ksize=ksize, sigma=sigma)

            # Replace NaN values with NoData values
            gaussian_filtered_data[np.isnan(gaussian_filtered_data)] = no_data_value

            # Write filtered data to output raster
            profile = src_ds.profile.copy()
            profile.update(dtype=rasterio.float32)

            with rasterio.open(output_file, 'w', **profile) as out_ds:
                out_ds.write(gaussian_filtered_data, 1)

    print(f"Mean filter applied and saved to {output_file}.")




def polygonize_raster(input_file, output_file, color_value):
    print(f"Polygonizing raster: {input_file}")

    src_ds = gdal.Open(input_file)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(src_ds.GetProjection())

    dst_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(output_file)
    dst_layer = dst_ds.CreateLayer("polygonized", srs=srs)
    dst_layer.CreateField(ogr.FieldDefn("DN", ogr.OFTInteger))
    dst_layer.CreateField(ogr.FieldDefn("Color", ogr.OFTInteger))  # Add a new field for the color attribute

    src_band = src_ds.GetRasterBand(1)
    mask_band = src_band.GetMaskBand()

    gdal.Polygonize(src_band, mask_band, dst_layer, 0, [], callback=None)

    # Set the color attribute for each feature
    feature = dst_layer.GetNextFeature()
    while feature:
        feature.SetField("Color", color_value)
        dst_layer.SetFeature(feature)
        feature = dst_layer.GetNextFeature()

    src_ds, dst_ds = None, None
    print(f"Polygonization of raster {input_file} complete.")


def merge_shapefiles(input_folder, output_file, color_values):
    print("Merging shapefiles...")

    driver = ogr.GetDriverByName("ESRI Shapefile")
    srs = None
    dst_ds = driver.CreateDataSource(output_file)
    dst_layer = None

    for color_value in color_values:
        input_file = os.path.join(input_folder, f"{color_value}_generalized.shp")
        src_ds = ogr.Open(input_file)

        if src_ds is not None:
            src_layer = src_ds.GetLayer(0)
            if srs is None:
                srs = src_layer.GetSpatialRef()
                dst_layer = dst_ds.CreateLayer("merged", srs=srs)
                # Copy fields from the source layer to the destination layer
                in_layer_defn = src_layer.GetLayerDefn()
                for i in range(in_layer_defn.GetFieldCount()):
                    field_defn = in_layer_defn.GetFieldDefn(i)
                    dst_layer.CreateField(field_defn)

            # Copy features from the source layer to the destination layer
            for feature in src_layer:
                dst_layer.CreateFeature(feature)
        else:
            print(f"Warning: Unable to open shapefile {input_file}")

    print("Shapefiles merged successfully.")



def generalize_vector(input_file, output_file, color_value):
    print(f"Generalizing vector: {input_file}")

    src_ds = ogr.Open(input_file)
    src_layer = src_ds.GetLayer()

    dst_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(output_file)
    dst_layer = dst_ds.CreateLayer("generalized", src_layer.GetSpatialRef())
    dst_layer.CreateField(ogr.FieldDefn("DN", ogr.OFTInteger))
    dst_layer.CreateField(ogr.FieldDefn("Color", ogr.OFTInteger))

    for feature in src_layer:
        geometry = feature.GetGeometryRef()
        simplified_geometry = geometry.SimplifyPreserveTopology(1.0)
        
        new_feature = ogr.Feature(dst_layer.GetLayerDefn())
        new_feature.SetField("DN", feature.GetField("DN"))
        new_feature.SetField("Color", feature.GetField("Color"))
        new_feature.SetGeometry(simplified_geometry)
        dst_layer.CreateFeature(new_feature)

    src_ds, dst_ds = None, None
    print(f"Generalization of vector {input_file} complete.")

