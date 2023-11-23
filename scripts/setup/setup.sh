#!/bin/bash

git clone https://github.com/AshGw/litecrypt.git
cd litecrypt || exit
rm -rf dist
rm -rf build
rm -rf litecrypt.egg-info
if [[ "$(uname -s)" == "MINGW"* ]]; then
  python.exe -m pip install --upgrade pip
else
  pip install --upgrade pip
fi
pip install -r scripts/setup/requirements.txt
python setup.py develop
rm -rf litecrypt.egg-info
pre-commit install
