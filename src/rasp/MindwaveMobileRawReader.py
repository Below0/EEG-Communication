from __future__ import print_function
import bluetooth
import time
import textwrap
import os, signal

from datetime import datetime


class MindwaveMobileRawReader:
    START_OF_PACKET_BYTE = 0xaa;
    def __init__(self, address=None):
        self._buffer = [];
        self._bufferPosition = 0;
        self._isConnected = False;
        self._mindwaveMobileAddress = address

    def mac(self):
        return self._mindwaveMobileAddress

    def connectToMindWaveMobile(self):
        # First discover mindwave mobile address, then connect.
        # Headset address of my headset was'9C:B7:0D:72:CD:02';
        # not sure if it really can be different?
        # now discovering address because of https://github.com/robintibor/python-mindwave-mobile/issues/4
        if (self._mindwaveMobileAddress is None):
            self._mindwaveMobileAddress = self._findMindwaveMobileAddress()
        if (self._mindwaveMobileAddress is not None):
            print ("Connecting to Mindwave Mobile...")
            if (self._connectToAddress(self._mindwaveMobileAddress)):
                #self._mindwaveMobileAddress = None
                return
        else:
            self._printErrorDiscoveryMessage()

    def _findMindwaveMobileAddress(self):
        err_count = 0
        while(err_count < 10):
            nearby_devices = bluetooth.discover_devices(lookup_names = True)
            for address, name in nearby_devices:
                print('Discover:',name)
                if (name == "MindWave Mobile"):
                    print('Found ',address)
                    return address
            err_count += 1
            print ("Attempt",err_count,"of 10: Could not find mindwave device; Retrying in 3s...")
            time.sleep(3)
        return None

    def _connectToAddress(self, mindwaveMobileAddress):
        err_count = 0
        #self.mindwaveMobileSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        while (not self._isConnected):
            try:
                self.mindwaveMobileSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.mindwaveMobileSocket.connect(
                    (mindwaveMobileAddress, 1))
                self._isConnected = True
                self.mindwaveMobileSocket.settimeout(1)
            except bluetooth.btcommon.BluetoothError as error:
                err_count += 1
                if err_count == 10:
                    print ("Attempt",err_count,"of 10: Could not connect:", error, ";")
                    return False
                else:
                    print ("Attempt",err_count,"of 10: Could not connect:", error, "; Retrying in 5s...")
                    time.sleep(5)
        return True


    def close(self):
        self.mindwaveMobileSocket.close()
        self._isConnected = False
        #self.mindwaveMobileSocket.shutdown(2)


    def isConnected(self):
        return self._isConnected

    def _printErrorDiscoveryMessage(self):
         print(textwrap.dedent("""\
                    Could not discover Mindwave Mobile. Please make sure the
                    Mindwave Mobile device is in pairing mode and your computer
                    has bluetooth enabled.""").replace("\n", " "))

    def _readMoreBytesIntoBuffer(self, amountOfBytes):
        newBytes = self._readBytesFromMindwaveMobile(amountOfBytes)
        self._buffer += newBytes

    def _readBytesFromMindwaveMobile(self, amountOfBytes):
        missingBytes = amountOfBytes
        receivedBytes = ""
        # Sometimes the socket will not send all the requested bytes
        # on the first request, therefore a loop is necessary...
        #print('(read)',end='')
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

    def peekByte(self):
        self._ensureMoreBytesCanBeRead();
        return ord(self._buffer[self._bufferPosition])

    def getByte(self):
        #print('s',end='')
        self._ensureMoreBytesCanBeRead(100);
        #print('s',end='')
        return self._getNextByte();

    def  _ensureMoreBytesCanBeRead(self, amountOfBytes):
        #print('r',end='')
        if (self._bufferSize() <= self._bufferPosition + amountOfBytes):
        #    print('(ri)',end='')
            self._readMoreBytesIntoBuffer(amountOfBytes)
        #    print('(ro)',end='')
        #print('r2',end='')
        return

    def _getNextByte(self):
        if(self._buffer.length > self._bufferPosition):
            nextByte = ord(self._buffer[self._bufferPosition]);
            self._bufferPosition += 1;
        return nextByte;

    def getBytes(self, amountOfBytes):
        #print('-GBs-',end='')
        self._ensureMoreBytesCanBeRead(amountOfBytes);
        return self._getNextBytes(amountOfBytes);

    def _getNextBytes(self, amountOfBytes):
        nextBytes = map(ord, self._buffer[self._bufferPosition: self._bufferPosition + amountOfBytes])
        self._bufferPosition += amountOfBytes
        return nextBytes

    def clearAlreadyReadBuffer(self):
        self._buffer = self._buffer[self._bufferPosition : ]
        self._bufferPosition = 0;

    def _bufferSize(self):
        #print('(bsize=',len(self._buffer),')',end='')
        return len(self._buffer);
