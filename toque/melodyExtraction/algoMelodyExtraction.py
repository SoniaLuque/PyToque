import numpy
from pylab import *
import sys
from essentia import Pool, array
from essentia.standard import *


def algoF0Solo(samples):

    '''
    Wrapper for the python bindings of the ESSENTIA implementation of the MELODIA monophonic melody extraction
    algorithm: Estimates a pitch contour from the samples of a monophonic recording with fs 44.1 kHz.
    J. Salamon and E. Gomez, Melody extraction from polyphonic music
    signals using pitch contour characteristics. IEEE Transactions on Audio,
    Speech and Language Processing, vol. 20, no. 6, 2011, pp. 1759-1770.

    :param samples: audio samples with fs 44.1 kHz
    :return: f0: estimated fundamental frequency contour with hopSize 128 at fs 44.1kHz
    '''

    # PARAMETERS
    fs = 44100
    fmin = 120.0
    fmax = 720.0
    wSize = 1024
    hSize = 128

    # extract f0 using ESSENTIA
    input = essentia.array(samples)
    pitchTracker = PitchMelodia(frameSize = wSize, hopSize = hSize, minFrequency = fmin, maxFrequency = fmax, sampleRate = fs)
    f0, pitchConf = pitchTracker(input)

    return f0


def algoF0Acc(samples):

    '''
    Wrapper for the Python bindings of the ESSENTIA implementation of the MELODIA predominant melody extraction
    algorithm: Estimates a pitch contour from the samples of a polyphonic recording with fs 44.1 kHz.

    J. Salamon and E. Gomez, Melody extraction from polyphonic music
    signals using pitch contour characteristics. IEEE Transactions on Audio,
    Speech and Language Processing, vol. 20, no. 6, 2011, pp. 1759-1770.

    :param samples: audio samples with fs 44.1 kHz
    :return: f0: estimated fundamental frequency of the predominant melody with hopSize 128 at fs 44.1kHz
    '''

    # PARAMETERS
    fs = 44100
    fmin = 120.0
    fmax = 720.0
    vTol = 0.2
    wSize = 1024
    hSize = 128

    # extract f0 using ESSENTIA
    input = essentia.array(samples)
    pitchTracker = PredominantPitchMelodia(frameSize = wSize, hopSize = hSize, minFrequency = fmin, maxFrequency = fmax, sampleRate = fs, voicingTolerance = vTol, voiceVibrato = True, filterIterations=10)
    f0, pitchConf = pitchTracker(input)

    return f0

def algoGuitPoliF0(samples):


    guitTrack=[]
    # PARAMETERS
    fs = 44100
    fmin = 80
    fmax = 1000
    vTol = 0.2
    wSize =2048
    hSize = 128

    # extract f0 using ESSENTIA
    input = essentia.array(samples)
    pitchTracker = MultiPitchMelodia(minFrequency=20, maxFrequency=2500,frameSize = wSize,minDuration=50 )
    guitF0 = pitchTracker(input)


    for i in range(0, len(guitF0)):
        ind = guitF0[i][0]
        guitTrack.append(ind)

    return guitTrack

def algoGuitMonoF0(samples):

     # PARAMETERS
    fs = 44100
    fmin = 80
    fmax = 1000
    wSize = 2048
    hSize = 128

    # extract f0 using ESSENTIA
    input = essentia.array(samples)
    pitchTracker = PitchMelodia(frameSize = wSize, hopSize = hSize, minFrequency = fmin, maxFrequency = fmax, sampleRate = fs)
    guitf0, pitchConf = pitchTracker(input)

    return guitf0

def klapuri(samples):

    # Wrapper for the Python bindings of the ESSENTIA implementation of the MultiPitchKlapuri:
    # This algorithm estimates multiple pitch values corresponding to the melodic lines present in
    # a polyphonic music signal
    #
    # A. Klapuri, "Multiple Fundamental Frequency Estimation by Summing Harmonic Amplitudes "
    # International Society for Music Information Retrieval Conference (2006).
    #
    # Assuming the guitar line as a polifonic melodic line, here we take all the values within
    # the guitar freq. range for each sample (80-750Hz). This frequency range is not limited as a parameter of klapuri
    # because of a subsequent sincronization issue. Therefore, we will descart later if it is out of the guitar range.
    #
    # :param samples: audio samples with fs 44.1 kHz
    # :return: guitF0: the estimated pitch values [Hz]

    guitTrack=[]
    input=essentia.array(samples)
    pitchTracker=MultiPitchKlapuri(maxFrequency=2500,minFrequency=20, magnitudeThreshold=50, numberHarmonics=10)
    guitF0 = pitchTracker(input)


    for i in range (0,len(guitF0)):
        index=[]
        for j in range(0, len(guitF0[i])):
            if len(guitF0[i])==1:
                indexa = guitF0[i][0]
                index.append(indexa)
                break

            if 80<guitF0[i][j]<750:
                indexa = guitF0[i][j]
                index.append(indexa)
            else:
                continue

        if len(index)==0:
            indexa = guitF0[i][0]
            index.append(indexa)

        guitTrack.append(index)

    for p in range(0,len(guitTrack)):
        guitTrack[p] = np.array(guitTrack[p])
    return guitTrack

def klapuriMono(samples):

    # Wrapper for the Python bindings of the ESSENTIA implementation of the MultiPitchKlapuri
    # A. Klapuri, Multiple Fundamental Frequency Estimation by Summing Harmonic Amplitudes
    # International Society for Music Information Retrieval Conference (2006)
    #
    # In this case, we only take the first Hz value of each subsegment,assuming the input file
    # as a monophonic melodic line. Also we restrict the frequency range between 80-750,
    # corresponding to the guitar freq range
    # :param samples audio samples with fs 44.1 kHz
    # :return guitF0 the estimated pitch values Hz

    guitTrack=[]
    input=essentia.array(samples)
    pitchTracker=MultiPitchKlapuri(maxFrequency=750,minFrequency=80, magnitudeThreshold=50, numberHarmonics=10)
    guitF0 = pitchTracker(input)

    for i in range (0,len(guitF0)):
        ind= guitF0[i][0]
        guitTrack.append(ind)


    return guitTrack


