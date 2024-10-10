#!/usr/bin/env bash
# pip install wheel twine
python3 setup.py sdist bdist_wheel
twine upload dist/*