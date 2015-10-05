#!/bin/bash

# install requirements
pip install -r requirements.txt
# launch batch
py.test --verbose tests.py
