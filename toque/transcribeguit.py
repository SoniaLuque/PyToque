from toque import utils
from . import *
import time
import os
import matplotlib.pyplot as plt




def AST(filename, acc=True, tmin=12,method=2,tone='default',transposed=0):
    # display current file
    print ('transcribing guitar %s ...') % filename
    # time tic
    startTime = time.time()
    # load audio file
    audio = loadWaveAudio(filename)

    ############################# CHANNEL SELECTION #################################

    if audio['numChannels'] == 2:
        print('channel selection')
        channel = algoChannelSelection(audio['left'],audio['right'])
        if channel == 0:
            samples = audio['left']
        else:
            samples = audio['right']
    else:
        samples = audio['left']

    ############################ VOCAL MELODY EXTRACTION ##############################

    print('vocal melody extraction')
    if acc:
        # predominant melody extraction
        f0 = algoF0Acc(samples)

    else:
        # monophonic melody extraction
        f0 = algoF0Solo(samples)

    ########################## CONTOUR FILTERING ####################################
    if acc:
        print('contour filtering')
        f0g = algoContourFiltering(f0,samples)
    ########################### GUITAR EXTRACTION #######################################
    if acc:
        if audio['numChannels'] == 2:
            print('Falseta Extraction')
            audioguitL, audioguitR, timefalsetas = algoGuitarExtraction(f0g,tmin, audio['left'],audio['right'])

            #falsetas .wav's exportation on each channel independently

            namewav = filename[0:len(filename) - 4] + 'L_falsetas.wav'
            scipy.io.wavfile.write(namewav, 44100, audioguitL)
            namewav = filename[0:len(filename) - 4] + 'R_falsetas.wav'
            scipy.io.wavfile.write(namewav, 44100, audioguitR)

            #txt file with the time corresponding to each falseta (in sec) : [start1,end1,start2,end2,...]

            name= filename[0:len(filename) -4]+'_timefalsetas.txt'
            np.savetxt(name,timefalsetas,fmt='%.1d')

            # Stereo to mono (mean of the 2 channels to work better with the transcription)
            gLen = min([len(audioguitL), len(audioguitR)])
            audioguitL = audioguitL[0:gLen]
            audioguitR = audioguitR[0:gLen]

            monoguit = np.array(audioguitR) + np.array(audioguitL)
            monoguit=monoguit/2

            wavmonofile = 'monoguit.wav'
            scipy.io.wavfile.write(wavmonofile, 44100, monoguit)

        if audio['numChannels'] == 1:
            audioguit, timefalsetas = algoGuitarExtractionMono(f0g, samples, tmin)

            #falsetas .wav's exportation
            namewav = filename[0:len(filename) - 4] + 'M_falsetas.wav'
            scipy.io.wavfile.write(namewav, 44100, audioguit)

            wavmonofile = 'monoguit.wav'
            scipy.io.wavfile.write(wavmonofile, 44100, audioguit)
            monoguit=audioguit

            # txt file with the time corresponding to each falseta (in sec) : [start1,end1,start2,end2,...]
            name= filename[0:len(filename) -4]+'_timefalsetas.txt'
            np.savetxt(name,timefalsetas,fmt='%.1d')

    print('Falseta extraction done')


    ##############################   TRANSCRIPTION    #################################
    #                                                                                 #
    # monoguit= samples of falseta file                                               #
    # wavmonofile= audio file 'monoguit.wav'                                          #
    #                                                                                 #
    ###################################################################################

    ############################## GUITAR MELODY EXTRACTION ##############################

    print('Guitar melody extraction')
    if not acc:
        wavmonofile=filename
        monoguit=samples

    if acc:
        # Klapuri Multipitch tracker (ESSENTIA)
        guitF0 = klapuri(monoguit)

    else:
        # Klapuri Pitch tracker (ESSENTIA)
        guitF0 = klapuriMono(monoguit)

    ####################### ONSET AND OFFSET DETECTION // NOTE SEGMENTATION ################

    print('Onset and offset detection')

    _onsetsflux,_onsetscomplex = algoOnsetDetection(wavmonofile)

    onsets, offsets, onsetsf0, offsetsf0,segmentsMG = Segmentation(_onsetsflux,monoguit)

    ################################ PITCH ESTIMATION ####################################

    print('Pitch estimation')
    notes,MyMIDI =algoPitchSegments(guitF0, onsetsf0, offsetsf0, monoguit, segmentsMG,filename, acc,method)

    ################################ POST-PROCESSING ####################################

    print('note post-processing')
    algoPostProcessTranscription(notes,tone,transposed)

    ########################### WRITE CSV FILE AND MIDI FILE ############################

    writeToCsv(notes,filename[0:len(filename)-3]+'notes.csv')

    namemidi = filename[0:len(filename) - 4] + '_MIDI.mid'
    with open(namemidi, "wb") as output_file:
        MyMIDI.writeFile(output_file)

    #display success & elapsed time

    print ('Done!')
    print('Elapsed time: %f seconds') % (time.time()-startTime)

    return



def transcribeguit(filename, acc = True, recursive = False, tmin=6, method=2,tone='default',transposed=0):
    '''
    TOQUE: Automatic Note-Level Transcription of Flamenco Guitar.

    The algorithm creates a .csv file containing the estimated note events corresponding to the
    guitar falseta melody, where each row corresponds to a note event as follows:

    < note onset [seconds] >, < note duration [seconds] >, < MIDI pitch value >;

    Input is a .wav audio file with a sample rate of 44.1kHz and a bit depth of 16 Bits. Otherwise
    an error is raised.

    If an f0 file is provided, the filename should be identical to the audio file, i.e. for test.wav,
    a file named test.csv should be located in the same folder. The required format matches the output
    of sonic visualizer (www.sonicvisualizer.org) and sonic annotator (http://www.vamp-plugins.org/sonic-annotator/):
    The first column contains the time instants in seconds and the second column holds the corresponding
    pitch values in Hz. Zero or negative pitch values indicate unvoiced frames. Hop size is restricted to
    128 samples for a sample rate of 44.1 kHz.

    In recursive mode, the algorithm transcribes all .wav files in the provided folder path.

    For accompanied recordings (i.e. vocals + guitar), an additional contour filtering stage is
    applied. In this case, set acc = True.

    If you use this code for research purposes, please cite [1].

    :param filename: <string> path to the input file or folder.
    :param acc: <bool> True if accompaniment is expected, False for a cappella recordings.
    :param f0_file: <bool> True if a .csv file containing the fundamental frequency is provided.
    :param recursive: <bool> True for folder recursion.
    :return: NONE - <filename>.notes.csv written to the same folder
    '''

    # transcribe a single file
    if not recursive:
        # sanity check
        if not os.path.isfile(filename):
            print ("ERROR: file not found!")
            return
        # transcription
        AST(filename, acc, tmin,method,tone,transposed)

    # recursive mode
    else:
        # sanity check
        if not os.path.isdir(filename):
            print ("ERROR: folder not found!")
            return
        # get list of all wav files
        files = []
        for file in os.listdir(filename):
            if file.endswith(".wav"):
                if not file.endswith("falsetas.wav"):
                    files.append(file)
        if not filename.endswith('/'):
            filename = filename + '/'
        for file in files:
            AST(filename+file, acc, tmin,method,tone,transposed)
    return


