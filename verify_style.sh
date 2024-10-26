#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <python file>"
  exit 1
fi

# Run pycodestyle
echo "Running pycodestyle..."
python3 -m pycodestyle "$1"
pycodestyle_exit_code=$?

# Run pydocstyle
echo "Running pydocstyle..."
python3 -m pydocstyle "$1"
pydocstyle_exit_code=$?

# Exit with the appropriate status code
if [ $pycodestyle_exit_code -ne 0 ] || [ $pydocstyle_exit_code -ne 0 ]; then
  exit 1
else
  exit 0
fi