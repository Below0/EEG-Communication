from __future__ import print_function
import os,signal
import time
import textwrap
from datetime import datetime
from bluetooth import *

class MindwaveMobileRawReader:

    START_OF_PACKET_BYTE = 0xaa # starting point of the packet

    def __init__(self, address=None):
        self._buffer = [] # list, but it'll be used like an array
        self._bufferPosition = 0
        self._isConnected = False
        self._mindwaveMobileAddress = 'C4:64:E3:E8:E6:7B' # Mindwave Mobile 2's MAC address
        self._nearby = None
        self._sock = None
        self.target_name = 'MindWave Mobile'
        self.target_addr = 'C4:64:E3:E8:E6:7B' # Mindwave Mobile 2's MAC address
        self.target_tuple = (self.target_addr,1) # RFCOMM port == 1

        os.system('sudo systemctl daemon-reload')
        os.system('sudo systemctl restart bluetooth')
        os.system('sudo chmod 777 /var/run/sdp')
        os.system('sudo hciconfig hci0 up')
        os.system('sudo hciconfig hci0 piscan') # set a pi's module discoverable
        
    # Headset address is 'C4:64:E3:E8:E6:7B'
    def connectToMindWaveMobile(self):

        # Choosing a communication device
        # scanning for target device

        self._nearby = discover_devices()

        for bdaddr in self._nearby:
            print(lookup_name(bdaddr))
            if self.target_addr == bdaddr:
                print('target name : %s'% self.target_name)
                break
 
        if bdaddr is not None:
            print('device found. target address %s'% self.target_addr)
        else:
            self._printErrorDiscoveryMessage()
 
        # Connect
        # establishing a connection

        while(not self.isConnected()):
            try:
                self._sock = BluetoothSocket(RFCOMM)
                #print(self._sock)
                self._sock.connect(self.target_tuple)
                self._isConnected = True

            except btcommon.BluetoothError as err:
                print('Connecting failed : %s' % err)
                time.sleep(2) # wait for 2 seconds...
        
        print('Connecting with MindWave Mobile 2 success!')

    def _connectToAddress(self, mindwaveMobileAddress):
        err_count = 0
        #self.mindwaveMobileSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        while(not self._isConnected):
            try:
                self._sock = BluetoothSocket(RFCOMM)
                self._sock.connect(
                    (mindwaveMobileAddress, 1))
                self._isConnected = True
                self._sock.settimeout(1)
            except btcommon.BluetoothError as error:
                err_count += 1
                if err_count == 10:
                    print ("Attempt",err_count,"of 10: Could not connect:", error, ";")
                    return False
                else:
                    print ("Attempt",err_count,"of 10: Could not connect:", error, "; Retrying in 5s...")
                    time.sleep(5)
        return True


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
            #print('\n(.REQ',missingBytes,')')
            try:
                receivedBytes += self.mindwaveMobileSocket.recv(missingBytes)
            except:
                print ("\n--- recev timed out! ---",datetime.now())
                #receivedBytes += ['\n']*missingBytes
                print("--- exit time out code ---")
                print("--- Close connection ---")
                self.close()
                time.sleep(1)
                print("--- Trying to re-connect ---")
                if (self._connectToAddress(self._mindwaveMobileAddress)):
                    print("--- Connected ---")
                else:
                    print('Terminating process')
                    os.kill(os.getpid(), signal.SIGKILL)
                    return receivedBytes
                #time.sleep(10)
                return receivedBytes
                #return 170
            missingBytes = amountOfBytes - len(receivedBytes)
            #print('--(GET',len(receivedBytes),',miss',missingBytes,')--',)
        #print('e-read',end='')
        return receivedBytes;
        '''
        while(missingBytes > 0):
            receivedBytes += self._sock.recv(missingBytes)
            missingBytes = amountOfBytes - len(receivedBytes)
        return receivedBytes
        '''

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
