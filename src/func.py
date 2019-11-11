import sys
sys.path.append("/home/harada/Documents/WorkSpace/miscela")

import pandas as pd
import numpy as np
import copy
import time
import pickle
from pyclustering.cluster.dbscan import dbscan

from src.myclass import Color
from src.myclass import Sensor
from src.myclass import Cluster
from src.myclass import CAP
from src.myutility import deg2km
from src.myutility import dist

def loadData(attribute, dataset):

    data = pd.read_csv("db/"+dataset+"/data.csv", dtype=object)
    data = data[data["attribute"] == attribute]
    location = pd.read_csv("db/"+dataset+"/location.csv", dtype=object)
    location = location[location["attribute"] == attribute]
    ids = list(location["id"])
    timestamps = list(data["time"])

    s = list()
    for i in ids:
        location_i = location[location["id"] == str(i)]
        location_i = (float(location_i["lat"]), float(location_i["lon"]))
        data_i = data[data["id"] == str(i)]
        data_i = list(data_i["data"])
        s_i = Sensor()
        s_i.setId(str(i))
        s_i.setAttribute(str(attribute))
        s_i.setTime(timestamps)
        s_i.setLocation(location_i)
        s_i.setData(data_i)
        s.append(s_i)
        del s_i

    return s

def dataSegmenting(S):

    '''
    algorithm
    rpt.Dynp(model='l2', custom_cost=None, min_size=2, jump=5, params=None)
    rpt.Pelt(model='l2', custom_cost=None, min_size=2, jump=5, params=None)
    rpt.Binseg(model='l2', custom_cost=None, min_size=2, jump=5, params=None)
    rpt.BottomUp(model='l2', custom_cost=None, min_size=2, jump=5, params=None)
    rpt.Window(width=100, model='l2', custom_cost=None, min_size=2, jump=5, params=None)
    '''

    for s_i in S:
        data = pd.Series(s_i.getData())
        data = data.fillna(method="ffill")
        data = data.fillna(method="bfill")
        data = data.astype("float64")
        s_i.setData_filled(list(data))

def estimateThreshold(S, M, evoRate):

    thresholds = dict()

    # each attribute
    offset = 0
    for attribute in M.keys():
        distribution = list()

        # each sensor
        for s_i in S[offset: offset+M[attribute]]:
            data = s_i.getData_filled()
            prev = 0.0

            # each value
            for value in data:
                distribution.append(abs(value-prev))
                prev = value

        distribution.sort(reverse=True)
        threshold = distribution[int(evoRate * len(distribution))]
        thresholds[attribute] = threshold
        offset += M[attribute]
        del distribution

    return thresholds

def extractEvolving(S, thresholds):

    for s in S:
        prev = 0.0
        data = s.getData_filled()
        for i in range(len(data)):
            delta = data[i] - prev
            if delta > thresholds[s.getAttribute()]:
                s.addTp(i)
            if delta < (-1)*thresholds[s.getAttribute()]:
                s.addTn(i)
            prev = data[i]

def clustering(S, distance):

    '''
    DBSCAN
    '''

    locations = list(map(lambda s_i: deg2km(s_i.getLocation()[0], s_i.getLocation()[1]), S))
    inst = dbscan(data=locations, eps=distance, neighbors=2, ccore=False) # True is for C++, False is for Python.
    inst.process()
    clusters = inst.get_clusters()

    '''
    set the results into Cluster class
    '''

    C = list()
    for cluster in clusters:
        c = Cluster()
        cluster.sort()
        c.setMember(cluster)
        attributes = set()
        for i in cluster:
            attributes.add(S[i].getAttribute())
            for j in cluster[cluster.index(i)+1:]:
                    if dist(S[i].getLocation(), S[j].getLocation()) <= distance:
                        S[i].addNeighbor(j)
                        S[j].addNeighbor(i)

        c.setAttribute(attributes)
        C.append(c)

    return C

def search(algorithm, S, C, K, psi, tau):

    CAPs = list()
    if algorithm == "miscela":
        for c in C:
            CAPs += capSearch(S, c, K, psi, tau, list(), list())

    if algorithm == "assembler":
        for c in C:
            CAPs += scpSearch(S, c, K, psi, tau, list(), list())

    for i in range(len(CAPs)):
        CAPs[i].setId(i)
        CAPs[i].setCoevolution()

    return CAPs

def capSearch(S, c, K, psi, tau, X, CAP_X):

    CAPs = list()

    if len(X) >= 2:
        CAPs += CAP_X

    F_X = follower(S, c, X)

    for y in F_X:
        Y = X.copy()
        Y.append(y)
        Y.sort()

        if parent_miscela(S, Y, K) == X:
            CAP_Y = getCAP(S, y, psi, tau, CAP_X)
            if len(CAP_Y) != 0:
                CAPs += capSearch(S, c, K, psi, tau, Y, CAP_Y)

    return CAPs

def scpSearch(S, c, K, psi, tau, X, CAP_X):

    CAPs = list()

    CNTs = 0
    if len(X) >= 2:
        for cap_x in CAP_X:
            if len(cap_x.getAttribute()) >= 2 and len(cap_x.getAttribute()) <= K:
                CAPs += CAP_X
                CNTs += 1
    print("")
    print(len(CAP_X), "\t", CNTs)

    F_X = follower(S, c, X)

    for y in F_X:
        Y = X.copy()
        Y.append(y)
        Y.sort()

        if parent_assembler(S, Y) == X:
            CAP_Y = getCAP(S, y, psi, tau, CAP_X)
            if len(CAP_Y) != 0:
                CAPs += capSearch(S, c, K, psi, tau, Y, CAP_Y)

    return CAPs

def follower(S, c, X):

    # root
    if len(X) == 0:
        return c.getMember()

    # followers
    else:
        F_X = set()
        for x in X:
            F_X |= S[x].getNeighbor()
        F_X -= set(X)
        return sorted(list(F_X))

def parent_miscela(S, Y, K):

    # size(Y) = 1
    if len(Y) == 1:
        return list()

    # size(Y) == 2
    if len(Y) == 2:
        if S[Y[0]].getAttribute() == S[Y[1]].getAttribute():
            return list()
        else:
            return [Y[1], ]

    # size(Y) >= 3
    # Y contains more/less than or equal to 2/K attributes
    attCounter = set()
    for y in Y:
        attCounter.add(S[y].getAttribute())
    if len(attCounter) > K:
        return list()

    for y in Y:
        Z = Y.copy()
        Z.remove(y)
        L_Z = np.array([[0]*len(Z)]*len(Z))
        for i in range(0, len(Z)):
            for j in range(i+1, len(Z)):
                if Z[j] in S[Z[i]].getNeighbor():
                    L_Z[i][j] = -1
                    L_Z[j][i] = -1
            L_Z[i][i] = np.count_nonzero(L_Z[i])

        # rank(L(Z)) = |Z|-1 => Z is connected
        if np.linalg.matrix_rank(L_Z) == len(Z)-1:

            # Z contains more/less than or equal to 2/K attributes
            attCounter = set()
            for z in Z:
                attCounter.add(S[z].getAttribute())
            if len(attCounter) >= 2 and len(attCounter) <= K:
                return Z

    return list()

def parent_assembler(S, Y):

    # size(Y) = 1
    if len(Y) == 1:
        return list()

    # size(Y) == 2
    if len(Y) == 2:
        return [Y[1], ]

    # size(Y) >= 3
    for y in Y:
        Z = Y.copy()
        Z.remove(y)
        L_Z = np.array([[0]*len(Z)]*len(Z))
        for i in range(0, len(Z)):
            for j in range(i+1, len(Z)):
                if Z[j] in S[Z[i]].getNeighbor():
                    L_Z[i][j] = -1
                    L_Z[j][i] = -1
            L_Z[i][i] = np.count_nonzero(L_Z[i])

        # rank(L(Z)) = |Z|-1 => Z is connected
        if np.linalg.matrix_rank(L_Z) == len(Z)-1:
            return Z

    return list()

def getCAP(S, y, psi, tau, C_X):

    delay = tau[S[y].getAttribute()]
    C_Y = list()
    # init
    if len(C_X) == 0:
        if len(S[y].getTp(delay)) + len(S[y].getTn(delay)) >= psi:
            cap = CAP()
            cap.addMember(y)
            cap.addAttribute(S[y].getAttribute())
            cap.setPattern(S[y].getAttribute(), 1)
            cap.setP1(S[y].getTp(delay))
            cap.setP2(S[y].getTn(delay))
            C_Y.append(cap)

        return C_Y

    # following
    else:

        for cap_x in C_X:
            cap = copy.deepcopy(cap_x)
            p1 = set()
            p2 = set()

            # y_a isn't a new attribute
            if S[y].getAttribute() in cap.getAttribute():

                # calculate intersection (1:increase, -1:decrease)
                if cap.getPattern()[S[y].getAttribute()] == 1:
                    p1 = cap.getP1() & S[y].getTp(delay)
                    p2 = cap.getP2() & S[y].getTn(delay)
                if cap.getPattern()[S[y].getAttribute()] == -1:
                    p1 = cap.getP1() & S[y].getTn(delay)
                    p2 = cap.getP2() & S[y].getTp(delay)
                if cap.getPattern()[S[y].getAttribute()] == 0:
                    print("cap error")
                    quit()

                # set cap
                if len(p1)+len(p2) >= psi:
                    cap.addMember(y)
                    cap.setP1(p1)
                    cap.setP2(p2)
                    C_Y.append(cap)

            # y_a is a new attribute
            else:

                cap_new = copy.deepcopy(cap)
                p1 = cap_new.getP1() & S[y].getTp(delay)
                p2 = cap_new.getP2() & S[y].getTn(delay)
                if len(p1) + len(p2) >= psi:
                    cap_new.addAttribute(S[y].getAttribute())
                    cap_new.addMember(y)
                    cap_new.setPattern(S[y].getAttribute(), 1)
                    cap_new.setP1(p1)
                    cap_new.setP2(p2)
                    C_Y.append(cap_new)

                del cap_new

                cap_new = copy.deepcopy(cap)
                p1 = cap_new.getP1() & S[y].getTn (delay)
                p2 = cap_new.getP2() & S[y].getTp(delay)
                if len(p1) + len(p2) >= psi:
                    cap_new.addAttribute(S[y].getAttribute())
                    cap_new.addMember(y)
                    cap_new.setPattern(S[y].getAttribute(), -1)
                    cap_new.setP1(p1)
                    cap_new.setP2(p2)
                    C_Y.append(cap_new)

        return C_Y

def outputCAP(dataset, S, CAPs):

    for cap in CAPs:

        cap_id = cap.getId()

        with open("result/" + dataset + "/" + str(cap_id).zfill(5) + "_pattern.csv", "w") as of_pattern:
            with open("result/"+dataset+"/"+str(cap_id).zfill(5)+"_location.csv", "w") as of_location:
                with open("result/" + dataset + "/" + str(cap_id).zfill(5) + "_data.csv", "w") as of_data:
                    with open("result/" + dataset + "/" + str(cap_id).zfill(5) + "_data_filled.csv", "w") as of_data_filled:

                        of_pattern.write("id,attribute,pattern\n")
                        of_location.write("id,attribute,lat,lon\n")
                        data = pd.DataFrame(S[0].getTime(), columns=["time"])
                        data_filled = pd.DataFrame(S[0].getTime(), columns=["time"])

                        for i in cap.getMember():

                            sid = S[i].getId()
                            attribute = S[i].getAttribute()

                            # pattern
                            pattern = cap.getPattern()[attribute]
                            of_pattern.write(sid+","+attribute+","+str(pattern)+"\n")

                            # location
                            lat, lon = S[i].getLocation()
                            of_location.write(sid+","+attribute+","+str(lat)+","+str(lon)+"\n")

                            # data
                            data[sid] = pd.Series(S[i].getData())
                            data_filled[sid] = pd.Series(S[i].getData_filled())

                        data.to_csv(of_data, index=False)
                        data_filled.to_csv(of_data_filled, index=False)

def miscela(args):

    print("*----------------------------------------------------------*")
    print("* MISCELA is getting start ...")

    # load data on memory
    print("\t|- phase0: loading data ... ", end="")
    S = list()
    M = dict()
    D, idx = dict(), 0
    for attribute in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        attribute = attribute.strip()
        S_a = loadData(attribute, str(args.dataset))
        S += S_a
        M[attribute] = len(S_a)
        D[attribute] = args.delay[idx]
        idx += 1
    print(Color.GREEN + "OK" + Color.END)

    # data segmenting
    print("\t|- phase1: pre-processing ... ", end="")
    dataSegmenting(S)
    print(Color.GREEN + "OK" + Color.END)

    # extract evolving timestamps
    print("\t|- phase2: extracting evolving timestamps ... ", end="")
    thresholds = estimateThreshold(S, M, args.evoRate)
    extractEvolving(S, thresholds)
    print(Color.GREEN + "OK" + Color.END)

    # clustering
    print("\t|- phase3: clustering ... ", end="")
    C = clustering(S, args.distance)
    print(Color.GREEN + "OK" + Color.END)

    # CAP search
    start = time.time()
    print("\t|- phase4: cap search ... ", end="")
    CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
    print(Color.GREEN + "OK" + Color.END)
    end = time.time()

    # save the results into .pickle file
    with open("pickle/"+args.dataset+"/sensor.pickle", "wb") as pl:
        pickle.dump(S, pl)
    with open("pickle/"+args.dataset+"/attribute.pickle", "wb") as pl:
        pickle.dump(M, pl)
    with open("pickle/"+args.dataset+"/cluster.pickle", "wb") as pl:
        pickle.dump(C, pl)
    with open("pickle/"+args.dataset+"/cap.pickle", "wb") as pl:
        pickle.dump(CAPs, pl)
    with open("pickle/"+args.dataset+"/cap_count.pickle", "w") as pl:
        pl.write("{}\n".format(str(len(CAPs))))
    with open("pickle/"+args.dataset+"/threshold.pickle", "wb") as pl:
        pickle.dump(thresholds, pl)

    print("*found caps: {}".format(len(CAPs)))
    print("*search time: {} [m]".format((end-start)/60.0))

def assembler(args):

    print("*----------------------------------------------------------*")
    print("* Assembler is getting start ...")

    # load data on memory
    print("\t|- phase0: loading data ... ", end="")
    S = list()
    M = dict()
    D, idx = dict(), 0
    for attribute in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        attribute = attribute.strip()
        S_a = loadData(attribute, str(args.dataset))
        S += S_a
        M[attribute] = len(S_a)
        D[attribute] = args.delay[idx]
        idx += 1
    print(Color.GREEN + "OK" + Color.END)

    # data segmenting
    print("\t|- phase1: pre-processing ... ", end="")
    dataSegmenting(S)
    print(Color.GREEN + "OK" + Color.END)

    # extract evolving timestamps
    print("\t|- phase2: extracting evolving timestamps ... ", end="")
    thresholds = estimateThreshold(S, M, args.evoRate)
    extractEvolving(S, thresholds)
    print(Color.GREEN + "OK" + Color.END)

    # clustering
    print("\t|- phase3: clustering ... ", end="")
    C = clustering(S, args.distance)
    print(Color.GREEN + "OK" + Color.END)

    # CAP search
    start = time.time()
    print("\t|- phase4: cap search ... ", end="")
    CAPs = search("assembler", S, C, args.maxAtt, args.minSup, D)
    print(Color.GREEN + "OK" + Color.END)
    end = time.time()

    # save the results into .pickle file
    with open("pickle/"+args.dataset+"/sensor.pickle", "wb") as pl:
        pickle.dump(S, pl)
    with open("pickle/"+args.dataset+"/attribute.pickle", "wb") as pl:
        pickle.dump(M, pl)
    with open("pickle/"+args.dataset+"/cluster.pickle", "wb") as pl:
        pickle.dump(C, pl)
    with open("pickle/"+args.dataset+"/cap.pickle", "wb") as pl:
        pickle.dump(CAPs, pl)
    with open("pickle/"+args.dataset+"/threshold.pickle", "wb") as pl:
        pickle.dump(thresholds, pl)

    print("*found caps: {}".format(len(CAPs)))
    print("*search time: {} [m]".format((end - start) / 60.0))

def mocServer(args):

    cap_id = 0
    example = {"00202": "temperature",
               "00199": "temperature",
               "00197": "temperature",
               "00064": "temperature",
               "00203": "temperature",
               "00193": "temperature",
               "10029": "light",
               "10126": "light",
               "10171": "light",
               "10129": "light",
               "10099": "light"}

    with open("result/"+args.dataset+"/"+str(cap_id).zfill(5)+"_pattern.csv", "w") as outfile:
        outfile.write("id,attribute,pattern\n")
        for sensor_id, attribute in example.items():
            outfile.write(sensor_id+","+attribute+",1\n")

    with open("result/"+args.dataset+"/"+str(cap_id).zfill(5)+"_location.csv", "w") as outfile:
        outfile.write("id,attribute,lat,lon\n")
        for sensor_id, attribute in example.items():
            with open("db/" + args.dataset + "/location.csv", "r") as infile:
                for line in infile.readlines()[1:]:
                    _sensor_id, _atttribute, _lat, _lon = line.strip().split(",")
                    if _sensor_id == sensor_id:
                        outfile.write(line)

    with open("result/"+args.dataset+"/"+str(cap_id).zfill(5)+"_data.csv", "w") as outfile1:
        with open("result/" + args.dataset + "/" + str(cap_id).zfill(5) + "_data_filled.csv", "w") as outfile2:
            outfile1.write("id,attribute,lat,lon\n")
            outfile2.write("id,attribute,lat,lon\n")

            ids = dict()
            with open("db/"+args.dataset+"/data.csv", "r") as infile:
                outfile1.write("time")
                outfile2.write("time")
                for sensor_id in example.keys():
                    ids[sensor_id] = []
                    outfile1.write("," + sensor_id)
                    outfile2.write("," + sensor_id)
                outfile1.write("\n")
                outfile2.write("\n")

            for sensor_id in ids.keys():
                timestamp = []
                with open("db/"+args.dataset+"/data.csv", "r") as infile:
                    for line in infile.readlines()[1:]:
                        _sensor_id, _attribute, _time, _data = line.strip().split(",")
                        if _sensor_id == sensor_id:
                            ids[_sensor_id].append(_data)
                            timestamp.append(_time)

            for i in range(len(timestamp)):
                outfile1.write(timestamp[i])
                for sensor_id in ids.keys():
                    outfile1.write("," + ids[sensor_id][i])
                outfile1.write("\n")

            for sensor_id in ids:
                ids[sensor_id] = [np.nan if i == "null" else i for i in ids[sensor_id]]
                data = pd.Series(ids[sensor_id])
                data = data.fillna(method="ffill")
                data = data.fillna(method="bfill")
                ids[sensor_id] = list(data)

            for i in range(len(timestamp)):
                outfile2.write(timestamp[i])
                for sensor_id in ids.keys():
                    outfile2.write("," + ids[sensor_id][i])
                outfile2.write("\n")

def re_miscela(args):

    print("*----------------------------------------------------------*")
    print("* re-MISCELA is getting start ...")

    # load data on memory
    print("\t|- loading data ... ", end="")
    S = pickle.load( open("pickle/"+args.dataset+"/sensor.pickle", "rb"))
    C = pickle.load(open("pickle/"+args.dataset+"/cluster.pickle", "rb"))
    D, idx = dict(), 0
    for attribute in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        attribute = attribute.strip()
        D[attribute] = args.delay[idx]
        idx += 1
    print(Color.GREEN + "OK" + Color.END)

    # CAP search
    start = time.time()
    print("\t|- cap search ... ", end="")
    CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
    print(Color.GREEN + "OK" + Color.END)
    end = time.time()

    print("*found caps: {}".format(len(CAPs)))
    print("*search time: {} [m]".format((end-start)/60.0))

    # save the results into .pickle file
    with open("pickle/"+args.dataset+"/cap.pickle", "wb") as pl:
        pickle.dump(CAPs, pl)

def capAnalysis(args):

    # c = list()
    # S = pickle.load(open("tmp/00/{}/sensor.pickle".format(args.dataset), "rb"))
    # for cap_i in pickle.load(open("tmp/00/{}/cap.pickle".format(args.dataset), "rb")):
    #     tmp = list()
    #     loc = set()
    #
    #     if S[cap_i.getMember()[0]].getId() == "090064":
    #         for s_i in cap_i.getMember():
    #             sid = S[s_i].getId()
    #             loc.add(tuple(S[s_i].getLocation()))
    #             tmp.append(S[s_i].getId())
    #             tmp.append(cap_i.getPattern()[S[s_i].getAttribute()])
    #
    #         if len(list(loc)) == 1:
    #             c.append(tmp)
    #             print(tmp)
    #
    # S = pd.read_csv("db/{}/location.csv".format(args.dataset))
    # for c_i in list(c):
    #     print("--pattern--")
    #     print(S[S["id"] == int(c_i[0])])
    #     print(S[S["id"] == int(c_i[2])])
    #     if len(c_i) > 4:
    #         print(S[S["id"] == int(c_i[4])])
    #     print("-----------")

    a = set()
    S = pickle.load(open("tmp/00/{}/sensor.pickle".format(args.dataset), "rb"))
    for cap_i in pickle.load(open("tmp/00/{}/cap.pickle".format(args.dataset), "rb")):
        tmp = list()
        for s_i in cap_i.getMember():
            tmp.append(S[s_i].getId())
            tmp.append(cap_i.getPattern()[S[s_i].getAttribute()])
        a.add(tuple(tmp))

    l = [1, 2] + list(range(5, 13)) + [19, 20]
    for idx in l:
        b = set()
        S = pickle.load(open("tmp/{}/{}/sensor.pickle".format(str(idx).zfill(2), args.dataset), "rb"))
        for cap_i in pickle.load(open("tmp/{}/{}/cap.pickle".format(str(idx).zfill(2), args.dataset), "rb")):
            tmp = list()
            loc = set()
            for s_i in cap_i.getMember():
                loc.add(tuple(S[s_i].getLocation()))
                tmp.append(S[s_i].getId())
                tmp.append(cap_i.getPattern()[S[s_i].getAttribute()])

            # if len(loc) >= 2:
            #     b.add(tuple(tmp))

            if len(loc) == 1:
                b.add(tuple(tmp))

            # b.add(tuple(tmp))

        c = b - (a & b)
        # if len(c) == 0:
        #     print(str(idx).zfill(2), ":\tNone")
        # else:
        #     print(str(idx).zfill(2), ":\t", len(c))

        # S = pd.read_csv("db/{}/location.csv".format(args.dataset))
        # for c_i in list(c):
        #     print("--pattern--")
        #     print(S[S["id"] == int(c_i[0])])
        #     print(S[S["id"] == int(c_i[2])])
        #     if len(c_i) > 4:
        #         print(S[S["id"] == int(c_i[4])])
        #     print("-----------")

        A = pickle.load(open("tmp/{}/{}/attribute.pickle".format(str(idx).zfill(2), str(args.dataset)), "rb"))
        A = dict(zip(list(A.keys()), [0]*len(list(A.keys()))))
        S = pd.read_csv("db/{}/location.csv".format(args.dataset))
        for c_i in list(c):

            sid = set()
            sid.add(int(c_i[0][:2]))
            sid.add(int(c_i[2][:2]))
            if len(c_i) > 4:
                sid.add(int(c_i[4][:2]))
            if len(c_i) > 6:
                sid.add(int(c_i[6][:2]))
            if len(c_i) > 8:
                sid.add(int(c_i[8][:2]))

            for j in list(sid):
                A[list(A.keys())[j]] += 1

        print(A)

def exp_minSup(args):

    print("*----------------------------------------------------------*")
    print("* MISCELA is getting start ...")

    # load data on memory
    print("\t|- phase0: loading data ... ", end="")
    S = list()
    M = dict()
    D = dict()
    for attribute in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        attribute = attribute.strip()
        S_a = loadData(attribute, str(args.dataset))
        S += S_a
        M[attribute] = len(S_a)
        D[attribute] = 0
    print(Color.GREEN + "OK" + Color.END)

    # data segmenting
    print("\t|- phase1: pre-processing ... ", end="")
    dataSegmenting(S)
    print(Color.GREEN + "OK" + Color.END)

    # extract evolving timestamps
    print("\t|- phase2: extracting evolving timestamps ... ", end="")
    thresholds = estimateThreshold(S, M, args.evoRate)
    extractEvolving(S, thresholds)
    print(Color.GREEN + "OK" + Color.END)

    # clustering
    print("\t|- phase3: clustering ... ", end="")
    C = clustering(S, args.distance)
    print(Color.GREEN + "OK" + Color.END)

    psi = ["400", "450", "500", "550", "600"]
    with open("result/" + args.dataset + "/minSup.csv", "w") as outfile:
        outfile.write("minSup,assembler,miscela\n")

    for psi_i in psi:

        args.minSup = int(psi_i)

        # SCP search
        start = time.time()
        print("\t|- scp search (minSup = {}) ... ".format(psi_i), end="")
        CAPs = search("assembler", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        tau_a = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(tau_a/60.0))

        # CAP search
        start = time.time()
        print("\t|- cap search (minSup = {}) ... ".format(psi_i), end="")
        CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        tau_m = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(tau_m/60.0))

        # save the results
        with open("result/" + args.dataset + "/minSup.csv", "a") as outfile:
            outfile.write("{},{},{}\n".format(psi_i, str(tau_a), str(tau_m)))

def exp_maxAtt(args):

    print("*----------------------------------------------------------*")
    print("* MISCELA is getting start ...")

    # load data on memory
    print("\t|- phase0: loading data ... ", end="")
    S = list()
    M = dict()
    D = dict()
    for attribute in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        attribute = attribute.strip()
        S_a = loadData(attribute, str(args.dataset))
        S += S_a
        M[attribute] = len(S_a)
        D[attribute] = 0
    print(Color.GREEN + "OK" + Color.END)

    # data segmenting
    print("\t|- phase1: pre-processing ... ", end="")
    dataSegmenting(S)
    print(Color.GREEN + "OK" + Color.END)

    # extract evolving timestamps
    print("\t|- phase2: extracting evolving timestamps ... ", end="")
    thresholds = estimateThreshold(S, M, args.evoRate)
    extractEvolving(S, thresholds)
    print(Color.GREEN + "OK" + Color.END)

    # clustering
    print("\t|- phase3: clustering ... ", end="")
    C = clustering(S, args.distance)
    print(Color.GREEN + "OK" + Color.END)

    myu = len(list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()))
    myu = list(range(2, myu+1))
    with open("result/" + args.dataset + "/maxAtt.csv", "w") as outfile:
        outfile.write("maxAtt,assembler,miscela\n")

    for myu_i in myu:

        args.maxAtt = int(myu_i)

        # SCP search
        start = time.time()
        print("\t|- scp search (maxAtt = {}) ... ".format(myu_i), end="")
        CAPs = search("assembler", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        tau_a = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(tau_a/60.0))

        # CAP search
        start = time.time()
        print("\t|- cap search (maxAtt = {}) ... ".format(myu_i), end="")
        CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        tau_m = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(tau_m/60.0))

        # save the results
        with open("result/" + args.dataset + "/maxAtt.csv", "a") as outfile:
            outfile.write("{},{},{}\n".format(myu_i, str(tau_a), str(tau_m)))

def exp_evoRate(args):
    print("*----------------------------------------------------------*")
    print("* MISCELA is getting start ...")

    eps = ["0.3", "0.4", "0.5", "0.6", "0.7"]
    with open("result/" + args.dataset + "/evoRate.csv", "w") as outfile:
        outfile.write("evoRate,assembler,miscela\n")

    for eps_i in eps:
        args.evoRate = float(eps_i)

        # load data on memory
        print("\t|- phase0: loading data ... ", end="")
        S = list()
        M = dict()
        D = dict()
        for attribute in list(open("db/" + str(args.dataset) + "/attribute.csv", "r").readlines()):
            attribute = attribute.strip()
            S_a = loadData(attribute, str(args.dataset))
            S += S_a
            M[attribute] = len(S_a)
            D[attribute] = 0
        print(Color.GREEN + "OK" + Color.END)

        # data segmenting
        print("\t|- phase1: pre-processing ... ", end="")
        dataSegmenting(S)
        print(Color.GREEN + "OK" + Color.END)

        # extract evolving timestamps
        print("\t|- phase2: extracting evolving timestamps ... ", end="")
        thresholds = estimateThreshold(S, M, args.evoRate)
        extractEvolving(S, thresholds)
        print(Color.GREEN + "OK" + Color.END)

        # clustering
        print("\t|- phase3: clustering ... ", end="")
        C = clustering(S, args.distance)
        print(Color.GREEN + "OK" + Color.END)

        # SCP search
        start = time.time()
        print("\t|- scp search (evoRate = {}) ... ".format(eps_i), end="")
        CAPs = search("assembler", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        tau_a = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(tau_a / 60.0))

        # CAP search
        start = time.time()
        print("\t|- cap search (evoRate = {}) ... ".format(eps_i), end="")
        CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        tau_m = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(tau_m / 60.0))

        # save the results
        with open("result/" + args.dataset + "/evoRate.csv", "a") as outfile:
            outfile.write("{},{},{}\n".format(eps_i, str(tau_a), str(tau_m)))

def exp_delay(args):

    print("*----------------------------------------------------------*")
    print("* MISCELA is getting start ...")

    # load data on memory
    print("\t|- phase0: loading data ... ", end="")
    S = list()
    M = dict()
    D = dict()
    for attribute in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        attribute = attribute.strip()
        S_a = loadData(attribute, str(args.dataset))
        S += S_a
        M[attribute] = len(S_a)
        D[attribute] = 0
    print(Color.GREEN + "OK" + Color.END)

    # data segmenting
    print("\t|- phase1: pre-processing ... ", end="")
    dataSegmenting(S)
    print(Color.GREEN + "OK" + Color.END)

    # extract evolving timestamps
    print("\t|- phase2: extracting evolving timestamps ... ", end="")
    thresholds = estimateThreshold(S, M, args.evoRate)
    extractEvolving(S, thresholds)
    print(Color.GREEN + "OK" + Color.END)

    # clustering
    print("\t|- phase3: clustering ... ", end="")
    C = clustering(S, args.distance)
    print(Color.GREEN + "OK" + Color.END)

    # CAP search
    start = time.time()
    print("\t|- phase4: cap search ... ", end="")
    CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
    print(Color.GREEN + "OK" + Color.END)
    tau0 = time.time()-start

    print("*found caps: {}".format(len(CAPs)))
    print("*search time: {} [m]".format(tau0/60.0))

    print("*----------------------------------------------------------*")
    print("* re-MISCELA is getting start ...")

    with open("result/" + args.dataset + "/delay.csv", "w") as outfile:
        outfile.write("delay,-1,+1\n")

    for a_i in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
        a_i = a_i.strip()

        '''
        delay_att = -1
        '''
        D = dict()
        for a_j in list(open("db/"+str(args.dataset)+"/attribute.csv", "r").readlines()):
            a_j = a_j.strip()
            if a_j == a_i:
                D[a_j] = -1
            else:
                D[a_j] = 0
        print("\t", D)

        # CAP search
        start = time.time()
        print("\t|- cap search ... ", end="")
        CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        taum1 = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(taum1/60.0))

        '''
        delay_att = +1
        '''
        D = dict()
        for a_j in list(open("db/" + str(args.dataset) + "/attribute.csv", "r").readlines()):
            a_j = a_j.strip()
            if a_j == a_i:
                D[a_j] = +1
            else:
                D[a_j] = 0
        print("\t", D)

        # CAP search
        start = time.time()
        print("\t|- cap search ... ", end="")
        CAPs = search("miscela", S, C, args.maxAtt, args.minSup, D)
        print(Color.GREEN + "OK" + Color.END)
        taup1 = time.time() - start

        print("\t*found caps: {}".format(len(CAPs)))
        print("\t*search time: {} [m]".format(taup1/ 60.0))

        # save the results
        with open("result/" + args.dataset + "/delay.csv", "a") as outfile:
            outfile.write("{},{},{},{}\n".format(a_i, str(taum1), str(tau0), str(taup1)))