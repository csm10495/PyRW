'''
Brief:
    File for the ReadWriteEverything class

Author(s):
    Charles Machalow
'''
import collections
import logging
import os
import subprocess
import tempfile

from ctypes import *

from pyrw.rwe_parser import bytesToDWordList, pciTreeTextToDict, verifyAddress
from pyrw.nvme import NVMeDevice, NVME_CLASS_CODE

logger = logging.getLogger(__name__)

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))
LOCAL_TMP_FILE = os.path.join(THIS_FOLDER, '__tmp.bin')
ProcessOutput = collections.namedtuple("ProcessOutput", ["Output", "ReturnCode"])

class ReadWriteEverything(object):
    '''
    Brief:
        Easy to use abstractions for RWE in Python
    '''
    def __init__(self, exePath=None):
        '''
        Brief:
            Initializer for the class. Takes the path to rw.exe
                Ensures we have admin and that rw.exe seems to work
        '''

        if exePath is None:
            # import here to prevent a circle
            from pyrw.finder import findRWEverything
            exePath = findRWEverything()

        self.exePath = exePath
        self.version = self.getRWEVersion()

        if not windll.shell32.IsUserAnAdmin():
            raise EnvironmentError("Please run as admin")

        self._checkValidRWExe()

    def _checkValidRWExe(self):
        '''
        Brief:
            Does a stupidly silly check to see if rw.exe appears to work
        '''
        r = self.callRWECommand("COUT Hello World;rwexit")
        if 'RW Exit' in r.Output and 'Hello World' in r.Output and r.ReturnCode:
            raise EnvironmentError("%s does not appear to be a valid RW-Everything exe" % self.exePath)

    def getRWEVersion(self):
        '''
        Brief:
            Uses some magic to get the RWE version
        '''
        if hasattr(self, 'version'):
            return self.version

        version = subprocess.check_output('powershell "(Get-Item -path \\"%s\\").VersionInfo.FileVersion"' % self.exePath).strip().decode()
        with open(self.exePath, 'rb') as f:
            # https://superuser.com/questions/358434/how-to-check-if-a-binary-is-32-or-64-bit-on-windows
            f.seek(0x204)
            if f.read(1)[0] == 0x64:
                b = 'x64'
            else:
                b = 'x86'

        v = 'RW - Read Write Utility v%s %s' % (version, b)
        self.version = v
        logger.debug("RWE Version: %s" % v)
        return self.version

    def callRawCommand(self, cmd):
        '''
        Brief:
            Calls a Raw command on rw.exe
        '''
        fullCmd = '\"%s\" %s' % (self.exePath, cmd)
        logger.debug("Calling raw command: %s" % fullCmd)
        try:
            output = subprocess.check_output(fullCmd, shell=True, stderr=subprocess.STDOUT)
            retCode = 0
        except subprocess.CalledProcessError as ex:
            output = ex.output
            retCode = ex.returncode

        ret = ProcessOutput(Output=output.decode(), ReturnCode=retCode)
        logger.debug("... Returned: %s" % str(ret))
        return ret

    def callRWECommand(self, cmd):
        '''
        Brief:
            Calls an embeded RWE command on rw.exe
        '''
        fullCommand = '/Min /Nologo /Stdout /Command="%s"' % (cmd.replace('\"', '\\"'))
        return self.callRawCommand(fullCommand)

    def readMemory(self, byteOffset, numBytes):
        '''
        Brief:
            Reads raw memory from a given offset for a given number of bytes
        '''
        n = self.callRWECommand("SAVE \"%s\" Memory 0x%X %d" % (LOCAL_TMP_FILE, byteOffset, numBytes))
        assert n.ReturnCode == 0, "Didn't return 0"
        verifyAddress(byteOffset, n.Output)

        with open(LOCAL_TMP_FILE, 'rb') as f:
            data = f.read()
        os.remove(LOCAL_TMP_FILE)
        return data

    def writeMemory(self, byteOffset, data):
        '''
        Brief:
            Writes given data to the given offset of memory
        '''
        with open(LOCAL_TMP_FILE, 'wb') as f:
            f.write(bytearray(data))

        ret = self.callRWECommand('LOAD "%s" Memory %d' % (LOCAL_TMP_FILE, byteOffset))
        verifyAddress(byteOffset, ret.Output)

        os.remove(LOCAL_TMP_FILE)
        return ret

    def readPCI(self, bus, device, function):
        '''
        Brief:
            Reads PCI header (configuration space) data from the given device
        '''
        n = self.callRWECommand("SAVE \"%s\" PCI %d %d %d" % (LOCAL_TMP_FILE, bus, device, function))
        assert n.ReturnCode == 0, "Didn't return 0"
        with open(LOCAL_TMP_FILE, 'rb') as f:
            data = f.read()
        os.remove(LOCAL_TMP_FILE)
        return data

    def writePCI(self, bus, device, function, data):
        '''
        Brief:
            Writes given PCI (configuration space) data to a given device
        '''
        with open(LOCAL_TMP_FILE, 'wb') as f:
            f.write(bytearray(data))

        ret = self.callRWECommand('LOAD "%s" Memory %d %d %d' % (LOCAL_TMP_FILE, bus, device, function))
        os.remove(LOCAL_TMP_FILE)
        return ret

    def getPCIBarAddresses(self, bus, device, function):
        '''
        Brief:
            Gets a list of BAR addresses for the given device
        '''
        pciRegisters = self.readPCI(bus, device, function)
        pciRegistersAsDWords = bytesToDWordList(pciRegisters[0x10:])
        return [((x >> 4) << 4) for x in pciRegistersAsDWords[:6]] # 6 bars max

    def getPCITree(self):
        '''
        Brief:
            Parses the system's PCI devices to a dictionary
        '''
        n = self.callRWECommand('PCITREE')
        assert n.ReturnCode == 0, "Didn't return 0"
        return pciTreeTextToDict(n.Output)

    def getPCIClassCode(self, bus, device, function):
        '''
        Brief:
            Gets the PCI class code for a given device
        '''
        d = self.readPCI(bus, device, function)
        return bytesToDWordList(d[0x09:0x0D])[0] & 0xFFFFFF

    def getNVMeDevices(self):
        '''
        Brief:
            Returns a list of all NVMe devices on the system
        '''
        nvmeDevices = []
        for address in self.getPCITree().keys():
            testClassCode = self.getPCIClassCode(address.Bus, address.Device, address.Function)
            if testClassCode == NVME_CLASS_CODE:
                nvmeDevices.append(NVMeDevice(self, address))

        return nvmeDevices

if __name__ == '__main__':
    rwe = ReadWriteEverything()