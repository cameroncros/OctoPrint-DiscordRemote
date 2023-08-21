#!/bin/bash
which py > /dev/null 2>&1
if [[ $? == 0 ]]; then
    echo "Running in Windows"
    PYTHON='python'
    py -3 -m venv testenv
    source testenv/Scripts/activate
else
    echo "Running in Linux"
    PYTHON=python3
    python3 -m venv testenv
    source testenv/bin/activate
fi

${PYTHON} -m pip install -r requirements-dev.txt
${PYTHON} -m pip install --upgrade --no-cache-dir git+https://github.com/foosel/OctoPrint.git@devel
${PYTHON} -m pip install --upgrade --no-cache-dir https://github.com/OctoPrint/OctoPrint-Testpicture/archive/refs/heads/main.zip
${PYTHON} -m pip uninstall OctoPrint-DiscordRemote
${PYTHON} -m pip install .
${PYTHON} configtest.py
${PYTHON} -m webbrowser -t http://127.0.0.1:5000
octoprint serve -b testconfig
