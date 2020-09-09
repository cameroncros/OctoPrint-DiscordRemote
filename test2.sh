#!/bin/bash
command -v py > /dev/null 2>&1
if [[ $? == 0 ]]; then
    echo "Running in Windows"
    PYTHON='python'
    py -2 -m virtualenv testenv2
    source testenv2/Scripts/activate
else
    echo "Running in Linux"
    PYTHON=python2
    ${PYTHON} -m virtualenv testenv2
    source testenv2/bin/activate
fi
set -e
echo "Installing Pre-requisites"
${PYTHON} -m pip install -r requirements-dev.txt
echo "Installing Octoprint"
${PYTHON} -m pip install --upgrade --no-cache-dir git+https://github.com/foosel/OctoPrint.git@1.3.12
echo "Install DiscordRemote"
${PYTHON} setup.py develop
echo "Copy config"
cp testconfig testenv2/ -rfv
${PYTHON} configtest2.py
echo "Start browser"
${PYTHON} -m webbrowser -t http://127.0.0.1:5000
echo "Start Octoprint"
FAKE_SNAPSHOT=unittests/test_pattern.png octoprint serve -b testenv2/testconfig
