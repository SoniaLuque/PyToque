from numpy import array, histogram, log2
import numpy as np
from matplotlib.pylab import hist, show
import matplotlib.pyplot as plt
from midiutil import MIDIFile
from utils import rmsSignal, bpmDetector, energyFunction, convertToCents



def algoPitchSegments(f0,on,off,samples,segmentsMG,filename,acc,method):

    '''
    In this section, we are going to define each subsegment as a note, which contains the time, duration,
    pitch and energy value. Later, in the postprocessing module, all of these parameters will be
    stored in a .csv file, and also in a MIDI file.

    The method used if the accompaniment is expected or not, will be different. If not, the algorithm will be
    easier due to the assumation that the input file will contain a monophonic melodic line , so we only
    will have one note for each subsegment. Otherwise, we can obtain, two simultaneous notes if both are
    present in the whole subsegment.

    :param f0 melodic line extracted by klapuri
    :param onsets and offsets
    :param samples of falsetas audio
    :param segmentsMG which contains the segments of the falsetas audio
    :param acc
    :return notes
    :return MIDI file
    '''
    # plt.hist(f0, len(f0))
    # plt.title("Histogram")
    # plt.show()

    #init
    hp=128
    fs=44100
    notes=[]
    segments=[]
    segments1=[]
    segments2=[]
    #fT=82.40
    fT=440
    midref=69#reference tuning of guitar (E2)

    #Converting to cents and sorting the frequencies that are present in each segment.
    if not acc:
        for i in range(0, len(on)):
            seg=f0[int(on[i]):int(off[i])]
            #for j in range(0, len(seg)):
            #    seg[j]=(seg[j])
            seg=convertToCents(seg,fT)
            segsort=sorted(seg)
            segments.append(segsort)

        segments=np.asarray(segments)
        cont=0
        for p in range(0, len(segments)):
            if len(segments[p])!=0:
                cont=cont+1
            else:
                cont=cont+0

    #Sorting the frequencies. We can obtain two simultaneous notes if both are present
    #in the whole subsegment.
    if acc:
        for i in range(0, len(on)):
            conti=0
            seg=f0[int(on[i]):int(off[i])]
            prim = np.zeros(len(seg))
            segun = np.zeros(len(seg))

            for j in range(0, len(seg)):
                cont=len(seg[j])
                if cont>1:
                    conti=conti+1
                else:
                    continue

            if len(seg)==conti:
                for j in range(0, len(seg)):
                    prim[j]=convertToCents(seg[j][0],fT)
                    segun[j]=convertToCents(seg[j][1], fT)
            else:
                for j in range(0, len(seg)):
                    prim[j] = convertToCents(seg[j][0],fT)
                    segun[j] = 0

            segsort1=sorted(prim)
            segsort2=sorted(segun)
            segments1.append(segsort1)
            segments2.append(segsort2)

        segments1=np.asarray(segments1)
        segments2 = np.asarray(segments2)

        cont=0
        for p in range(0, len(segments1)):
            if len(segments1[p])!=0:
                cont=cont+1
            else:
                cont=cont+0

    # Computing the energy/RMS of every subsegment and clipping it between 40-100, related to volume of the MIDI file

    listRms=[]
    for j in range(0,cont-1):
        seg_energy = segmentsMG[j]
        energyseg = energyFunction(seg_energy)
        listRms.append(energyseg)

    b=np.clip(listRms,40,100)

    # Here we detect de BPM of the whole audio file, to can include in the MIDI file
    bpm = bpmDetector(samples) #ESSENTIA
    track = 0
    channel = 0
    time = 0
    tempo = bpm  # In BPM

    # Creating the MIDI file
    MyMIDI = MIDIFile(1)  # One track, defaults to format 1
    MyMIDI.addTempo(track, time, tempo)

    for j in range(0,cont-1):

        if acc:
            ################################  METODO MEDIANA ###############################
            if method==1:
                if len(segments1[j]) % 2 == 0:
                    n = len(segments1[j])
                    segj=segments1[j]
                    mediana = (segj[n / 2 - 1] + segj[n / 2]) / 2
                else:
                    segj = segments1[j]
                    mediana = segj[len(segj) / 2]

                mPitch = mediana
                thr = mediana

            ############################## METODO HISTOGRAMA ###############################
            if method==2:
                x1=np.min(segments1[j])
                x2=np.max(segments1[j])
                if x1==x2:
                    x2=x2+1
                hist=histogram(segments1[j], np.arange(x1,x2,1))
                if len(hist[0])!=0:
                    pos = max(hist[0])
                    for k in range(0, len(hist[0])):
                        if hist[0][k] == pos:
                            ind = k
                            break
                    local_hist = hist[1][ind]
                    mPitch = local_hist
                    thr = local_hist
                else:
                    local_hist = hist[1][0]
                    mPitch = local_hist
                    thr = local_hist

            if convertToCents(80,fT) < mPitch < convertToCents(750,fT):
                freq_value = fT * pow(10.0, float(mPitch) / (1200.0 * 3.322038403))
                pitch_value = round(12 * log2(freq_value / fT)) + midref
                #mPitch= round(12 * log2(mPitch/fT)) + 40 #E midi note value
                sTime = on[j] * hp/float(fs)
                duration = (off[j] - on[j]) * hp / float(fs) #Duration of each note in .csv file
                factorBeat=bpm/60
                durationBeat=duration*factorBeat  #Duration of each note in MIDI file
                energyseg=b[j] #Energy of each note

                # add note to array
                notes.append([sTime, duration, pitch_value, energyseg])

            # In the same way, the second melodic line:
            if method==1:
                if len(segments2[j]) % 2 == 0:
                    n = len(segments2[j])
                    segj = segments2[j]
                    mediana = (segj[n / 2 - 1] + segj[n / 2]) / 2
                else:
                    segj = segments2[j]
                    mediana = segj[len(segj) / 2]

                mPitch2 = mediana

            if method == 2:
                hist = histogram(segments2[j], np.arange(0,convertToCents(2500,fT), 1))
                pos = max(hist[0])
                for k in range(0, len(hist[0])):
                    if hist[0][k] == pos:
                        ind = k
                        break
                local_hist = hist[1][ind]
                mPitch2 = local_hist
                thr = local_hist

            if mPitch2!=0 and convertToCents(80,fT) < mPitch2 < convertToCents(750,fT):
                freq_value = fT * pow(10.0, float(mPitch2) / (1200.0 * 3.322038403))
                pitch_value2 = round(12 * log2(freq_value / fT)) + midref

                #mPitch2 = round(12 * log2(mPitch2 / fT)) + 40  # E midi note value
                sTime2 = on[j] * hp / float(fs)

                duration2 = (off[j] - on[j]) * hp / float(fs)
                factorBeat = bpm / 60
                durationBeat2 = duration * factorBeat
                energyseg = b[j]
                # add note to array
                notes.append([sTime2, duration2, pitch_value2, energyseg])

        # If it is monophonic, there is only one note:
        if not acc:
            if method==1:

                ####### MEDIANA #######
                if len(segments[j]) % 2 == 0:
                    n = len(segments[j])
                    segj = segments[j]
                    mediana = (segj[n / 2 - 1] + segj[n / 2]) / 2
                else:
                    segj = segments[j]
                    mediana = segj[len(segj) / 2]

                mPitch = mediana
                thr=mediana

            if method==2:

                #### METODO HISTOGRAMA####
                x1 = np.min(segments[j])
                x2 = np.max(segments[j])
                if x1 == x2:
                    x2 = x2 + 1
                hist = histogram(segments[j], np.arange(x1, x2, 1))
                if len(hist[0]) != 0:
                    pos = max(hist[0])
                    for k in range(0, len(hist[0])):
                        if hist[0][k] == pos:
                            ind = k
                            break
                    local_hist = hist[1][ind]
                    mPitch = local_hist
                    thr = local_hist
                else:
                    local_hist = hist[1][0]
                    mPitch = local_hist
                    thr = local_hist


            freq_value=fT * pow(10.0, float(mPitch) / (1200.0 * 3.322038403))
            pitch_value = round(12 * log2(freq_value / fT)) + midref  # E midi note value
            sTime = on[j] * hp / float(fs)
            duration = (off[j] - on[j]) * hp / float(fs)
            factorBeat = bpm / 60
            durationBeat = duration * factorBeat
            energyseg = b[j]
            # add note to array
            notes.append([sTime, duration, pitch_value, energyseg])

        #MIDI track filling
        if 80 < thr < 750:
            if not acc:
                MyMIDI.addNote(track, channel, pitch_value, sTime, durationBeat, energyseg)
            if acc:
                MyMIDI.addNote(track, channel,pitch_value, sTime, durationBeat, energyseg)
                if mPitch2>0:
                    MyMIDI.addNote(track, channel, pitch_value2, sTime2, durationBeat2, energyseg)

    return notes, MyMIDI