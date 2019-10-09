import sys
sys.path.append("/home/harada/Documents/WorkSpace/miscela")

import argparse
import pickle
from src.func import miscela
from src.func import assembler
from src.func import outputCAP

if __name__ == "__main__":
    '''
    :parameters
        0. path_root_src
        1. dataset
        2. maxAtt
        3. minSup
        4. evoRate (from 0 to 1)
        5. distance ([km])
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_root_src", type=str, default="src/main.py")
    parser.add_argument("--dataset", help="which dataset would like to use", type=str, default="santander")
    parser.add_argument("--maxAtt", help="the maximum number of attributes you would like to find", type=int, default=5)
    parser.add_argument("--minSup", help="the minimum number of timestamps for co-evolution", type=int, default=1000)
    parser.add_argument("--evoRate", help="evolving rate", type=float, default=0.5)
    parser.add_argument("--distance", help="distance threshold", type=float, default=1.0)
    parser.add_argument("--delay", help="delay", nargs="*", default=[0, 0, 0, 0, 0])
    args = parser.parse_args()

    print(args)

    # cap mining
    #assembler(args)
    miscela(args)

    exit()

    # output
    CAP = pickle.load(open("pickle/" + args.dataset + "/cap.pickle", "rb"))
    S = pickle.load(open("pickle/"+args.dataset+"/sensor.pickle", "rb"))
    outputCAP(args.dataset, S, CAP[:1])