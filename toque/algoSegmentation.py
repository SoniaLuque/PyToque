from utils import findSegments00, rmsSignal, energyFunction
import numpy as np

def Segmentation(onsets,monoguit):

    segments=[]
    offsets =[]
    thres = 44100 * 0.16

    #Onsets[s]-> Onset[samples]
    onsetssamples = onsets * 44100

    # Here we separate by segments [onset1 to onset2-1] and relate each one with monoguit original samples
    #later, we will determine the offset

    for i in range(0, len(onsetssamples)-1):

        auxistart=int(onsetssamples[i])
        auxiend=int(onsetssamples[i+1]-1)
        allsegment=monoguit[auxistart:auxiend]

        segments.append(allsegment)

    #Then, we compute the RMS/ENERGY in blocks of 256 samples of every segment.

    rmslist=[]
    energylist=[]
    for p in range(0, len(segments)):
        st = segments[p]

        for w in range(0, len(st)-256,255):
            subsegment=st[w:w+256]
            #rms=rmsSignal(subsegment)
            rms=energyFunction(subsegment)
            rmslist.append(rms)
            rmslista=np.hstack(rmslist)
        energylist.append(rmslista)
        rmslist=[]

    ##### OFFSET DETECTION : Analysing each segments in order to find the most accurate offset ########
    #
    # METHOD 1: We set a minimum time value according to the guitar attack time : 0.25s (11025 samples)
    # So, if the subsegment has less samples than this minimum time, we take the last sample of
    # this subsegment as a offset.
    #
    ###################################################################################################


    for i in range(0, len(segments)):
        startC = findSegments00(segments[i])

        if len(segments[i])<thres:

            if i==len(segments):
                ind=onsetssamples[i]
                ind2=len(monoguit)
                index=ind+ind2
                startP = index
                offsets.append(int(startP))

            if i!=len(segments):

                ind=onsetssamples[i+1]
                index=ind-1
                startP = index
                offsets.append(int(startP))


        # METHOD 2: if the subsegment is bigger than 0.25s, we analyse:
        #
        # 2,1 If there is not any segment of consecutive 0's , ergo a definite offset, we set it
        # defining a energy threshold (10% of the maximum value of each subsegment). The first 256-block
        # of each subsegment that has a energy value corresponding equal or lower to the thr, will be selected
        # as a offset.

        if len(segments[i])>=thres and len(startC) == 0:
            #iii=energylist[i]
            maxenergy= np.amax(energylist[i])
            for k in range(0, len(energylist[i])):
                if energylist[i][k]==maxenergy:
                    pos=k
                    break
            thr=0.1*maxenergy

            for t in range (pos,len(energylist[i])):
                if energylist[i][t]<thr: #or t==len(energylist[i]):
                    ind=energylist[i][t]
                    offsetEnergy=t*256+onsetssamples[i]
                    break
                else:
                    offsetEnergy = t*256+onsetssamples[i]
            offsets.append(int(offsetEnergy))

        # 2.2 If all the energy values are bigger than the thr, we choose it in the same way of method 1.
        # Finally, if we find a consecutive zeros segment (at least 3), we will pick out the first one as a offset.

        if len(startC)!=0 and len(segments[i])>=thres:
            for j in range (0, len(startC)):
                if startC[j]>thres:

                    index = onsetssamples[i]
                    startV= startC[j]+index
                    break

                if startC[j]<=thres:
                    if i == len(segments):
                        ind = onsetssamples[i]
                        ind2 = len(monoguit)
                        index = ind + ind2
                        startV = index


                    if i != len(segments):
                        ind = onsetssamples[i + 1]
                        index = ind - 1
                        startV = index

            offsets.append(int(startV))


    last=len(monoguit)-1
    offsets.append(int(last))

    onsetarray = np.asarray(onsetssamples)
    offsetarray = np.asarray(offsets)

    # SCALING onsets and offsets in order to evaluate the guitF0 samples(HopSize= 128)
    onsetsf0 = []
    offsetsf0 = []

    for i in range(0,len(onsetarray)):

        oni=onsetarray[i]/128
        ofi=int((offsetarray[i]/float(128)))
        if oni==ofi:
            ofix=ofi+1
            onsetsf0.append(oni)
            offsetsf0.append(ofix)
        if oni!=ofi:
            onsetsf0.append(oni)
            offsetsf0.append(ofi)

    onsetsf0 = np.asarray(onsetsf0)
    offsetsf0 = np.asarray(offsetsf0)

    return onsetarray, offsetarray, onsetsf0, offsetsf0, segments