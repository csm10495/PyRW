'''
Brief:
    finder.py - Contains utilities related to finding the RW-Everything executable

Author(s):
    Charles Machalow
'''

import os

from rwe import ReadWriteEverything

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))
BIN_FOLDER = os.path.join(THIS_FOLDER, 'bin')
X86_BIN_FOLDER = os.path.join(BIN_FOLDER, 'x86')
X64_BIN_FOLDER = os.path.join(BIN_FOLDER, 'x64')

X64_PROGRAM_FILES = '/Program Files (x86)'

RW_EXE = 'Rw.exe'
DEFAULT_INSTALL_LOCATIONS = [
    "/Program Files/RW-Everything/%s" % RW_EXE,
    "/Program Files (x86)/RW-Everything/%s" % RW_EXE,
]

def findInstalledRWEverything():
    '''
    Brief:
        Searches for an installed version of RW-Everything. If found, returns the string path.
    '''
    drivePath = os.environ.get('SYSTEMDRIVE', 'C:')
    for defInstLoc in DEFAULT_INSTALL_LOCATIONS:
        fullPath = os.path.join(drivePath, defInstLoc)
        if os.path.isfile(fullPath):
            try:
                ReadWriteEverything(fullPath)
                return fullPath
            except EnvironmentError:
                continue

def getEnvironmentVariableAsList(v):
    '''
    Brief:
        Returns the given environment variable's values as a list
    '''
    return os.environ.get(v, '').split(os.pathsep)

def findPathedRWEverything():
    '''
    Brief:
        Searched for a RW-Everything executable in the system path. If found, returns the string path.
    '''
    path = getEnvironmentVariableAsList('PATH')
    for p in path:
        possibleRw = os.path.join(p, RW_EXE)
        if os.path.isfile(possibleRw):
            try:
                ReadWriteEverything(possibleRw)
                return possibleRw
            except EnvironmentError:
                continue

def findCwdRWEverything():
    '''
    Brief:
        Searches the current working directory for RWE
    '''
    fullPath = os.path.join(os.getcwd(), RW_EXE)
    if os.path.isfile(fullPath):
        try:
            ReadWriteEverything(fullPath)
            return fullPath
        except EnvironmentError:
            pass

def findPackagedRWEverything():
    '''
    Brief:
        Finds the RWE packaged with this module
    '''
    folder = X86_BIN_FOLDER
    if os.environ.get('ProgramFiles(x86)', False):
        # 64 bit
        folder = X64_BIN_FOLDER

    loc = os.path.join(folder, RW_EXE)
    if os.path.isfile(loc):
        return loc


def findRWEverything():
    '''
    Brief:
        Searches known directories for RWE
    '''
    r = findCwdRWEverything()
    if r:
        return r
    
    r = findPathedRWEverything()
    if r:
        return r

    r = findPackagedRWEverything()
    if r:
        return r

    r = findInstalledRWEverything()

    return r

