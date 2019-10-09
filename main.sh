#!/bin/sh
python ./src/main.py --dataset china13 --maxAtt 13 --distance 200 --delay [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
cp -r ./pickle/china13/ ./tmp/china13_0/
python ./src/main.py --dataset china13 --maxAtt 13 --distance 200 --delay [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
cp -r ./pickle/china13/ ./tmp/china13_1/
python ./src/main.py --dataset china13 --maxAtt 13 --distance 200 --delay [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
cp -r ./pickle/china13/ ./tmp/china13_2/
python ./src/main.py --dataset china13 --maxAtt 13 --distance 200 --delay [0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0]
cp -r ./pickle/china13/ ./tmp/china13_3/
python ./src/main.py --dataset china13 --maxAtt 13 --distance 200 --delay [0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0]
cp -r ./pickle/china13/ ./tmp/china13_4/