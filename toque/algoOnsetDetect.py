import sys
from essentia import Pool, array
from essentia.standard import *
import matplotlib.pyplot as plt


def algoOnsetDetection(wavfile):

    # Copyright (C) 2006-2016  Music Technology Group - Universitat Pompeu Fabra
    #
    # This file is part of Essentia
    #
    # Essentia is free software: you can redistribute it and/or modify it under
    # the terms of the GNU Affero General Public License as published by the Free
    # Software Foundation (FSF), either version 3 of the License, or (at your
    # option) any later version.
    # http://essentia.upf.edu/documentation/reference/streaming_OnsetDetection.html

    # Onset detection consists of two main phases:

    #  1- we need to compute an onset detection function, which is a function
    #     describing the evolution of some parameters, which might be representative
    #     of whether we might find an onset or not
    #  2- performing the actual onset detection, that is given a number of these
    #     detection functions, decide where in the sound there actually are onsets
    #############################################################################

    filename=wavfile

    # we're going to work with a file specified as an argument in the command line
    try:
        filename = sys.argv[1]
    except:
        print "usage:", sys.argv[0], "<audiofile>"

    # don't forget, we can actually instantiate and call an algorithm on the same line!

    audio = MonoLoader(filename=filename)()

    # Phase 1: compute the onset detection function

    od1 = OnsetDetection(method='flux')
    od2 = OnsetDetection(method='complex')

    # let's also get the other algorithms we will need, and a pool to store the results

    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = Pool()

    # let's get down to business
    print 'Computing onset detection functions...'
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.flux', od1(mag, phase))
        pool.add('features.complex', od2(mag, phase))

    # Phase 2: compute the actual onsets locations
    onsets = Onsets()
    onsets_flux = onsets(array([pool['features.flux']]), [1])
    onsets_complex = onsets(array([pool['features.complex']]), [1])

    # mark the 'hfc' onsets:
    marker = AudioOnsetsMarker(onsets=onsets_flux, type='beep')
    marked_audio = marker(audio)
    #MonoWriter(filename='onsets_flux.wav')(marked_audio)
    #plt.plot(marker(audio))
    #plt.show()

    # mark the 'complex' onsets:
    #marker = AudioOnsetsMarker(onsets=onsets_complex, type='beep')
    #mark the audio and make it an mp3 file, all in 1 line, just because we can!
    #MonoWriter(filename='onsets_complex.mp3', format='mp3')(marker(audio))
    #plt.plot(marker(audio))
    #plt.show()

    return onsets_flux, onsets_complex

