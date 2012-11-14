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

# Example: http://invisibleroads.com/tutorials/gdal-shapefile-points-save.html

import os
import sys
import ogr
import osr
import gdal
import json
import urllib2
from gdalconst import *
from optparse import OptionParser

def getAppId(server, appName):
    """
    Get the application id given the short name

    :arg string server: Address of the server
    :arg string appName: Short name of the application
    :returns: Numerical id of the application
    :rtype: integer
    """
    JSONdata = urllib2.urlopen(url=server+"/api/app?short_name="+ \
        appName).read()
    data = json.loads(JSONdata)
    appId = data[0]['id']
    return appId

def getTasks(server, appId, maxNumberTasks, completedOnly):
    """
    Get the tasks of a particular application from the server.

    :arg string server: Address of the server
    :arg string appId: ID of the application to be analysed
    :arg integer maxNumberTasks: Maximum number of tasks to be downloaded
    :arg int completedOnly: If we'll get only completed tasks
    :returns: Tasks info for the application
    :rtype: dictionary
    """
    if completedOnly == 1:
        JSONdata = urllib2.urlopen(url=server+"/api/task?app_id="+ \
            str(appId)+"&state=completed&limit="+ \
            str(maxNumberTasks)).read()
    else:
        JSONdata = urllib2.urlopen(url=server+"/api/task?app_id="+ \
            str(appId)+"&limit="+str(maxNumberTasks)).read()
    data = json.loads(JSONdata)
    numberTasks = len(data)
    tasksInfo = []
    for item in range(numberTasks):
        tasksInfo.append({'taskId':data[item]['id'], \
            'area':data[item]['info']['tile']['restrictedExtent']})
    return tasksInfo

def getResults(server, tasksInfo, maxNumberAnswers):
    """
    Get the results of a particular application from the server.

    :arg string server: Address of the server
    :arg integer maxNumberAnswers: Maximum number of answers per task to be downloaded
    :arg list tasksInfo: List of tasks
    :returns: Results for the application
    :rtype: dictionary
    """
    answersApp = []
    numberTasks = len(tasksInfo)
    for item in range(numberTasks):
        answersApp.append([])
        JSONdata = urllib2.urlopen(url=server+"/api/taskrun?task_id="+ \
            str(tasksInfo[item]['taskId'])+"&limit="+ \
            str(maxNumberAnswers)).read()
        data = json.loads(JSONdata)
        lenData = len(data)
        for ans in range(lenData):
            answersApp[item].append({'taskId':data[ans]['task_id'], \
            'id':data[ans]['id'], 'answer':data[ans]['info']['deforestedareas']})
    return answersApp

def generateShapefiles(data, destDir, printStats = 0):
    """
    Generates the shapefile with the polygons based on the results

    :arg list dict data: Dictionary list with all the results.
    :arg string destDir: Destination directory

    :returns: None
    """
    # Defing spacial reference
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

    # Creating the polygon shapefile
    destFilePoly = destDir+'deforestedAreasPoly.shp'
    if os.path.isfile(destFilePoly):
        os.remove(destFilePoly)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapeDataPoly = driver.CreateDataSource(destFilePoly)
    # Creating the polygon layer
    layerPoly = shapeDataPoly.CreateLayer('DeforestedAreasPoly', spatialReference, ogr.wkbPolygon)
    layerDefinitionPoly = layerPoly.GetLayerDefn()

    # Creating the point shapefile
    destFilePoint = destDir+'deforestedAreasPoint.shp'
    if os.path.isfile(destFilePoint):
        os.remove(destFilePoint)
    shapeDataPoint = driver.CreateDataSource(destFilePoint)
    # Creating the point layer
    layerPoint = shapeDataPoint.CreateLayer('DeforestedAreasPoint', spatialReference, ogr.wkbPoint)
    layerDefinitionPoint = layerPoint.GetLayerDefn()

    # Getting the number of tasks and the number of answers for each one
    numberTasks = len(data)
    for task in range(numberTasks):
        numberResults = len(data[task])
        if (numberResults > 0):
            print 'Task ', task, ' - Number results: ', numberResults
            for result in range(numberResults):
                if data[task][result]['answer'] == 'no-deforestation':
                    print '  No-deforestation in task', data[task][result]['id']
                else:
                    numberAnswers = len(data[task][result]['answer'])
                    print '  Number of features: ', numberAnswers
                    for answer in range(numberAnswers):
                        typeGeometry = data[task][result]['answer'][answer]['geometry']['type']
                        print '    Type of geometry: ', typeGeometry
                        if (typeGeometry == 'Polygon'):
                            outring = ogr.Geometry(ogr.wkbLinearRing)
                            pointsGeometry = data[task][result]['answer'][answer]['geometry']['coordinates']
                            numberPoints = len(pointsGeometry[0])
                            print '      Number of points: ', numberPoints
                            # Adds the polygons points then closes the ring
                            for point in range(numberPoints):
                                outring.AddPoint(pointsGeometry[0][point][0], pointsGeometry[0][point][1])
                            outring.CloseRings()
                            # Creates the polygon
                            polygon = ogr.Geometry(ogr.wkbPolygon)
                            polygon.AddGeometry(outring)
                            # Put the polygon in the feature
                            feature = ogr.Feature(layerDefinitionPoly)
                            feature.SetGeometry(polygon)
                            # Creates the feature in the layer
                            layerPoly.CreateFeature(feature)
                            # Clears environment for next polygon
                            outring.Destroy()
                            polygon.Destroy()
                            feature.Destroy()
                        elif (typeGeometry == 'Point'):
                            pointCoordinate = data[task][result]['answer'][answer]['geometry']['coordinates']
                            # Creates the point
                            point = ogr.Geometry(ogr.wkbPoint)
                            point.SetPoint(0, pointCoordinate[0], pointCoordinate[1])
                            # Put the point in the feature
                            feature = ogr.Feature(layerDefinitionPoint)
                            feature.SetGeometry(point)
                            # Creates the feature in the layer
                            layerPoint.CreateFeature(feature)
                            # Clears environment for next point
                            point.Destroy()
                            feature.Destroy()
            print ''

    # Flush the content
    shapeDataPoly.Destroy()
    shapeDataPoint.Destroy()

    return 0


#######################
# Begin of the script #
#######################

if __name__ == "__main__":

    # Arguments for the application
    usage = "usage: %prog arg1 arg2 ..."
    parser = OptionParser(usage)

    parser.add_option("-s", "--server", dest="server", \
        help="Address to the server", metavar="SERVER")
    parser.add_option("-n", "--app-name", dest="appName", \
        help="Short name of the application", metavar="APPNAME")
    parser.add_option("-t", "--max-number-tasks", dest="maxNumberTasks", \
        help="Maximum number of tasks to be downloaded", \
        metavar="MAXNUMBERTASKS")
    parser.add_option("-a", "--max-number-answers", dest="maxNumberAnswers", \
        help="Maximum number of answers to be downloaded", \
        metavar="MAXNUMBERANSWERS")
    parser.add_option("-c", "--completed-only", dest="completedOnly", \
        help="Get only completed tasks", metavar="COMPLETEDONLY")
    parser.add_option("-d", "--destination-directory", dest="destDir", \
        help="Directory for results", metavar="DESTDIR")

    (options, args) = parser.parse_args()

    if options.server:
        server = options.server
    else:
        server = "http://forestwatchers.net/pybossa"
    if options.appName:
        appName = options.appName
    else:
        appName = "deforestedareas"
    if options.maxNumberTasks:
        maxNumberTasks = options.maxNumberTasks
    else:
        maxNumberTasks = 200
    if options.maxNumberAnswers:
        maxNumberAnswers = options.maxNumberAnswers
    else:
        maxNumberAnswers = 30
    if options.completedOnly:
        completedOnly = options.completedOnly
    else:
        completedOnly = 1
    if options.destDir:
        destDir = options.destDir
    else:
        destDir = "/home/eduardo/Testes/fw_img/results/"

    #Get the data and start analysing it
    appId = getAppId(server, appName)
    print 'App ID: ', appId
    print ''

    #For all tasks
    completedOnly = 0
    
    tasksInfo = getTasks(server, appId, maxNumberTasks, completedOnly)
    print 'Number tasks: ', len(tasksInfo)
    print ''
    
    results = getResults(server, tasksInfo, maxNumberAnswers)
    print 'Number answers: ', len(results)
    print ''
    
    stats = generateShapefiles(results, destDir, 0)
    print stats
