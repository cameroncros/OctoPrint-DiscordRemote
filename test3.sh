#!/bin/sh
which py > /dev/null 2>&1
if [[ $? == 0 ]]; then
    echo "Running in Windows"
    PYTHON='python'
    py -3 -m venv testenv3
    source testenv3/Scripts/activate
else
    echo "Running in Linux"
    PYTHON=python3
    python3 -m venv testenv3
    source testenv3/bin/activate
fi

${PYTHON} -m pip install -r requirements-dev.txt
${PYTHON} -m pip install --upgrade --no-cache-dir git+https://github.com/foosel/OctoPrint.git@devel
${PYTHON} setup.py develop
cp testconfig testenv3/ -rfv
${PYTHON} configtest3.py
${PYTHON} -m webbrowser -t http://127.0.0.1:5000
FAKE_SNAPSHOT=unittests/test_pattern.png octoprint serve -b testenv3/testconfig
