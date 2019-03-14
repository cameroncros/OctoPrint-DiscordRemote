#!/bin/sh
# Setup testenv on *nix os's
PYTHON=python2
ACTIVATE='source testenv/bin/activate'
which $PYTHON > /dev/null 2>&1
if [ $? == 1 ]; then
    PYTHON='py -2'
    ACTIVATE='source testenv/Scripts/activate'
fi
$PYTHON -m virtualenv testenv
$ACTIVATE

$PYTHON -m pip install --upgrade --no-cache-dir https://get.octoprint.org/latest
$PYTHON setup.py develop
$PYTHON configtest.py
$PYTHON -m webbrowser -t http://127.0.0.1:5000
FAKE_SNAPSHOT=unittests/test_pattern.png octoprint serve -b testenv/testconfig
