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

# Purpose:
# This script compares files from a directory to those contemplated
# in a specific mapfile. If the file is not in the mapfile it creates
# a unique name based on the filename and add a new layer in the end
# of the mapfile

import os
import sys
import shutil
from optparse import OptionParser
from osgeo import osr, gdal

def getRasterLocation(fname):
    """
    To map the location of a raster image to an unique identifier

    :arg string fname: The name of the file
    :returns: A unique ID for the location
    :rtype: string
    """
    pointLoc = fname.find(".")
    locationTemp = fname[0:pointLoc]
    if locationTemp == "AERONET_Rio_Branco":
        location = "a"
    elif locationTemp == "FAS_Brazil1":
        location = "b"
    elif locationTemp == "FAS_Brazil3":
        location = "c"
    elif locationTemp == "FAS_Brazil6":
        location = "d"
    elif locationTemp == "FAS_Brazil7":
        location = "e"
    elif locationTemp == "Peru":
        location = "f"
    return location

def getRasterMonth(fname):
    """
    To map the month (in Julian days) to a string (for raster files)

    :arg string fname: The name of the file
    :returns: The month of the image
    :rtype: string
    """
    pointLoc = fname.find(".")
    monthTemp = fname[pointLoc+5:pointLoc+8]
    if monthTemp == "031":
        month = "jan"
    elif monthTemp == "059" or monthTemp == "060":
        month = "feb"
    elif monthTemp == "090" or monthTemp == "091":
        month = "mar"
    elif monthTemp == "120" or monthTemp == "121":
        month = "apr"
    elif monthTemp == "151" or monthTemp == "152":
        month = "may"
    elif monthTemp == "181" or monthTemp == "182":
        month = "jun"
    elif monthTemp == "212" or monthTemp == "213":
        month = "jul"
    elif monthTemp == "243" or monthTemp == "244":
        month = "aug"
    elif monthTemp == "273" or monthTemp == "274":
        month = "sep"
    elif monthTemp == "304" or monthTemp == "305":
        month = "oct"
    elif monthTemp == "334" or monthTemp == "335":
        month = "nov"
    elif monthTemp == "365" or monthTemp == "366":
        month = "dec"
    return month

def writeRasterLayer(linesNew,lastLine,path,fname,nameLayer):
    """
    Add a new layer for the new raster image

    :arg list linesNew: A list of lines from the mapfile 
    :arg int lastLine: The number of lines in the mapfile
    :arg string path: The path for the new raster file
    :arg string fname: The name of the image file
    :arg string nameLayer: The unique name for the layer

    :returns: Nothing
    """
    linesNew.insert(lastLine,    "\n  LAYER")
    linesNew.insert(lastLine+1,  "\n    NAME \""+nameLayer+"\"")
    linesNew.insert(lastLine+2,  "\n    DATA \""+path+fname+"\"")
    linesNew.insert(lastLine+3,  "\n    TYPE RASTER")
    linesNew.insert(lastLine+4,  "\n    STATUS ON")
    linesNew.insert(lastLine+5,  "\n    METADATA")
    linesNew.insert(lastLine+6,  "\n      \"wfs_title\"          \"Amazon Image\"")
    linesNew.insert(lastLine+7,  "\n      \"wfs_srs\"            \"EPSG:4326\"")
    linesNew.insert(lastLine+8,  "\n      \"gml_include_items\"  \"all\"")
    linesNew.insert(lastLine+9,  "\n      \"gml_featureid\"      \"ID\"")
    linesNew.insert(lastLine+10, "\n      \"ows_enable_request\" \"*\"")
    linesNew.insert(lastLine+11, "\n    END")
    linesNew.insert(lastLine+12, "\n  END\n")
    return

def getShapeMonth(fname):
    """
    To map the month to a string (for shape files)

    :arg string fname: The name of the shapefile
    :returns: The month of the shapefile
    :rtype: string
    """
    pointLoc = fname.find("_")
    monthTemp = fname[pointLoc+5:pointLoc+7]
    if monthTemp == "01":
        month = "jan"
    elif monthTemp == "02":
        month = "feb"
    elif monthTemp == "03":
        month = "mar"
    elif monthTemp == "04":
        month = "apr"
    elif monthTemp == "05":
        month = "may"
    elif monthTemp == "06":
        month = "jun"
    elif monthTemp == "07":
        month = "jul"
    elif monthTemp == "08":
        month = "aug"
    elif monthTemp == "09":
        month = "sep"
    elif monthTemp == "10":
        month = "oct"
    elif monthTemp == "11":
        month = "nov"
    elif monthTemp == "12":
        month = "dec"
    return month

def writeShapeLayer(linesNew,lastLine,path,fname,nameLayer):
    """
    Add a new layer for the new shapefile

    :arg list linesNew: A list of lines from the mapfile 
    :arg int lastLine: The number of lines in the mapfile
    :arg string path: The path for the new shapefile
    :arg string fname: The name of the shapefile
    :arg string nameLayer: The unique name for the layer

    :returns: Nothing
    """
    linesNew.insert(lastLine,    "\n  LAYER")
    linesNew.insert(lastLine+1,  "\n    NAME \""+nameLayer+"\"")
    linesNew.insert(lastLine+2,  "\n    METADATA")
    linesNew.insert(lastLine+3,  "\n      \"wfs_title\"          \"Amazon Cloud\"")
    linesNew.insert(lastLine+4,  "\n      \"wfs_srs\"            \"EPSG:4326\"")
    linesNew.insert(lastLine+5,  "\n      \"gml_include_items\"  \"all\"")
    linesNew.insert(lastLine+6,  "\n      \"gml_featureid\"      \"ID\"")
    linesNew.insert(lastLine+7,  "\n      \"ows_enable_request\" \"*\"")
    linesNew.insert(lastLine+8,  "\n    END")
    linesNew.insert(lastLine+9,  "\n    TYPE POLYGON")
    linesNew.insert(lastLine+10, "\n    STATUS ON")
    linesNew.insert(lastLine+11, "\n    DATA \""+path+fname+"\"")
    linesNew.insert(lastLine+12, "\n    PROJECTION")
    linesNew.insert(lastLine+13, "\n      \"init=epsg:4326\"")
    linesNew.insert(lastLine+14, "\n    END")
    linesNew.insert(lastLine+15, "\n    CLASS")
    linesNew.insert(lastLine+16, "\n      NAME \"Amazon\"")
    linesNew.insert(lastLine+17, "\n      STYLE")
    linesNew.insert(lastLine+18, "\n        COLOR 255 128 128")
    linesNew.insert(lastLine+19, "\n        OUTLINECOLOR 96 96 96")
    linesNew.insert(lastLine+20, "\n      END")
    linesNew.insert(lastLine+21, "\n    END")
    linesNew.insert(lastLine+22, "\n  END\n")
    return

def readFile(origFile):
    """
    Reads the original mapfile and creates copies of it in the memory

    :arg string origFile: The name of the original mapfile
    :returns: Copies of the original file in plain text and as a list of lines
    :rtype list:
    """
    inFile = open(origFile,"r")
    textOrig = inFile.read()
    inFile.seek(0)
    linesOrig = inFile.readlines()
    inFile.close()
    return textOrig, linesOrig

def writeFile(origfile, linesNew):
    """
    Write down the new map file while creates a backup copy

    :arg string origFile: The name of the original mapfile
    :arg list linesNew: The lines for the new map file with new layers
    :returns: The name of the new filemap
    :rtype string:
    """
    shutil.copy(origFile, origFile+"~")
    newFileName = origFile
    outfile = open(newFileName, "w")
    outfile.write("".join(linesNew))
    outfile.close()
    return newFileName

def searchAndAddNewLayer(path, textOrig, linesOrig):
    """
    Main function for searching and adding a new layer

    :arg string path: The path for the new file (raster or shapefile)
    :arg string textOrig: The original plain text of the mapfile
    :arg list linesOrig: The original text of the mapfile as a list of lines
    :returns: If a new layer was added
    :rtype bool:
    """
    #So far, no new layers exists
    newLayer = False

    #Create a copy to build the new mapfile
    linesNew = linesOrig

    #Get the number of lines in the original file
    lastLine = len(linesOrig)

    #Get a list of the files in the directory
    dirList = os.listdir(path)

    #For each file in the directory
    for fname in dirList:
        
        #Let's only look for tif, geotif or shp files
        if fname[-4:] == '.tif' or fname[-7:] == '.geotif' or fname[-4:] == '.shp':
            
            #Set the filename as the search parameter
            search = fname
            
            #Search in the original mapfile
            index = textOrig.find(search)
            
            #If the file name is not found in the original file
            if index == -1:

                # A new raster image ou shapefile is detected
                newLayer = True

                #Building an unique ID for the name of the layer
                #First for shapefiles
                if fname[-4:] == '.shp':
                    #Let's warn the user
                    print "New Shapefile file detected:", fname

                    #For shape files it's based on year and month
                    pointLoc = fname.find("_")
                    year = fname[pointLoc+1:pointLoc+5]
                    month = getShapeMonth(fname)
                    nameLayer = "shp_cld_"+month+year

                    #Get the last line of the new map file
                    lastLine = len(linesNew)
                
                    #Append the new layer in the new file
                    writeShapeLayer(linesNew,lastLine-2,path,fname,nameLayer)

                #Then for raster images
                else:
                    #Let's warn the user
                    print "New GeoTIFF file detected:", fname            

                    #Get info from the raster image using GDAL (NOT BEING USED SO FAR)
                    projection, width, height = getRasterInfo(path, fname)

                    #For raster images it's based on the location of the image, year and month
                    location = getRasterLocation(fname)
                    pointLoc = fname.find(".")
                    year = fname[pointLoc+1:pointLoc+5]
                    month = getRasterMonth(fname)
                    nameLayer = month+year+location
                
                    #Get the last line of the new map file
                    lastLine = len(linesNew)
                
                    #Append the new layer in the new file
                    writeRasterLayer(linesNew,lastLine-2,path,fname,nameLayer)
    
    #Returns the info about finding a new layer
    return newLayer, linesNew

def getRasterInfo(path, fname):
    """
    Get projection and size information from the raster image

    :arg string path: The path for the raster file
    :arg string fname: The name of the raster file
    :returns: The DATUM, width and height of the image
    :rtype list:
    """
    image = gdal.Open(path+fname)
    width = image.RasterXSize
    height = image.RasterYSize
    projTemp = image.GetProjection()
    datum = projTemp.find('DATUM')
    projection = projTemp[datum+7:31]
    return projection, width, height

def checkProjection(projection):
    """
    Raises a warning if the projection is not the desired one

    :arg string projection: Projection of the file
    :returns: Print on screen
    """
    desiredProj = "WGS_1984"
    if projection != desiredProj:
        print "\nWARNING!!! Projection of this file is not WGS_1984.\n\n"
    return

#######################
# Begin of the script #
#######################

if __name__ == "__main__":

    # Arguments for the application
    usage = "usage: %prog arg1 arg2"
    parser = OptionParser(usage)

    parser.add_option("-f", "--file", dest="origFile", help="Name of the original map file", metavar="FILE")
    parser.add_option("-p", "--path", dest="path", help="Directory containing the files (raster and/or shapefiles)", metavar="PATH")

    (options, args) = parser.parse_args()

    if options.origFile:
        origFile = options.origFile
    else:
        parser.error("You must supply the name of the original map file")

    if options.path:
        path = options.path
    else:
        parser.error("You must supply the path with the new images/shapefiles")

    #Let's get a mirror of the original file in the memory
    textOrig, linesOrig = readFile(origFile)

    #Search and add a new layer
    newLayer, linesNew = searchAndAddNewLayer(path, textOrig, linesOrig)

    # Write the new file if a new layer was inserted
    if newLayer:
        newMapFile = writeFile(origFile, linesNew)
        print "New mapfile written: ", newMapFile

#
#End of the script
#
