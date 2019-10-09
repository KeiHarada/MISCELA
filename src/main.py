import argparse
import pickle
from src.func import miscela
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
    parser.add_argument("--minSup", help="the minimum number of timestamps for co-evolution", type=int, default=1000)
    parser.add_argument("--evoRate", help="evolving rate", type=float, default=0.5)
    parser.add_argument("--distance", help="distance threshold", type=float, default=0.1)
    parser.add_argument("--delay", help="delay", nargs="*", default=[0, 0, 0, 0, 0])
    args = parser.parse_args()

    print(args)

    a = set()
    a.add(1)
    a.add(2)
    print(a)
    a = set(list(map(lambda x: x+5, a)))
    print(a)
    exit()

    # cap mining
    miscela(args)

    # output
    CAP = pickle.load(open("pickle/" + args.dataset + "/cap.pickle", "rb"))
    S = pickle.load(open("pickle/"+args.dataset+"/sensor.pickle", "rb"))
    outputCAP(args.dataset, S, CAP[:1])