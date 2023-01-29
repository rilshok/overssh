#!/usr/bin/env bash

stubgen ./<PROJECT_NAME> -o .
python setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
find <PROJECT_NAME> -name "*.pyi" -type f -delete
rm -r dist build
