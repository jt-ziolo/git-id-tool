#!/bin/bash

pip install --upgrade build
python -m build
pip install --editable .