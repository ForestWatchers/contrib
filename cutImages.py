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

import os
from osgeo import ogr, osr, gdal

#Import easy to use xml parser called minidom (Ex.: http://www.travisglines.com/web-coding/python-xml-parser-tutorial):
from xml.dom.minidom import parseString

def getLatLon (nameFile):
    """
    Get Upper Left and Lower Right Latitude/Longitude from image

    :arg string nameFile: Name of the file to be analysed
    :returns: The width, height of the image and the lat/long position of the upper left and lower right corners
    :rtype float:
    """
    imageData = gdal.Open(nameFile)
    geoTransf = imageData.GetGeoTransform()
    width = imageData.RasterXSize
    height = imageData.RasterYSize
    minX = geoTransf[0]
    minY = geoTransf[3] + width*geoTransf[4] + height*geoTransf[5]
    maxX = geoTransf[0] + width*geoTransf[1] + height*geoTransf[2]
    maxY = geoTransf[3]
    return width, height, minX, maxX, minY, maxY

#Number of divisions
numDivX = 2
numDivY = 2

#Output directory
outputDir = '/home/eduardo/Testes/fw_img/cuts/'

#Image output type:
outputType = 'PNG'
outputExt = '.png'

#Directory to be processed
imageDir = '/home/eduardo/Testes/fw_img/test/'

#Get the name of every file in the directory
dirList = os.listdir(imageDir)

#For every file in directory
for fname in dirList:
  
    #Let's work only with GeoTIFF files
    if fname[-4:] == '.tif' or fname[-7:] == '.geotif':

        #Open the image
        imageFile = fname
        imageData = gdal.Open(imageDir+imageFile)

        #Geting info on projection
        proj = imageData.GetProjection()
        datum = proj.find('DATUM')
        print "Projection: ", proj[datum+7:31]

        #Calculating lat/long
        [width, height, minX, maxX, minY, maxY] = getLatLon(imageDir+imageFile)

        #Calculating size of sqares
        sizeSquareX = width / numDivX
        sizeSquareY = height / numDivY

        #Print info
        print "Size: ", width, height
        print ""
        print "Full projection info: ",  proj
        print ""
        print "Lat/Long for corners: "
        print "    Upper Left: ", minX, maxY
        print "    Lower Right",  maxX, minY
        print ""
        print "Size of each square: ", sizeSquareX, sizeSquareY
        print ""
        print ""

        #Create every square
        pixelXini = 0
        for itemX in range(numDivX):
            pixelYini = 0
            for itemY in range(numDivY):
                idSquare = 'Img_'+str(itemX)+'_'+str(itemY)
                outName = outputDir+idSquare+'_'+imageFile[0:-4]+outputExt
                print idSquare+': ', pixelXini, pixelYini
                cmd = 'gdal_translate -of '+outputType+' -srcwin '+str(pixelXini)+' '+str(pixelYini)+' '+str(sizeSquareX)+' '+str(sizeSquareY)+' '+imageDir+imageFile+' '+outName
                print cmd
                print ''
                os.system(cmd)
                pixelYini = pixelYini + sizeSquareY
                [widthCut, heightCut, minXcut, maxXcut, minYcut, maxYcut] = getLatLon(outName)
                print 'Upper Left: ', minXcut, maxYcut
                print 'Lower Right: ', maxXcut, minYcut
                print ''
            pixelXini = pixelXini + sizeSquareX
