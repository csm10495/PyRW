'''
Brief:
    File for the PCI device

Author(s):
    Charles Machalow
'''

class PCIDevice(object):
    '''
    Brief:
        Abstraction of some things to do on a PCI device
    '''
    def __init__(self, rwe, address):
        '''
        Brief:
            Initializer for the object. Takes a RWE instance and the PCI Address
        '''
        self.rwe = rwe
        self.address = address

        # aliases
        self.readPCI = lambda : self.rwe.readPCI(self.address.Bus, self.address.Device, self.address.Function)
        self.writePCI = lambda data: rwe.writePCI(self.address.Bus, self.address.Device, self.address.Function, data)
        self.getPCIClassCode = lambda : self.rwe.getPCIClassCode(self.address.Bus, self.address.Device, self.address.Function)
        self.getPCIBarAddresses = lambda : self.rwe.getPCIBarAddresses(self.address.Bus, self.address.Device, self.address.Function)