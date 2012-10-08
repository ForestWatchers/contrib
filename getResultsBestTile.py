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
import sys
import gdal
import json
import shutil
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
            'id':data[ans]['id'], 'answer':data[ans]['info']['besttile']})
    return answersApp

def genStats(data, printStats = 0):
    """
    Calculate statistics about the results

    :arg list dict data: Dictionary list with all the results.

    :returns: Matrix with answers count for each task
    :rtype: list
    """
    tileCount = []
    numberTasks = len(data)
    for task in range(numberTasks):
        tileCount.append([0] * 12)
        numberResults = len(data[task])
        for result in range(numberResults):
            if data[task][result]['answer'] == '2011352':
                tileCount[task][0] += 1
            elif data[task][result]['answer'] == '2011353':
                tileCount[task][1] += 1
            elif data[task][result]['answer'] == '2011355':
                tileCount[task][2] += 1
            elif data[task][result]['answer'] == '2011357':
                tileCount[task][3] += 1
            elif data[task][result]['answer'] == '2011358':
                tileCount[task][4] += 1
            elif data[task][result]['answer'] == '2011359':
                tileCount[task][5] += 1
            elif data[task][result]['answer'] == '2011360':
                tileCount[task][6] += 1
            elif data[task][result]['answer'] == '2011361':
                tileCount[task][7] += 1
            elif data[task][result]['answer'] == '2011362':
                tileCount[task][8] += 1
            elif data[task][result]['answer'] == '2011363':
                tileCount[task][9] += 1
            elif data[task][result]['answer'] == '2011364':
                tileCount[task][10] += 1
            elif data[task][result]['answer'] == '2011365':
                tileCount[task][11] += 1
        #Print info for debug
        if printStats == 1:
            print "Stats for task " + str(task)
            print "Tile 00 (352) = " + str(tileCount[task][0])
            print "Tile 01 (353) = " + str(tileCount[task][1])
            print "Tile 02 (355) = " + str(tileCount[task][2])
            print "Tile 03 (357) = " + str(tileCount[task][3])
            print "Tile 04 (358) = " + str(tileCount[task][4])
            print "Tile 05 (359) = " + str(tileCount[task][5])
            print "Tile 06 (360) = " + str(tileCount[task][6])
            print "Tile 07 (361) = " + str(tileCount[task][7])
            print "Tile 08 (362) = " + str(tileCount[task][8])
            print "Tile 09 (363) = " + str(tileCount[task][9])
            print "Tile 10 (364) = " + str(tileCount[task][10])
            print "Tile 11 (365) = " + str(tileCount[task][11])
            print "Maximum value = " + str(max(tileCount[task]))
            print "Position = " + str(tileCount[task].index(max(tileCount[task])))
            print ""
    return tileCount

def cutBestTiles(tasksInfo, results):
    """
    Cut the best tiles based on the results obtained by genStats

    :arg list dict tasks: Dictionary list with the tasks info.
    :arg list dict results: Dictionary list with the processed results.

    :returns: Nothing
    :rtype: None
    """
    origLocation = "/home/eduardo/Testes/fw_img/FAS_Brazil7/"
    tmpLocation = "/home/eduardo/Testes/fw_img/FAS_Brazil7/tmp/"
    destLocation = "/home/eduardo/Testes/fw_img/FAS_Brazil7/final/"
    colourTmp = "/home/eduardo/Testes/fw_img/FAS_Brazil7/tmpColour/"
    colourFinal = "/home/eduardo/Testes/fw_img/FAS_Brazil7/finalColour/"

    intensity = 1
    formatFile = "GTiff"
    driver = gdal.GetDriverByName(formatFile)

    numberTasks = len(tasksInfo)
    for task in range(numberTasks):
        taskId = tasksInfo[task]['taskId']
        definedArea = tasksInfo[task]['area']
        selectedTile = results[task].index(max(results[task]))
        if selectedTile == 0:
            selectedFile = '2011352'
        elif selectedTile == 1:
            selectedFile = '2011353'
        elif selectedTile == 2:
            selectedFile = '2011355'
        elif selectedTile == 3:
            selectedFile = '2011357'
        elif selectedTile == 4:
            selectedFile = '2011358'
        elif selectedTile == 5:
            selectedFile = '2011359'
        elif selectedTile == 6:
            selectedFile = '2011360'
        elif selectedTile == 7:
            selectedFile = '2011361'
        elif selectedTile == 8:
            selectedFile = '2011362'
        elif selectedTile == 9:
            selectedFile = '2011363'
        elif selectedTile == 10:
            selectedFile = '2011364'
        elif selectedTile == 11:
            selectedFile = '2011365'
        print taskId
        print selectedFile
        print definedArea
        cmd = "gdal_translate -projwin "+str(definedArea[0])+" "+ \
            str(definedArea[3])+" "+str(definedArea[2])+" "+ \
            str(definedArea[1])+" "+origLocation+selectedFile+".tif "+ \
            tmpLocation+str(taskId)+".tif"
        os.system(cmd)
        if intensity == 1:
            origCut = tmpLocation+str(taskId)+".tif"
            colourCut = colourTmp+str(taskId)+".tif"
            if os.path.isfile(origCut):
                shutil.copy(origCut, colourCut)
                pointFile = gdal.Open(colourCut, 2)
                votes = max(results[task])
                for item in range(pointFile.RasterCount):
                    data = pointFile.GetRasterBand(item+1).ReadAsArray()
                    lenData = len(data)
                    if item == 1:
                        newData = (data * 0) + int(votes * 8)
                    else:
                        newData = (data * 0)
                    pointFile.GetRasterBand(item+1).WriteArray(newData)
                pointFile = None
    cmd = "gdal_merge.py -o "+destLocation+"mosaic.tif "+tmpLocation+ \
        "*.tif"
    os.system(cmd)
    cmd = "gdal_merge.py -o "+colourFinal+"mosaic.tif "+colourTmp+ \
        "*.tif"
    os.system(cmd)
    resultCut = 0
    return resultCut

#######################
# Begin of the script #
#######################

if __name__ == "__main__":

    # Arguments for the application
    usage = "usage: %prog arg1 arg2"
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

    (options, args) = parser.parse_args()

    if options.server:
        server = options.server
    else:
        server = "http://forestwatchers.net/pybossa"
    if options.appName:
        appName = options.appName
    else:
        appName = "besttile"
    if options.maxNumberTasks:
        maxNumberTasks = options.maxNumberTasks
    else:
        maxNumberTasks = 1060
    if options.maxNumberAnswers:
        maxNumberAnswers = options.maxNumberAnswers
    else:
        maxNumberAnswers = 35
    if options.completedOnly:
        completedOnly = options.completedOnly
    else:
        completedOnly = 0

    #Get the data and start analysing it
    appId = getAppId(server, appName)
    tasksInfo = getTasks(server, appId, maxNumberTasks, completedOnly)
    results = getResults(server, tasksInfo, maxNumberAnswers)
    stats = genStats(results, 0)
    finalResult = cutBestTiles(tasksInfo, stats)
