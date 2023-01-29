#!/usr/bin/env bash

stubgen ./overssh -o .
python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
find overssh -name "*.pyi" -type f -delete
rm -r dist build
