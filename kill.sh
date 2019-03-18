#!/usr/bin/env bash
OCTOPRINT_STRING=`ps -e | grep octoprint`
if [[ $? -ne 0 ]]; then
    echo Octoprint not running
    exit 1
fi

ps -e | grep WINPID 2>&1
if [[ $? == 0 ]]; then
    OCTOPRINT_PID=`${OCTOPRINT_STRING} | awk '{print $1;}'`
    kill -9 $OCTOPRINT_PID
else
    OCTOPRINT_PID=`${OCTOPRINT_STRING} | awk '{print $4;}'`
    taskkill -PID $OCTOPRINT_PID -F
fi


