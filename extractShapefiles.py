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

import sys
import ogr

#Desired class
#desClass = 'HIDROGRAFIA'
desClass = 'FLORESTA'

#Desired state
desState = 'TO'

#Set the name to be openned
fileName = "/home/eduardo/ShapeFiles/PRODES/estados/PDigital2000_2011_"+desState+"_shp/PDigital2011_"+desState+"_pol.shp"

#Opens the shapefile and test the openning procedure
shapeFile = ogr.Open(fileName)
if shapeFile is None:
    print "Open failed.\n"
    sys.exit(1)

#Set the new file to be written (initially a copy of the original)
destName = "/home/eduardo/ShapeFiles/PRODES/estados/PDigital2000_2011_"+desState+"_shp/new/"+desClass+"_PDigital2011_"+desState+"__pol.shp"
driveName = "ESRI Shapefile"
driver = ogr.GetDriverByName(driveName)
if driver is None:
    print "Driver not available!\n"
    sys.exit(1)
dest = driver.CopyDataSource(shapeFile,destName)

#Close all and save
shapeFile = None
dest = None

#Informs the user
print "File copied..."
print ""

#Open the new file for removal
shapeFile = ogr.Open(destName,2)

#Reads the layer
layer = shapeFile.GetLayer()
print "Name of the layer: ", layer.GetName()
print ""

#Reads the layer definition
layer_def = layer.GetLayerDefn()
#print layer_def

#Get the fields names
field_names = [layer_def.GetFieldDefn(i).GetName() for i in range (layer_def.GetFieldCount())]
print "Field names available: ", field_names
print ""

#Get the number of features
numberFeatures = layer.GetFeatureCount()
print "Number of features :", numberFeatures
print ""

#Let's count the number of desired features
counter = 0
for i in range(numberFeatures):
    feature = layer.GetNextFeature()
    if feature['mainclass'] == desClass:
        counter = counter + 1
    else:
        layer.DeleteFeature(i)
print "Number of new features: ", counter

#Close things
shapeFile = None
dest = None
