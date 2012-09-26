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

#Desired states
listStates = ['AC', 'AM', 'AP', 'MA', 'MT', 'PA', 'RO', 'RR', 'TO']

#Desired classes
listClasses = ['FLORESTA', 'HIDROGRAFIA']

#Loop in list of desired states
for desState in listStates:

    #Loop in list of desired classes
    for desClass in listClasses:

        #Set the name to be openned
        fileName = "/home/eduardo/ShapeFiles/PRODES/estados/PDigital2000_2011_"+desState+"_shp/PDigital2011_"+desState+"_pol.shp"

        #Opens the shapefile and test the openning procedure
        origFile = ogr.Open(fileName)
        if origFile is None:
            print "Open failed.\n"
            print fileName
            sys.exit(1)

        #Set the new file to be written (initially a copy of the original)
        destName = "/home/eduardo/ShapeFiles/PRODES/estados/PDigital2000_2011_"+desState+"_shp/new/"+desClass+"_PDigital2011_"+desState+"_pol.shp"
        driveName = "ESRI Shapefile"
        driver = ogr.GetDriverByName(driveName)
        if driver is None:
            print "Driver not available!\n"
            sys.exit(1)
        destFile = driver.CopyDataSource(origFile,destName)

        #Close file
        origFile = None

        #Informs the user
        print "File copied..."
        print ""

        #Reads the layer
        layer = destFile.GetLayer()
        print "Name of the layer: ", layer.GetName()
        print ""

        #Reads the layer definition
        layer_def = layer.GetLayerDefn()

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
            classFeature = feature.GetFieldAsString(6)
            if classFeature == desClass:
                counter = counter + 1
            else:
                lfid = feature.GetFID()
                errorCode = layer.DeleteFeature(lfid)
                if errorCode != 0:
                    print "Error deleting feature.\n"
                    sys.exit(1)
            feature.Destroy()
        print "Number of new features: ", counter

        #Repack SQL
        destFile.ExecuteSQL("REPACK " + layer.GetName())

        #Close file
        destFile = None

#Program ends correctly
sys.exit(0)

