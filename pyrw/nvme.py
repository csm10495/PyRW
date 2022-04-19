'''
Brief:
    File for the NVMe Devices

Author(s):
    Charles Machalow
'''

import collections
import time
from ctypes import *

from pyrw.rwe_parser import *
from pyrw.pci import PCIDevice

COMPLETION_ENTRY_SIZE = 16
SUBMISSION_ENTRY_SIZE = 64
NVME_CLASS_CODE = 0x10802

AdminQueueAddresses = collections.namedtuple("AdminQueueAddresses", ['AdminSubmissionQueueBase', 'AdminCompletionQueueBase'])
AdminQueueAttributes = collections.namedtuple("AdminQueueAttributes", ['AdminCompletionQueueSize', 'AdminSubmissionQueueSize'])
AdminQueueEntries = collections.namedtuple("AdminQueueEntries", ['AdminCompletionQueue', 'AdminSubmissionQueue'])
NVMeVersion = collections.namedtuple("NVMeVersion", ['Major', 'Minor', 'Tertiary'])

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class NVMeDevice(PCIDevice):
    '''
    Brief:
        Abstraction for an NVMe PCIe Device
    '''
    def __init__(self, rwe, address):
        '''
        Brief:
            Initializer for the NVMe Device
        '''
        PCIDevice.__init__(self, rwe, address)
        assert self.getPCIClassCode() == NVME_CLASS_CODE, "This is not an NVMe device."

    def getControllerRegisterData(self):
        '''
        Brief:
            Returns a copy of the first 4096 bytes of controller register data
        '''
        bar0 = self.getPCIBarAddresses()[0]
        return self.rwe.readMemory(bar0, 4096)

    def getNVMeVersion(self):
        '''
        Brief:
            Returns the NVMe version from the controller registers
        '''
        controllerRegisterData = self.getControllerRegisterData()
        vs = bytesToDWordList(controllerRegisterData[0x8:])[0]
        return NVMeVersion(Major=vs >> 16, Minor=((vs >> 8) & 0xFF), Tertiary=vs & 0xFF)

    def getAdminQueueAttributes(self):
        '''
        Brief:
            Returns the admin queue sizes
        '''
        controllerRegisterData = self.getControllerRegisterData()
        aqa = bytesToDWordList(controllerRegisterData[0x24:])[0]
        return AdminQueueAttributes(AdminCompletionQueueSize=(aqa >> 16) & 0xFFF, AdminSubmissionQueueSize=aqa & 0xFFF)

    def getAdminQueueBaseAddresses(self):
        '''
        Brief:
            Returns the addresses of the admin submission and completion queues
        '''
        controllerRegisterData = self.getControllerRegisterData()
        asqb = ((c_uint64.from_buffer_copy(controllerRegisterData[0x28:]).value) >> 12) << 12
        acqb = ((c_uint64.from_buffer_copy(controllerRegisterData[0x30:]).value) >> 12) << 12
        return AdminQueueAddresses(asqb, acqb)

    def getAdminQueueEntries(self):
        '''
        Brief:
            Returns all the queue entries in the admin queues
        '''
        addresses = self.getAdminQueueBaseAddresses()
        sizes = self.getAdminQueueAttributes()
        submissionQueue = self.rwe.readMemory(addresses.AdminSubmissionQueueBase, SUBMISSION_ENTRY_SIZE * sizes.AdminSubmissionQueueSize)
        completionQueue = self.rwe.readMemory(addresses.AdminCompletionQueueBase, COMPLETION_ENTRY_SIZE * sizes.AdminCompletionQueueSize)
        sqDw = bytesToDWordList(submissionQueue)
        cqDw = bytesToDWordList(completionQueue)
        return AdminQueueEntries(list(chunks(cqDw, 4)), list(chunks(sqDw, 16)))

    def controllerReset(self):
        '''
        Brief:
            Performs a complete NVMe Controller Reset.
                CC.EN -> 0
                CSTS.RDY -> 0
                CC.EN -> 1
                CSTS.RDY -> 1
        '''
        bar0 = self.getPCIBarAddresses()[0]
        CCAddr = bar0 + 0x14
        CSTSAddr = bar0 + 0x1C

        timeoutMs = self.getControllerRegisterData()[3] * 500

        CC0 = self.rwe.readMemory(CCAddr, 1)[0]
        CC0 = ((CC0 >> 1) << 1) # set CC.EN to 0
        assert self.rwe.writeMemory(CCAddr, [CC0]).ReturnCode == 0

        deathTime = time.time() + (timeoutMs / 1000.0)
        while time.time() < deathTime:
            CSTS0 = self.rwe.readMemory(CSTSAddr, 1)[0]
            if CSTS0 & 1 == 0:
                break
        else:
            raise RuntimeError("CSTS.RDY did not go to 0")

        CC0 = CC0 + 1 # set CC.EN to 1
        self.rwe.writeMemory(CCAddr, [CC0])

        deathTime = time.time() + (timeoutMs / 1000.0)
        while time.time() < deathTime:
            CSTS0 = self.rwe.readMemory(CSTSAddr, 1)[0]
            if CSTS0 & 1 == 1:
                break
        else:
            raise RuntimeError("CSTS.RDY did not go back to 1")

    def subsystemReset(self):
        '''
        Brief:
            Performs an NVMe Subsystem Reset
        '''
        # write 4E564D65h ("NVMe") to NSSR (0x20)
        bar0 = self.getPCIBarAddresses()[0]
        NSSR = bar0 + 0x20

        if self.rwe.writeMemory(NSSR, [0x4e, 0x56, 0x4d, 0x65]).ReturnCode != 0:
            raise RuntimeError("Failed to write the NSSR")

        # todo: check if it worked?