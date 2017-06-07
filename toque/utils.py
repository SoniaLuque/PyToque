''' Various auxiliary functions '''
from numpy import ones, convolve, array, log10, multiply, divide, hanning, r_
from essentia.standard import *

def movingAverage(input,length):

    '''
    Moving average filter.
    :param input: input array
    :param length: filter length
    :return: filtered signal
    '''

    x = array(input)
    s=r_[x[length-1:0:-1],x,x[-1:-length:-1]]
    w = hanning(length)

    return convolve(w/w.sum(),s,mode='valid')

def movingAverageBin(input,length):

    """
    Moving average filter (alternative implementation).
    :param input: input array
    :param length: filter length
    :return: filtered signal
    """

    length = min(length,len(input))
    window = ones(int(length))/float(length)

    return convolve(input, window, 'same')


def convertToCents(_input, fRef):

    '''
    Covert a pitch sequence in Hz to cents relative to a given reference frequency
    :param _input: input sequence in Hz
    :param fRef: reference frequency
    :return: sequence in cents
    '''
    input = array(_input,dtype=float)
    input = divide(input,fRef)
    input = log10(input)
    output = multiply(input, 1200*3.32204)

    return output

def findSegments(f0):

    '''
    Finds sections of consecutive voiced frames in a fundamental frequency contour.
    :param f0: fundamental frequency contour with hop size 128 at fs 44.1kHz
    :return: startC: section start indices, endC: section end indices
    '''
    startC = []
    endC = []
    if f0[0]>0:
        startC.append(0)
    for i in range(0,len(f0)-1):
        if (abs(f0[i+1]) > 0) and (abs(f0[i])<=0):
            startC.append(i+1)
        if (abs(f0[i+1]) <= 0) and (abs(f0[i]>0)):
            endC.append(i)

    if len(endC) < len(startC):
        endC.append(len(f0))

    return startC, endC

def findSegments0(f00):

    '''
    Finds sections of consecutive voiced frames in a fundamental frequency contour.
    :param f0: fundamental frequency contour with hop size 128 at fs 44.1kHz
    :return: startC: section start indices, endC: section end indices
    '''
    startG = []
    endG = []
    if f00[0]==0:
        startG.append(0)
    for i in range(0,len(f00)-1):
        if (abs(f00[i+1]) == 0) and (abs(f00[i])>0):
            startG.append(i+1)
        if (abs(f00[i+1]) > 0) and (abs(f00[i]==0)):
            endG.append(i)

    if len(endG) < len(startG):
        endG.append(len(f00))

    return startG, endG

def findSegments00(f00):
    '''
    # Finds sections of 3 consecutive 0's in a vector.
    :param input: input array
    :return: the first 0 of the 0-array

    '''
    startG = []
    for i in range(0,len(f00)-1):
        if (abs(f00[i]) == 0) and (abs(f00[i+1])==0)and (abs(f00[i+2])==0):
            startG.append(i)
            break

    return startG

def rmsSignal(samples):
    '''
    Copyright (C) 2006-2016  Music Technology Group - Universitat Pompeu Fabra
    RMS is part of Essentia
    :param input: input array
    :return: The Root Mean Square value of the input
    '''

    input = essentia.array(samples)
    rmsMethod = RMS()
    rmsValue = rmsMethod(input)

    return rmsValue

def energyFunction(samples):
    '''
    Copyright (C) 2006-2016  Music Technology Group - Universitat Pompeu Fabra
    Energy is part of Essentia
    :param input: input array
    :return: The Energy value of the input
    '''
    input = essentia.array(samples)
    rmsMethod = Energy()
    energyValue = rmsMethod(input)

    return energyValue

def bpmDetector(samples):

    '''
    Copyright (C) 2006-2016  Music Technology Group - Universitat Pompeu Fabra
    PerceivalBmpEstimator is part of Essentia
    :param input: input array
    :return: The tempo estimation [bpm]


    Percival, G., & Tzanetakis, G. (2014). Streamlined tempo estimation based on autocorrelation
    and cross-correlation with pulses.
    '''

    input= essentia.array(samples)
    bpmDetect=PercivalBpmEstimator()
    bpm=bpmDetect(input)

    return bpm


def adjustScale(pitches,scale):
    '''
    # Rescaling MIDI notes:
    :param pitches: MIDI notes to adjust
    :param scale: reference scale (MIDI)
    :return: MIDI notes array rescaled

    '''

    for i in range(0,len(pitches)):
        for j in range(0,len(scale)):
            x=pitches[i]
            y=scale[j]
            if x==y:
                aux='1'
                break
            else:
                aux='0'
                continue
        if aux=='0':
            pitches[i]=pitches[i]-1

    return pitches