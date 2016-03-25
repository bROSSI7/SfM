###########################################################################################

# DEM MASK: CREATE POLYGON MASK OF DEM BOUNDARY USING GDAL, OGR AND NUMPY
# Becca Rossi

###########################################################################################

# Utah State University
# Department of Watershed Sciences
# Ecogeomorphology and Topographic Analysis Laboratory

###########################################################################################

# Import stuff
import os

from osgeo import gdal
from osgeo import ogr
import osgeo.osr as osr
from osgeo.gdalnumeric import *  
from osgeo.gdalconst import *  

import numpy as np

###########################################################################################

# DIVIDE THE ARRAY BY ITSELF TO ASSIGN DEM DATA CELLS WITH A VALUE OF 1.
# Replace * w/ user defined inputs

# Set working directory
os.chdir(r'*')

# SfM DEM input file DEM_in
DEMin = 'SfM.tif'

# DEM output file
DEMout = 'temp.tif'

# Open the DEM dataset
ds = gdal.Open(DEMin)

# Get DEM band
band = ds.GetRasterBand(1)

# Read the data into numpy array
array = BandReadAsArray(band)

# Divide the array by itself to assign DEM data cells with a value of 1
divArray = np.divide(array, array)

###########################################################################################

# WRITE NEW DEM FROM NUMPY ARRAY
# Note: gdal.Polygonize requires a raster input; would be better to input the array in memory directly to gdal.Polygonize

# Get gdal driver
driver = gdal.GetDriverByName("GTiff")

# Define DEM_out
outDatasource = driver.Create(DEMout, ds.RasterXSize, ds.RasterYSize, 1, band.DataType)

# Copy DEM_in dataset info to DEM_out
CopyDatasetInfo(ds,outDatasource)

# Define DEM_out band
bandOut = outDatasource.GetRasterBand(1)

# Write array to DEM_out band
BandWriteArray(bandOut, divArray)

# CLOSE:
band = None  
ds = None  
bandOut = None  
outDatasource = None

###########################################################################################

# GDAL.POLYGONIZE

# Set spatial reference
srs = osr.SpatialReference()
srs.ImportFromEPSG(26949)

# Re-open DEM_out
sourceRaster = gdal.Open(DEMout)

# Get raster band
band = sourceRaster.GetRasterBand(1)

# Read band in as an array
bandArray = band.ReadAsArray()

# Define output shapefile name
outShapefile = 'polygonized'

# Define driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# Delete shapefile if it already exists
if os.path.exists(outShapefile + '.shp'):
    driver.DeleteDataSource(outShapefile + '.shp')

# Create polygonized.shp
outDatasource = driver.CreateDataSource(outShapefile + '.shp')
outLayer = outDatasource.CreateLayer('polygonized', srs)

# Assign new field to attribute areas of data = 1
newField = ogr.FieldDefn('maskValue', ogr.OFTInteger)
outLayer.CreateField(newField)

# Polygonize DEMout
gdal.Polygonize(band, None, outLayer, 0, [], callback=None)

outDatasource.Destroy()
sourceRaster = None

###########################################################################################

# Create DEM mask from attribute selection

# Define in datasource
inDatasource = ogr.Open('polygonized.shp')

# Define in layer
inLayer = inDatasource.GetLayer()

# Select all values of 1 in the maskValue attribute field
inLayer.SetAttributeFilter('maskValue = 1')

# Define driver
driver = ogr.GetDriverByName('ESRI Shapefile')

# Define outdatasource
outDatasource = driver.CreateDataSource('SfM_mask.shp')

# Define outlayer
outLayer = outDatasource.CopyLayer(inLayer, 'SfM.mask')

# DELETE:
del inLayer, inDatasource, outLayer, outDatasource

###########################################################################################