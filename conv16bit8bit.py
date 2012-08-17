#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Instituto Nacional de Pesquisas Espaciais (INPE)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#Example: http://gis.stackexchange.com/questions/7377/rescale-raster-band-with-gdal-python-bindings

import gdal
from gdalconst import *
import numpy

#Opening file
fileName = '/home/eduardo/Testes/NASA/img.sur_refl_b06.tif'
dataset = gdal.Open(fileName, GA_ReadOnly)
if dataset is None:
    print 'Error opening file!'
    exit

#Creating copy
destinyName = '/home/eduardo/Testes/NASA/img.sur_refl_b06_8bit.tif'

#Getting dataset information
print 'Driver: ', dataset.GetDriver().ShortName,'/', \
      dataset.GetDriver().LongName
print 'Size is ', dataset.RasterXSize,'x',dataset.RasterYSize, \
      'x',dataset.RasterCount
print 'Projection is ', dataset.GetProjection()

geotransform = dataset.GetGeoTransform()
if not geotransform is None:
    print 'Origin = (', geotransform[0], ',', geotransform[3],')'
    print 'Pixel Size = (', geotransform[1], ',', geotransform[5],')'

#Fetching the Raster Bands
print 'Number of bands = ', dataset.RasterCount

#Cria o arquivo destino
driver = gdal.GetDriverByName("GTiff")
dest = driver.Create(destinyName, dataset.RasterXSize, \
    dataset.RasterYSize, dataset.RasterCount, gdal.GDT_Byte)

for item in range(dataset.RasterCount):
    band = dataset.GetRasterBand(item+1)
    print 'Band Type = ', gdal.GetDataTypeName(band.DataType)
    min = band.GetMinimum()
    max = band.GetMaximum()
    print 'data 1: ', min, max
    if min is None or max is None:
        (min,max) = band.ComputeRasterMinMax(1)
    print 'Min = %.3f, Max = %.3f' % (min,max)
    if band.GetOverviewCount() > 0:
        print 'Band has ', band.GetOverviewCount(), ' overviews.'
    if not band.GetRasterColorTable() is None:
        print 'Band has a color table with ', \
              band.GetRasterColorTable().GetCount(), ' entries.'
    rasterData = dataset.ReadAsArray(0,0,dataset.RasterXSize, dataset.RasterYSize)
    print rasterData
    print ''
    rasterData2 = numpy.clip(rasterData,0,rasterData.max())
    print rasterData2
    print ''
    #~ rasterDataTest = rasterData
    #~ rasterDataTest = rasterDataTest.astype(numpy.double)
    #~ rasterDataTest = rasterDataTest/10000.0
    #~ minTest = rasterDataTest.min()
    #~ maxTest = rasterDataTest.max()
    #~ rasterDataTest = ((255-0)*((rasterData-minTest)/(maxTest-minTest)))+0
    #~ rasterDataTest = rasterDataTest.astype(numpy.uint8)
    #~ print minTest, maxTest
    #~ print rasterDataTest
    #~ print rasterData
    min2 = float(rasterData2.min())
    max2 = float(rasterData2.max())
    print 'data 2: ', min2, max2
    rasterData2 = ((255-0)*((rasterData2-min2)/(max2-min2)))+0
    rasterData2 = rasterData2.astype(numpy.uint8)
    rasterData = ((255-0)*((rasterData-min)/(max-min)))+0
    rasterData = rasterData.astype(numpy.uint8)
    print rasterData2
    dest.GetRasterBand(item+1).WriteArray(rasterData2)
    #~ dest.GetRasterBand(item+1).ComputeStatistics(False)

dest.SetProjection(dataset.GetProjection())
dest.SetGeoTransform(dataset.GetGeoTransform())

#Only blue
#~ onlyBlue = 1
#~ if onlyBlue:
    #~ print "Let's play!"
    #~ for itemX in range(dataset.RasterXSize):
        #~ for itemY in range(dataset.RasterYSize):
            #~ if values[0][itemX][itemY] != 73:
                #~ values[0][itemX][itemY] = 0
                #~ #print 'Value change!'

#Printing some info
#print values[0][0][0], values[1][0][0], values[2][0][0]

#Set new values
#~ dest.GetRasterBand(1).WriteArray(values)

#Closing properly to write things down
dataset = None
dest = None

