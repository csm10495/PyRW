# PyRW

Python Read/Write Everything Wrapper. This module attempts to wrap some of RW-Everything's functionality in a way that makes it easy to access some hardware within a Python script.

Note that RW-Everything is very powerful and can cause some damage if used incorrectly. Be careful.

# Prerequisites

As of now, RWE is included with this package.

# RW-Everything

Read/Write Everything is an amazing tool that can be used to access almost all computer hardware. It is really cool. It is the basis for this Python package.

For more information and to download directly check out http://rweverything.com/.
If it works really well for you, consider making a donation to the author as well.

## Examples

A lot can be done with Read Write Everything.... here are some simplified examples of PyRW:

### Interactive CLI

To use PyRW in an interactive way run (as an admin)
```
C:\>python -m pyrw

| --------------------------------------------- |
| rwe object has been created for your usage... |
| RW - Read Write Utility v1.7.0.0 x64          |
| --------------------------------------------- |

In [1]: print(rwe)
<pyrw.rwe.ReadWriteEverything object at 0x000001B9EEC691F0>
```

The ReadWriteEverything (rwe) object can be used for several operations

### Scanning PCI Devices

We can use the `getPCITree()` method to get a listing of PCI devices.

```
In [1]: from pprint import pprint

In [2]: pprint(rwe.getPCITree())
{PCILocation(Bus=0, Device=0, Function=0): 'Advanced Micro Devices Host Bridge',
 PCILocation(Bus=0, Device=1, Function=0): 'Advanced Micro Devices Host Bridge',
 PCILocation(Bus=0, Device=1, Function=1): 'Advanced Micro Devices PCI-to-PCI '
                                           'Bridge (PCIE)',
...
}
```

We can use the PCI Tree to find devices on various PCI Bus/Device/Functions.

### Getting a PCIDevice Object

To get a PCIDevice object you can do something like this:

```
In [1]: from pyrw.rwe_parser import PCILocation

In [2]: from pyrw.pci import PCIDevice

# You can use the output of rwe.getPCITree() to get a Bus/Device/Function or PCILocation object
In [3]: p = PCIDevice(rwe, PCILocation(Bus=0, Device=0, Function=0))
```

### Get PCI BAR Addresses (in RAM)

To get the PCI BAR addresses, we have the getPCIBarAddresses() function

```
# p is a PCIDevice object
In [1]: print(p.getPCIBarAddresses())
Out[1]: [0, 0, 0, 0, 0, 0]

# 0's for BARs may indicate BARs not being used

# Once you have a BAR address, it can be used with `readMemory()` and `writeMemory()`
```

### Reading / Writing PCI Configuration Space

When reading the PCI Configuration Space, expect to get back 256 bytes.
When writing the PCI Configuration Space, pass in the full 256 bytes to overwrite the space.

```
# p is a PCIDevice object
In [1]: data = p.readPCI()

In [2]: len(data)
Out[2]: 256

In [3]: type(data)
Out[3]: bytes

# Make a change and write the data back
In [4]: wdata = bytearray(data)

In [5]: wdata[0] = 34

In [6]: assert p.writePCI(wdata).ReturnCode == 0
```

### Modifying Data in Memory

To modify data in memory, you can use the `readMemory()` and `writeMemory()` functions.

```
# read 10 bytes from byte offset 0 in memory
In [1]: data = bytearray(rwe.readMemory(0, 10))

In [2]: print(data)
bytearray(b'"\x10\x80\x14\x00\x00\x00\x00\x00\x00')

In [3]: data[0] = 0xaa

In [4]: data[1] = 0x55

In [5]: assert rwe.writeMemory(0, data).ReturnCode == 0

In [6]: [hex(a) for a in (rwe.readMemory(0, 2))]
Out[6]: ['0xaa', '0x55']
```

### NVMe Specific

Use `rwe.getNVMeDevices()` to get a list of NVMe Controllers on the system. Internally it just looks for PCI devices with the NVMe class code.

See nvme.py for some utility functions available specifically for NVMe Devices.
