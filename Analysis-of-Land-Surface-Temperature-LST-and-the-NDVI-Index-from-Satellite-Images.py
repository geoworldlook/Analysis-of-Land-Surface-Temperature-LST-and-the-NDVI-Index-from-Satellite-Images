import arcpy
import numpy as np
from matplotlib import pyplot as plt

# Setting up the work environment and loading raster files
arcpy.env.workspace = r"C:\Users\User\Documents\ArcGIS\Projects\MyProject9\MyProject9.gdb"
raster_files = {
    'B4': r'C:\Users\User\Desktop\Mapa\LC08_L1TP_191022_20200815_20200919_02_T1_B4.tif',
    'B5': r'C:\Users\User\Desktop\Mapa\LC08_L1TP_191022_20200815_20200919_02_T1_B5.tif',
    'B10': r'C:\Users\User\Desktop\Mapa\LC08_L1TP_191022_20200815_20200919_02_T1_B10.tif'
}
numpy_rasters = {band: arcpy.RasterToNumPyArray(arcpy.Raster(file), nodata_to_value=0) for band, file in raster_files.items()}

# Loading values from the metadata file
metadata_values = {}
keys = [
    'RADIANCE_MULT_BAND_10', 'RADIANCE_MULT_BAND_4', 'RADIANCE_MULT_BAND_5',
    'RADIANCE_ADD_BAND_10', 'RADIANCE_ADD_BAND_4', 'RADIANCE_ADD_BAND_5',
    'K1_CONSTANT_BAND_10', 'K2_CONSTANT_BAND_10', 'CORNER_LL_PROJECTION_X_PRODUCT',
    'CORNER_LL_PROJECTION_Y_PRODUCT', 'UTM_ZONE'
]

with open(r'C:\Users\User\Desktop\Mapa\LC08_L1TP_191022_20200815_20200919_02_T1_MTL.txt') as MTL:
    for line in MTL:
        key, _, value = line.partition("=")
        key = key.strip()
        if key in keys:
            metadata_values[key] = float(value)

# TOA calculations and TOA correction to brightness temperature
TOA_band_10 = metadata_values['RADIANCE_MULT_BAND_10'] * numpy_rasters['B10'] + metadata_values['RADIANCE_ADD_BAND_10']
BT = (metadata_values['K2_CONSTANT_BAND_10'] / np.log((metadata_values['K1_CONSTANT_BAND_10'] / TOA_band_10) + 1)) - 273.15

# NDVI calculations
ndvi_numerator = numpy_rasters['B5'] - numpy_rasters['B4']
ndvi_denominator = numpy_rasters['B5'] + numpy_rasters['B4']
NDVI = np.where(ndvi_denominator == 0, 0, ndvi_numerator / ndvi_denominator)

# Vegetation proportion and emissivity
P_v = np.sqrt((NDVI - np.min(NDVI)) / (np.max(NDVI) - np.min(NDVI)))
E = 0.004 * P_v + 0.986

# Surface temperature
LST = (BT / (1 + (0.00115 * BT / 1.4388) * np.log(E)))

# Removing nodata values and conversion from numpy to raster
point = arcpy.Point(metadata_values['CORNER_LL_PROJECTION_X_PRODUCT'], metadata_values['CORNER_LL_PROJECTION_Y_PRODUCT'])
LST_raster = arcpy.NumPyArrayToRaster(np.where(LST < -100, -60, LST), point, 30, 30, value_to_nodata=-60)
LST_raster.save("E:\mapa\est15.tif")

print("END")
