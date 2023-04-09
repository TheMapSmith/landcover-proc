import os
from osgeo import gdal, ogr, osr

def simplify_and_generalize(input_file, output_file):
    # Open the global file
    src_ds = gdal.Open(input_file)

    # Create an output shapefile
    shp_output_file = os.path.splitext(output_file)[0] + ".shp"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(shp_output_file)
    dst_layer = dst_ds.CreateLayer("polygonized", srs=osr.SpatialReference().ImportFromWkt(src_ds.GetProjection()))
    dst_layer.CreateField(ogr.FieldDefn("DN", ogr.OFTInteger))

    # Polygonize and simplify
    gdal.Polygonize(src_ds.GetRasterBand(1), None, dst_layer, 0, [], callback=None)
    dst_layer.SimplifyPreserveTopology(1.0)  # Adjust the simplification factor to control the degree of simplification

    # Clean up
    src_ds, dst_ds = None, None