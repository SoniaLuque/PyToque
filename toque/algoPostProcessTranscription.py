from numpy import array, mean, std
import numpy as np
from utils import adjustScale


def algoPostProcessTranscription(notes, tone, transposed):

    '''
    Post-processing stage for automatic note transcription: Notes are transposed or eliminated based on their relative
    pitch and temporal isolation as described in 2-B-III of

    :param notes: notes: array in which rows correspond to note events; first element -> onset time [seconds], second element
            --> note duration [seconds], third element --> MIDI pitch
    :param tone: <string> 'Ef' to scale adjust in E flamenco tonality
                 <string> 'E' to scale adjust in E major tonality
                 <string> 'Af' to scale adjust in A flamenco tonality
                 <string> 'default' to no scale adjust
    :param transposed <int> [0 to 7] Only if the audio file is transposed, taking the previous tonalities as a reference
    :return: notes modified
    '''

    # PARAMETERS
    minNoteDurationSec = 0.02

    # compute duration mean and std
    noteArray = array(notes)
    pitches = noteArray[:,2]

    for note in notes:
        # remove notes with short duration
        if note[1] < minNoteDurationSec:
            notes.remove(note)
            continue
    # Defining 3 of most popular scales used in flamenco field (Mi Frigio Mayorizado, A frigio Mayorizado, E major)

    E_frigio_mayorizado_1=np.array([40.0,41.0,43.0,44.0,45.0,47.0,48.0,50.0])
    E_frigio_mayorizado_2 = E_frigio_mayorizado_1+12
    E_frigio_mayorizado_3 = E_frigio_mayorizado_2+12
    E_frigio_mayorizado_4 = E_frigio_mayorizado_3+12
    E_frigio_mayorizado=np.hstack((E_frigio_mayorizado_1,E_frigio_mayorizado_2,E_frigio_mayorizado_3,E_frigio_mayorizado_4))


    E_mayor_1 = np.array([40.0,41.0,42.0,44.0,45.0,47.0,48.0,49.0,51.0])
    E_mayor_2 = E_mayor_1 + 12
    E_mayor_3 = E_mayor_2 + 12
    E_mayor_4 = E_mayor_3 + 12
    E_mayor = np.hstack((E_mayor_1,E_mayor_2,E_mayor_3,E_mayor_4))

    E_frigio_mayorizado = E_frigio_mayorizado + transposed
    A_frigio_mayorizado = E_frigio_mayorizado + 5 + transposed
    E_mayor=E_mayor+transposed

    # Scale adjusting taking account of the previous ones
    if tone == 'Ef':
        pitches_=adjustScale(pitches,E_frigio_mayorizado)
    if tone== 'E':
        pitches_ = adjustScale(pitches, E_mayor)
    if tone== 'Af':
        pitches_ = adjustScale(pitches, A_frigio_mayorizado)
    if tone == 'default':
        pitches_=pitches

    for i in range(0,len(notes)):
        notes[i][2] = pitches_[i]

    return notes
