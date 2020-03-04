import os
import time
import textwrap
from bluetooth import *

class MindwaveMobileRawReader:

    START_OF_PACKET_BYTE = 0xaa # starting point of the packet

    def __init__(self, address=None):
        self._buffer = [] # list, but it'll be used like an array
        self._bufferPosition = 0
        self._isConnected = False
        self._mindwaveMobileAddress = address
        self._nearby = None
        self._sock = None
        self.target_name = 'MindWave Mobile'
        self.target_addr = 'C4:64:E3:E8:E6:7B' # Mindwave Mobile 2's MAC address
        self.target_tuple = (self.target_addr,1) # RFCOMM port == 1

    # Headset address is 'C4:64:E3:E8:E6:7B'
    def connectToMindWaveMobile(self):

        # Choosing a communication device
        # scanning for target device
        '''
        self._nearby = discover_devices()

        for bdaddr in self._nearby:
            print(lookup_name(bdaddr))
            if self.target_addr == bdaddr:
                print('target name : %s'% self.target_name)
                print('target addr : %s'% self.target_addr)
                break
        if bdaddr is not None:
            print('device found. target address %s'% self.target_addr)
        else:
            self._printErrorDiscoveryMessage()
        '''
        # Connect
        # establishing a connection

        while(not self._isConnected):
            try:
                self._sock = BluetoothSocket(RFCOMM)
                self._sock.connect(self.target_tuple)
                self._sock.settimeout(3) # socket timeout setting
                self._isConnected = True

            except btcommon.BluetoothError as err:
                print('Connecting failed : %s' % err)
                if(err.errno is 115):
                    self.close()
                if(err.errno is 16):
                    time.sleep(3)
                time.sleep(2) # wait for 2 seconds...

        print('Connecting with MindWave Mobile 2 success!')

    def isConnected(self):
        return self._isConnected

    def close(self):
        self._sock.close()
        self._isConnected = False

    def _printErrorDiscoveryMessage(self):
         print((textwrap.dedent("""\
                    Could not discover Mindwave Mobile. Please make sure the
                    Mindwave Mobile device is in pairing mode and your computer
                    has enabled.""").replace("\n", " ")))

    def _readMoreBytesIntoBuffer(self, amountOfBytes):
        newBytes = self._readBytesFromMindwaveMobile(amountOfBytes)
        self._buffer += newBytes
    def _readBytesFromMindwaveMobile(self, amountOfBytes):
        missingBytes = amountOfBytes
        receivedBytes = b''   #py3
        # Sometimes the socket will not send all the requested bytes
        # on the first request, therefore a loop is necessary...
        while(missingBytes > 0):
            try:
                temp = self._sock.recv(missingBytes)
                receivedBytes += temp
            except Exception as err:
                print('trying to reconnect with Mindwave Mobile2')
                self._sock.close()
                time.sleep(2)
                self._isConnected = False
                self.connectToMindWaveMobile()
                continue
            missingBytes = amountOfBytes - len(receivedBytes)

        return receivedBytes

    def peekByte(self):
        self._ensureMoreBytesCanBeRead()
        return ord(self._buffer[self._bufferPosition])

    def getByte(self):
        self._ensureMoreBytesCanBeRead(100)
        return self._getNextByte()

    def  _ensureMoreBytesCanBeRead(self, amountOfBytes):
        if (self._bufferSize() <= self._bufferPosition + amountOfBytes):
            self._readMoreBytesIntoBuffer(amountOfBytes)

    def _getNextByte(self):
        nextByte = self._buffer[self._bufferPosition] # use a list like an array
        self._bufferPosition += 1 # pos++
        return nextByte

    def getBytes(self, amountOfBytes):
        self._ensureMoreBytesCanBeRead(amountOfBytes)
        return self._getNextBytes(amountOfBytes)

    def _getNextBytes(self, amountOfBytes):
        nextBytes = list(self._buffer[self._bufferPosition: self._bufferPosition + amountOfBytes]) #py3
        self._bufferPosition += amountOfBytes
        return nextBytes

    def clearAlreadyReadBuffer(self):
        self._buffer = self._buffer[self._bufferPosition : ]
        self._bufferPosition = 0

    def _bufferSize(self):
        return len(self._buffer)
