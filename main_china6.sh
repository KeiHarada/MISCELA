#!/home/harada/.pyenv/versions/miscela_demo/bin/python
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 0 0 0
cp -r ./pickle/china6 ./tmp/00
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 1 0 0 0 0 0
cp -r ./pickle/china6 ./tmp/01
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay -1 0 0 0 0 0
cp -r ./pickle/china6 ./tmp/02
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 1 0 0 0 0 
cp -r ./pickle/china6 ./tmp/03
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 -1 0 0 0 0 
cp -r ./pickle/china6 ./tmp/04
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 1 0 0 0 
cp -r ./pickle/china6 ./tmp/05
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 -1 0 0 0 
cp -r ./pickle/china6 ./tmp/06
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 1 0 0 
cp -r ./pickle/china6 ./tmp/07
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 -1 0 0
cp -r ./pickle/china6 ./tmp/08
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 0 1 0 
cp -r ./pickle/china6 ./tmp/09
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 0 -1 0 
cp -r ./pickle/china6 ./tmp/10
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 0 0 1 
cp -r ./pickle/china6 ./tmp/11
python ./src/main.py --dataset china6 --maxAtt 6 --distance 200 --delay 0 0 0 0 0 -1
cp -r ./pickle/china6 ./tmp/12