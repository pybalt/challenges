#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: bash run_single_test.sh \"<test_case_name>\""
    exit 1
fi

python -m unittest "$1"

