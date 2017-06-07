PyTOQUE
=====

A python package for automatic transcription of flamenco guitar.

TOQUE estimates a note-level transcription from monophonic or polyphonic recording.


Requirements
------------

TOQUE depends on numpy/scipy (https://www.scipy.org).

Essentia (http://essentia.upf.edu) python bindings.

MIDIUtil python library https://pypi.python.org/pypi/MIDIUtil/

Usage
-----
    import toque

    toque.transcribeguit('filename', acc=False, recursive=False, tmin=15, method=2,tone='default', transposed=0)

    (you can also run main module)

The algorithm creates a .csv file containing the estimated note events corresponding to the
guitar melody, where each row corresponds to a note event as follows:

    < note onset [seconds] >, < note duration [seconds] >, < MIDI pitch value >, <energy value>;

Input is a .wav audio file with a sample rate of 44.1kHz and a bit depth of 16 Bits. Otherwise
an error is raised.

In recursive mode, the algorithm transcribes all .wav files in the provided folder path.

For accompanied recordings (i.e. vocals + guitar), an additional contour filtering stage is
applied. In this case, set acc = True. Also you can give a minimal time of the falsetas that you want to extract.

In addition, only if you are sure about the tonal features and (if it is necessary) a transposition value, you can also set it.
This will allow an scale adjust in the post-processing stage.

    :param filename: <string> path to the input file or folder.
    :param acc: <bool> True if accompaniment is expected, False for guitar falseta
    :param recursive: <bool> True for folder recursion.
    :param tmin: <int> Minimum time to consider a segment as a falseta (recommended > 6s)
    :param method:  <int> '1' to choose the pitch value of each segment using the median value
                    <int> '2' to choose the pitch value using an histogram
    :param tone: <string> 'Ef' to scale adjust in E flamenco tonality
                 <string> 'E' to scale adjust in E major tonality
                 <string> 'Af' to scale adjust in A flamenco tonality
                 <string> 'default' to no scale adjust
    :param transposed <int> [0 to 7] Only if the audio file is transposed, taking the previous tonalities as a reference. (Default=0)

    :return: <filename>_timefalsetas.txt
    :return: <filename>_Lfalsetas.wav only if the input is a stereo file
    :return: <filename>_Rfalsetas.wav only if the input is a stereo file
    :return: <filename>_Mfalsetas.wav only if the input is a mono file
    :return: NONE - <filename>.notes.csv written to the same folder
    :return: NONE- <filename>_MIDI.mid  written to the same folder