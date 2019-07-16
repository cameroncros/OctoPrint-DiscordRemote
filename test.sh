#!/bin/sh
which py > /dev/null 2>&1
if [[ $? == 0 ]]; then
    echo "Running in Windows"
    PYTHON='python'
    py -2 -m virtualenv testenv
    source testenv/Scripts/activate
else
    echo "Running in Linux"
    PYTHON=python2
    python2 -m virtualenv testenv
    source testenv/bin/activate
fi

${PYTHON} -m pip install -r requirements-dev.txt
${PYTHON} -m pip install --upgrade --no-cache-dir https://get.octoprint.org/latest
${PYTHON} setup.py develop
cp testconfig testenv/ -rfv
${PYTHON} configtest.py
${PYTHON} -m webbrowser -t http://127.0.0.1:5000
FAKE_SNAPSHOT=unittests/test_pattern.png octoprint serve -b testenv/testconfig
