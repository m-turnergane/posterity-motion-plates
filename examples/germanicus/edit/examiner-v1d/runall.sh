#!/bin/bash
cd /workspace/posterity/standalones/germanicus/edit/examiner-v1d
M=/workspace/posterity/renders/posterity-germanicus-ROUGH-v1d.mp4
/workspace/asrvenv/bin/python asr3.py $M small.en asr_master_small.json > asr_small.out 2>&1
/workspace/asrvenv/bin/python asr3.py $M medium.en asr_master_medium.json > asr_medium.out 2>&1
echo ALLDONE > done.flag
