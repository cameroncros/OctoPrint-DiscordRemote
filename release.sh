#!/bin/sh
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
