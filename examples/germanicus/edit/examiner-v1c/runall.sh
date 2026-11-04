#!/bin/bash
cd /workspace/posterity/standalones/germanicus/edit/examiner-v1c
M=/workspace/posterity/renders/posterity-germanicus-ROUGH-v1c.mp4
(cd audio && /workspace/mpvenv/bin/python ana.py > ana.out 2>&1) &
/workspace/asrvenv/bin/python asr3.py $M small.en asr_master_small.json > asr_small.out 2>&1
/workspace/asrvenv/bin/python asr3.py $M medium.en asr_master_medium.json > asr_medium.out 2>&1
wait
echo ALLDONE > done.flag
