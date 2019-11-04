import sys
sys.path.append("/home/harada/Documents/WorkSpace/miscela")

import argparse
import pickle
from src.func import miscela
from src.func import re_miscela
from src.func import assembler
from src.func import capAnalysis
from src.func import exp_delay
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
    parser.add_argument("--maxAtt", help="the maximum number of attributes you would like to find", type=int, default=2)
    parser.add_argument("--minSup", help="the minimum number of timestamps for co-evolution", type=int, default=500)
    parser.add_argument("--evoRate", help="evolving rate", type=float, default=0.5)
    parser.add_argument("--distance", help="distance threshold", type=float, default=0.8)
    parser.add_argument("--delay", help="delay", nargs="*", default=[0, 0, 0, 0, 0])
    parser.add_argument("--mode", help="minig or analysis or exp or output", type=str, default="mining")
    args = parser.parse_args()

    if type(args.delay[0]) is str:
        args.delay = [int(x) for x in args.delay]
    print(args)

    if args.mode == "mining":
        assembler(args)
        miscela(args)
        # re_miscela(args)
        exit()

    if args.mode == "analysis":
        capAnalysis(args)
        exit()

    if args.mode == "exp":
        exp_delay(args)
        exit()

    if args.mode == "output":
        CAP = pickle.load(open("tmp/00/" + args.dataset + "/cap.pickle", "rb"))
        S = pickle.load(open("tmp/00/"+args.dataset+"/sensor.pickle", "rb"))
        outputCAP(args.dataset, S, CAP[:10])
        exit()
