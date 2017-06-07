from utils import findSegments0
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile


def algoGuitarExtraction(f0g, tmin,audioL,audioR):

    ''' Algorithm to filter out pitch contour segments which originate from the vocals

    :param f0g: Estimated vocal melody with the guitar parts turned to 0, computed with hopSize 128 at fs 44.1kHz
    :param audioSamples signal with fs 44.1kHz
    :param tmin: Minimum time to consider a segment as a falseta
    :return: audioguit: Audio signal of falsetas extraction
    :return: .txt with the start and the end time value of falsetas in the whole song
    '''

    #init
    guitsamplesR=[]
    guitarra=[] #start and end values of falsetas in f0 [samples]-> [start1 end1 start2 end2 ...]
    guitsamples=[] #start and end values of falsetas in audioSamples[samples]
    #intersamples= 132300
    #intervalo=np.zeros(intersamples)
    timefalsetas=[] #start and end values of falsetas [sec]
    smin=tmin*44100/128

    #Finding 0's segments biggers than [tmin]*fs in f0g -> FALSETAS

    startG, endG = findSegments0(f0g)

    for i in range(0,len(startG)):
        vguit = sum(f0g[startG[i]:endG[i]])
        if vguit==0 and (endG[i]-startG[i])>smin:

            guitarra.append(startG[i])
            guitarra.append(endG[i])

    #LEFT CHANNEL

    # We relate the previous segments with audioSamples to extract the falsetas from the original audio.
    # f0g->audioSamples i+i*128

    for i in range(0,len(guitarra),2): #step=2 due to the format: [start1 end1 start2 end2 ...]
        auxistart= guitarra[i] + guitarra[i]*128
        auxiend= guitarra[i+1] + guitarra[i+1]*128
        guit= audioL[auxistart+88200:auxiend-88200] #*

        guitsamples.append(guit)
        #guitsamples.append(intervalo)

        falsetastart = (auxistart+88200) / 44100
        falsetaend = (auxiend-88200) / 44100

        timefalsetas.append(falsetastart)
        timefalsetas.append(falsetaend)
    timefalsetas=np.array(timefalsetas)
    timefalsetas=np.split(timefalsetas,len(timefalsetas)/2)



    audioguitL = np.hstack(guitsamples)


    #RIGHT CHANNEL

    for i in range(0,len(guitarra),2): #step=2 due to the format: [start1 end1 start2 end2 ...]
        auxistart= guitarra[i] + guitarra[i]*128
        auxiend= guitarra[i+1] + guitarra[i+1]*128
        guit= audioR[auxistart+88200:auxiend-88200]

        guitsamplesR.append(guit)
        #guitsamplesR.append(intervalo)


    audioguitR = np.hstack(guitsamplesR)

    #plt.plot(audioguit)
    #plt.show()
    return audioguitL,audioguitR, timefalsetas

def algoGuitarExtractionMono(f0g, audioSamples, tmin):

    ''' Algorithm to filter out pitch contour segments which originate from the vocals

    :param f0g: Estimated vocal melody with the guitar parts turned to 0, computed with hopSize 128 at fs 44.1kHz
    :param audioSamples signal with fs 44.1kHz
    :return: audioguit: Audio signal of falsetas extraction
    :return: .txt with the start and the end time value of falsetas in the whole song
    '''


    #plt.plot(f0g)
    #plt.show()

    #init

    guitarra=[] #start y end de las falsetas en samples de f0 [start1 end1 start2 end2 ...]
    guitsamples=[] #start y end de las falsetas en samples de audioSamples
    intersamples= 132300 #muestras 0 entre falsetas, 3 segundos modificables
    intervalo=np.zeros(intersamples)
    timefalsetas=[] #start y end de las falsetas en segundos
    smin=tmin*44100/128

    # Finding 0's segments biggers than [tmin]*fs in f0g -> FALSETAS

    startG, endG = findSegments0(f0g)

    for i in range(0,len(startG)):
        vguit = sum(f0g[startG[i]:endG[i]])
        if vguit==0 and (endG[i]-startG[i])>smin:

            guitarra.append(startG[i])
            guitarra.append(endG[i])

    # We relate the previous segments with audioSamples to extract the falsetas from the original audio.
    # f0g->audioSamples i+i*128

    for i in range(0,len(guitarra),2): #step=2 ya que el formato es [start1 end1 start2 end2 ...]
        auxistart= guitarra[i] + guitarra[i]*128
        auxiend= guitarra[i+1] + guitarra[i+1]*128
        guit= audioSamples[auxistart+88200:auxiend-88200]

        guitsamples.append(guit)
        #guitsamples.append(intervalo)

        falsetastart = (auxistart+88200) / 44100
        falsetaend = (auxiend-88200) / 44100

        timefalsetas.append(falsetastart)
        timefalsetas.append(falsetaend)
    timefalsetas = np.array(timefalsetas)
    timefalsetas = np.split(timefalsetas, len(timefalsetas) / 2)

    audioguit = np.hstack(guitsamples)


    #plt.plot(audioguit)
    #plt.show()
    return audioguit, timefalsetas
