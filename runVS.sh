#!/bin/sh
if [ "$#" -gt 1 ]; then
    python3 connect3VS.py "$1" "$2"
else
    python3 connect3VS.py "$1"
fi
