#!/bin/sh

pip3 show coinlib

python3 -u coinlibFactory.py 2>&1 &
P1=$!

# node tumblerServer starten

wait $P1