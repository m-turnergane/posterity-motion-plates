#!/bin/bash
cd /workspace/posterity/standalones/germanicus/edit/examiner-v5b
M=/workspace/posterity/renders/posterity-germanicus-v5b-ROUGH.mp4
/workspace/asrvenv/bin/python asr5.py $M small.en asr_small.json > asr_small.out 2>&1
/workspace/asrvenv/bin/python asr5.py $M medium.en asr_medium.json > asr_medium.out 2>&1
echo ALLDONE > done.flag
