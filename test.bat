REM Setup testenv on Windows

py -2 -m virtualenv testenv

call Scripts\activate.bat
pip install https://get.octoprint.org/latest
python2 setup.py develop
cp -rf testconfig testenv\
python2 configtest.py
python -m webbrowser -t http://127.0.0.1:5000
octoprint serve -b testenv\testconfig
