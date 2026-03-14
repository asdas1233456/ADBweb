#!/bin/bash

set -e

echo "========================================"
echo "ADBweb comprehensive test suite"
echo "========================================"
echo

if ! command -v python3 &> /dev/null; then
  echo "Error: python3 not found. Please install Python 3.8+"
  exit 1
fi

echo "Python version: $(python3 --version)"

# Install dependencies if needed
if ! python3 -c "import pytest" &> /dev/null; then
  echo "Installing test dependencies..."
  python3 -m pip install -r requirements.txt
fi

mkdir -p reports allure-results

echo
echo "Running tests..."
python3 -m pytest -v

status=$?
if [ $status -ne 0 ]; then
  echo
  echo "Tests failed"
else
  echo
  echo "Tests completed"
fi

echo
if command -v allure &> /dev/null; then
  echo "Generating Allure report..."
  allure generate allure-results -o allure-report --clean
  echo "Allure report: allure-report/index.html"
else
  echo "Allure CLI not found. HTML report: reports/report.html"
fi

echo
exit $status
