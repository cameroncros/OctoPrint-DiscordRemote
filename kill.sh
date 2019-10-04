#!/usr/bin/env bash
ps -e | grep WINPID 2>&1
if [[ $? -ne 0 ]]; then
    OCTOPRINT_PID=`ps -e | grep octoprint 2>&1 | awk '{print $1;}'`
    if [[ ${OCTOPRINT_PID} == "" ]]; then
        echo Octoprint not running
        exit 1
    fi
    kill -9 ${OCTOPRINT_PID}
else
    OCTOPRINT_PID=`wmic process get processid, commandline -format:csv | grep python | awk -F ',' '{print $3}'`
    OCTOPRINT_PID=`echo $OCTOPRINT_PID | awk -F '\r' '{print $1}'`
    if [[ ${OCTOPRINT_PID} == "" ]]; then
        echo Octoprint not running
        exit 1
    fi
    taskkill -PID ${OCTOPRINT_PID} -F
fi
