# import stuff
###############################################################################
import csv
import os
###############################################################################
import numpy as np
from scipy.spatial import cKDTree as KDTree
###############################################################################
from osgeo import gdal
import osgeo.osr as osr
###############################################################################
from Tkinter import Tk
from tkFileDialog import askdirectory
from glob import glob
##############################################################################

'''FUNCTIONS'''

##############################################################################

def select_directory():
    '''
    User is prompted to select folder
    '''
    Tk().withdraw()
    folder = askdirectory()
    return folder
	
##############################################################################

def read_topcat_data(in_file):
    '''
    Reformat ToPCAT output
    '''
    with open(in_file, 'r') as fp:
        x, y, z = [], [], []
        reader = csv.reader(fp, delimiter =',')
        row = next(reader) #skip header
        for row in reader:
            a, b, c = [i for i in row]
            a=float(a[1:])
            b=float(b)
            c=float(c[:-1])
            x.append(a)
            y.append(b)
            z.append(c)
    fp.close()
    return x,y,z
	
##############################################################################

def define_dem_extent(input_array):
    dem_extent = []
    dem_extent.append(np.floor(min(input_array[0])))
    dem_extent.append(np.ceil(max(input_array[0])))
    dem_extent.append(np.floor(min(input_array[1])))
    dem_extent.append(np.ceil(max(input_array[1])))
    dem_extent = tuple(dem_extent)
    data1 = {}  
    data1['extent'] = dem_extent   
    data1['x']=input_array[0]
    data1['y']=input_array[1]
    data1['z']=input_array[2]  
    del input_array
    print 'finished importing points'
    return data1

##############################################################################

def get_raster_size(minx, miny, maxx, maxy, cell_width, cell_height):
    """
    Determine the number of rows/columns given the bounds of the point data and the desired cell size
    """
    cols = int((maxx - minx) / cell_width)
    rows = int((maxy - miny) / abs(cell_height))
    return cols, rows

##############################################################################

def get_spatial_reference(epsg_code):
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg_code)
    return srs

##############################################################################

def create_raster(grid_x, grid_y, grid_z, geotransform, proj, cols,rows,driverName,outFile):
    grid_z[np.isinf(grid_z)] = -99
    grid_z[grid_z>1000] = -99
    driver = gdal.GetDriverByName(driverName)
    print outFile
    ds = driver.Create(outFile, cols, rows, 1, gdal.GDT_Float32)
    if proj is not None:  
        ds.SetProjection(proj.ExportToWkt())
    ds.SetGeoTransform(geotransform)
    z_band = ds.GetRasterBand(1)
    z_band.WriteArray(grid_z)
    z_band.SetNoDataValue(-99)
    z_band.FlushCache()
    z_band.ComputeStatistics(False)
    del ds
    del z_band


##############################################################################
##############################################################################
#get the list of files
fnames = glob(r'C:\Users\Rebecca Rossi\Desktop\GC\Working_Data\sfm_working\photoscan_outputs\4_ToPCAT_inputs'+r'\*zmin.txt')

#loop througn the list of files
for i in fnames:
    # select input directory
#    in_directory = r'C:\Users\Rebecca Rossi\Desktop\GC\Working_Data\sfm_working\photoscan_outputs\4_ToPCAT_inputs'
#    #    in_directory = select_directory()
#    in_directory_string = str(in_directory)
#    in_name = '213L_1repeat_3gcps_CANUPO_zmin.txt'
#    in_file = in_directory_string + os.sep + in_name
#    in_file = os.path.normpath(in_file)
    #Build Dem name
    n = i.split('\\')[-1].split('_')
    dem_name = 'r'+n[0]+'_'+n[2]+'.tif'
    
    print 'In flie is %s' %(i,)

    in_file = i
    x, y, z = read_topcat_data(in_file)
    
    # build x, y, z array
    input_array = np.array((x,y,z),dtype=float)
    
    
    # aquire dem extent information
    data = define_dem_extent(input_array)
    
    # Nearest Neighbor
    # define dem extents
    xMin, xMax, yMin, yMax = [i for i in data['extent']]
    xMin = xMin + 0.5
    xMax = xMax + 0.5
    yMin = yMin + 0.5
    yMax = yMax + 0.5
    
    # specify cell resolution
    res = 1.0
    
    grid_x, grid_y = np.meshgrid(np.arange(xMin, xMax, res), np.arange(yMin,yMax, res))
    
    ## db begin changes
    tree = KDTree(zip(x, y))
    
    d, i = tree.query(zip(grid_x.ravel(), grid_y.ravel()), k=1) # distance_upper_bound=1)
    grid_z = np.asarray(z).flatten()[i].reshape(np.shape(grid_x))
    
    # specify a threshold distance for masking
    thres_dist = 1.0
    
    # mask out areas too far away from a nearest point
    grid_z[d.reshape(np.shape(grid_x)) > thres_dist] = np.nan
    grid_z = np.flipud(grid_z)
    
    ## db end changes
    
    # create raster
    driverName= 'GTiff'
    epsg_code = 26949
    proj = get_spatial_reference(epsg_code)
    outFile = os.path.normpath(os.path.join('C:\\','Users','Rebecca Rossi','Desktop','GC','Working_Data','sfm_working','photoscan_outputs', '5_DEM_outputs',dem_name))
    cols, rows = get_raster_size(xMin,yMin,xMax,yMax,res,res)
    geotransform =[xMin,res,0,yMax,0,-res]    
    create_raster(grid_x, grid_y, grid_z, geotransform, proj, cols,rows,driverName,outFile)
    
