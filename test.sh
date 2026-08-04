#!/bin/bash
set -e

echo "========================================"
echo " Running ForgeTUI Unit Test Suite"
echo "========================================"

python3 -m unittest discover -s tests -p "test_*.py" "$@"
