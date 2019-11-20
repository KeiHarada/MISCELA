#!/usr/local/bin/python3.7

# evoRate
python ./src/main.py --mode expEvoRate --dataset santander --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 0.8 --delay 0 0 0 0 0
python ./src/main.py --mode expEvoRate --dataset china13 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0 0 0 0 0 0 0 0
python ./src/main.py --mode expEvoRate --dataset china6 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0

# minSup
python ./src/main.py --mode expMinSup --dataset santander --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 0.8 --delay 0 0 0 0 0
python ./src/main.py --mode expMinSup --dataset china13 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0 0 0 0 0 0 0 0
python ./src/main.py --mode expMinSup --dataset china6 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0

# maxAtt
python ./src/main.py --mode expMaxAtt --dataset santander --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 0.8 --delay 0 0 0 0 0
python ./src/main.py --mode expMaxAtt --dataset china13 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0 0 0 0 0 0 0 0
python ./src/main.py --mode expMaxAtt --dataset china6 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0

# delay
python ./src/main.py --mode expDelay --dataset santander --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 0.8 --delay 0 0 0 0 0
python ./src/main.py --mode expDelay --dataset china13 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0 0 0 0 0 0 0 0
python ./src/main.py --mode expDelay --dataset china6 --minSup 500 --evoRate 0.5 --maxAtt 2 --distance 200 --delay 0 0 0 0 0 0
