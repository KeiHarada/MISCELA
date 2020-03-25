# MISCELA
データセットはvishnu/users/home/harada/miscela の中の db を本ディレクトリ上にコピーしてください。

## パラメータ
- dataset (str) : (デフォルト "santander")
- maxAtt (int) : 発見するCAPの最大属性数 (デフォルト 5)
- minSup (int) : ミニマムサポート (デフォルト 500)
- evoRate (float) : Evolving 率 (from 0 to 1) (デフォルト 0.5)
- distance (float) : DBSCAN の距離 ([km])
- delay (array) : ディレイさせたい属性の数字を変化させる (例: 属性数5の Santander dataset なら 0 0 0 0 0 --> 1 0 0 0 0 や -1 0 0 0 0 など)。属性の並び順は論文やデータセットを参照してください。

## 実行モード
- mining : Assembler と MISCELA が実行されます。結果は /pickle の中に保存されます。
- expDelay : Delayを変化させた場合の実験が実施されます。--delay 以外のパラメータを指定してください。結果は /result に保存されます。
- expEvoRate : Delayを変化させた場合の実験が実施されます。--evoRate 以外のパラメータを指定してください。結果は /result に保存されます。
- expMaxAtt : Delayを変化させた場合の実験が実施されます。--maxAtt 以外のパラメータを指定してください。結果は /result に保存されます。
- expMinSup : Delayを変化させた場合の実験が実施されます。--minSup 以外のパラメータを指定してください。結果は /result に保存されます。

## Santander dataset のマイニング命令
python ./src/main.py --mode mining --dataset santander --minSup 500 --evoRate 0.5 --maxAtt 5 --distance 0.8 --delay 0 0 0 0 0

## China6 dataset のマイニング命令
python ./src/main.py --mode mining --dataset china6 --minSup 500 --evoRate 0.5 --maxAtt 6 --distance 200.0 --delay 0 0 0 0 0 0

## China13 dataset のマイニング命令
python ./src/main.py --mode mining --dataset china13 --minSup 500 --evoRate 0.5 --maxAtt 13 --distance 200.0 --delay 0 0 0 0 0 0 0 0 0 0 0 0 0