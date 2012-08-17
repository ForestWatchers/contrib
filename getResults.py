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

import json
import urllib2
from optparse import OptionParser

def getAppId(server, appName):
    """
    Get the application id given the short name

    :arg string server: Address of the server
    :arg string appName: Short name of the application
    :returns: Numerical id of the application
    :rtype: integer
    """
    JSONdata = urllib2.urlopen(server+"/api/app?short_name="+appName)
    data = json.load(JSONdata)
    appId = data[0]['id']
    return appId

def getTasks(server, appId):
    """
    Get the tasks of a particular application from the server.

    :arg string server: Address of the server
    :arg string appID: ID of the application to be analysed
    :returns: Tasks for the applcation
    :rtype: dictionary
    """
    JSONdata = urllib2.urlopen(server+"/api/task?app_id="+str(appId))
    data = json.load(JSONdata)
    numberTasks = len(data)
    taskId = []
    for item in range(numberTasks):
        taskId.append(data[item]['id'])
    return taskId

def getResults(server, appID, tasksId):
    """
    Get the results of a particular application from the server.

    :arg string server: Address of the server
    :arg string appID: ID of the application to be analysed
    :arg list taskId: List of task ID
    :returns: Results for the application
    :rtype: dictionary
    """
    answersApp = {}
    numberTasks = len(tasksId)
    idxData = 0
    for item in range(numberTasks):
        JSONdata = urllib2.urlopen(server+"/api/taskrun?app_id="+str(appID)+"&task_id="+str(tasksId[item]))
        data = json.load(JSONdata)
        lenData = len(data)
        for ans in range(lenData):
            answersApp[idxData] = {'taskId':data[ans]['task_id'], 'id':data[ans]['id'], 'answer':data[ans]['info']}
            idxData = idxData + 1
    return answersApp

def genStats(taskId, data, printStats = 0):
    """
    Calculate statistics about the results

    :art list taskId: List of unique tasks
    :arg dict data: Dictionary with all the results.

    :returns: Some basic statistics about the results
    :rtype: Nothing so far
    """
    numberTasks = len(taskId)
    numberResults = len(data)
    #This structure for search is not efficient. Must replace!!!
    for task in range(numberTasks):
        voteYes = 0
        voteNo = 0
        for result in range(numberResults):
            if data[result]['taskId'] == taskId[task]:
                if data[result]['answer'] == 'Yes':
                    voteYes = voteYes + 1
                else:
                    voteNo = voteNo + 1
        #Print info for debugging
        if printStats == 1:
            print "Stats for task " + str(taskId[task])
            print "Yes = " + str(voteYes)
            print "No = " + str(voteNo)
            print ""
    stats = 'Done.'    
    return stats

#######################
# Begin of the script #
#######################

if __name__ == "__main__":

    # Arguments for the application
    usage = "usage: %prog arg1 arg2"
    parser = OptionParser(usage)

    parser.add_option("-s", "--server", dest="server", help="Address to the server", metavar="SERVER")
    parser.add_option("-n", "--app-name", dest="appName", help="Short name of the application", metavar="APPNAME")

    (options, args) = parser.parse_args()

    if options.server:
        server = options.server
    else:
        server = "http://forestwatchers.net/pybossa"
        #server = "http://pybossa.com"
    if options.appName:
        appName = options.appName
    else:
        appName = "filtering"
        #appName = "flickrperson"

    #Get the data
    appId = getAppId(server, appName)
    tasksId = getTasks(server, appId)
    numberTasks = len(tasksId)
    print "Number of tasks:", numberTasks
    results = getResults(server, appId, tasksId)
    numberResults = len(results)
    print "Number of results:", numberResults
    stats = genStats(tasksId, results, 1)
