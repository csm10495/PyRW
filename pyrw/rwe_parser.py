'''
Brief:
    Contains helpers to parse RWE output data

Author(s):
    Charles Machalow
'''
import collections
import re

PCI_DEVICE_LINE_REGEX = r'Bus (\w*), Device (\w*), Function (\w*) \- (.*)'
RWE_ADDRESS_REGEX = r' Address=(\w*?), '
PCILocation = collections.namedtuple("PCILocation", ['Bus', 'Device', 'Function'])

def getBinaryFromHexDump(hexDumpStr):
    '''
    Brief:
        Gets a binary representation of the string hex dump RWE would print in some cases
    '''
    lines = hexDumpStr.splitlines()
    lines = [line for line in lines if line[0] != ' '] # remove spaced lines
    lines = [line for line in lines if line[1] != 'u'] # remove dump lines
    lines = [line for line in lines if line[2] != 'r'] # remove parameter error lines
    ret = []
    for line in lines:
        line = line.split(' ', 1)[1] # remove index
        line = line.split('\t')[0]   # remove ascii
        ret += [int(c, 16) for c in line.split()]

    return bytearray(ret)

def bytesToDWordList(b):
    '''
    Brief:
        Convert a list of bytes to a list of DWords
    '''
    ret = []
    for idx in range(0, len(b), 4):
        d = b[idx] + (b[idx + 1] << 8) + (b[idx + 2] << 16) + (b[idx + 3] << 24)
        ret.append(d)

    return ret

def pciTreeTextToDict(txt):
    '''
    Brief:
        Converts a PCI tree's text to a dict of PCI devices to descriptions
    '''
    a = re.findall(PCI_DEVICE_LINE_REGEX, txt)
    retDict = {}
    for itm in a:
        retDict[
            PCILocation(int(itm[0], 16), int(itm[1], 16), int(itm[2], 16))
        ] = itm[3].strip()

    return retDict

def verifyAddress(address, rweOutput):
    '''
    Brief:
        Verifies that the given address matches the RWE output. Raises if it is mismatched.
            Note that there are some current issues with 64-bit addresses and RWE not handling them properly in commands.
                This should at least tell the user if that happens, though there is no current workaround.
                    I've emailed RWE's Jeff about this bug. Said it should be fixed in a future release.
    '''
    m = re.findall(RWE_ADDRESS_REGEX, rweOutput)
    rweAddr = int(m[0], 16)
    if address != rweAddr:
        raise RuntimeError("RWE Didn't process the correct address! It processed: 0x%X instead of 0x%X" % (rweAddr, address))
