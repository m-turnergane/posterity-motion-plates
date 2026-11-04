#!/bin/bash
cd /workspace/posterity/standalones/bjorn/rough_v2/build
for k in "$@"; do /workspace/mpvenv/bin/python build_bjorn_rough_v2.py clip $k 2>&1 | grep -v WARN | tail -2; done
