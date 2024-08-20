#!/bin/sh

# Find the Python  path
PATH=$(which python3)

# Check if Python interpreter was found
if [ -z "$PATH" ]; then
    echo "Python3 not found."
    exit 1
fi

#run the script
"$PATH" setup.py "$@"

