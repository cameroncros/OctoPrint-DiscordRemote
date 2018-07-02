REM Setup testenv on Windows

py -2 -m virtualenv testenv

call testenv\Scripts\activate.bat
pip install https://get.octoprint.org/latest
python setup.py develop
cp -rf testconfig testenv\
python configtest.py
python -m webbrowser -t http://127.0.0.1:5000
octoprint serve -b testenv\testconfig
