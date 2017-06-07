''' Auxiliary functions for csv file reading and writing'''

import csv
from numpy import genfromtxt

def writeToCsv(notes,filename):

    '''
    Writes the output array of the transcription algorithm to a csv file in the following format:
    <note onset [seconds]>, <note duration [seconds]>, <MIDI pitch>

    :param notes: array containing note events
    :param filename: csv file to be written
    :return: NONE
    '''
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(notes)

    return