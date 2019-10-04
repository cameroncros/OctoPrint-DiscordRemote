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

${PYTHON} -m pip install bumpversion
git checkout dev
git pull
git checkout master
git pull
git merge dev
git push
git checkout dev
git stash
bumpversion minor
git commit setup.py .bumpversion.cfg -m "Bump version for next release"
git push
git stash pop
