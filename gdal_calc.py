import os
from osgeo import gdal
from osgeo_utils import gdal_calc

def separate_rasters_by_color(input_file, output_folder, color_values):
    print("Separating rasters by color...")

    for color_value in color_values:
        output_file = os.path.join(output_folder, f"{color_value}_global.tif")
        print(f"Processing color value {color_value}")

        # Run gdal_calc to create a new raster with the specified color_value
        try:
            gdal_calc.Calc(
                calc="logical_and(A=={}, 1)".format(color_value),
                A=input_file,
                outfile=output_file,
                NoDataValue=0,
                format='GTiff',
                creation_options=['COMPRESS=LZW'],
                quiet=False
            )
            print(f"Successfully created raster for color value {color_value}")
        except Exception as e:
            print(f"Error creating raster for color value {color_value}: {e}")
