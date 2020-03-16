import struct
import collections
from .bci_MindwaveMobileRawReader import MindwaveMobileRawReader
from .bci_MindwavePacketPayloadParser import MindwavePacketPayloadParser

class MindwaveDataPointReader:

    def __init__(self, address=None):
        self._mindwaveMobileRawReader = MindwaveMobileRawReader(address=address)
        self._dataPointQueue = collections.deque() # bothways Queue : deque

    def start(self):
        self._mindwaveMobileRawReader.connectToMindWaveMobile() # connect to Mindwave Mobile 2

    def close(self):
        self._mindwaveMobileRawReader.close()

    def isConnected(self):
        return self._mindwaveMobileRawReader.isConnected() # is Connected -> True/False

    def readNextDataPoint(self):
        if (not self._moreDataPointsInQueue()): # if self._dataPointQueue is <= 0
            self._putNextDataPointsInQueue() # insert a data into self._dataPointQueue -- 1)
        return self._getDataPointFromQueue() # self._dataPointQueue.pop()

    def _moreDataPointsInQueue(self):
        return len(self._dataPointQueue) > 0
    
    def _getDataPointFromQueue(self):
        return self._dataPointQueue.pop()
    
    def _putNextDataPointsInQueue(self):
        dataPoints = self._readDataPointsFromOnePacket() # read a data from one packet -- 2)
        self._dataPointQueue.extend(dataPoints) # insert into the deque
    
    def _readDataPointsFromOnePacket(self):
        self._goToStartOfNextPacket() # move to a payload address -- 3)
        payloadBytes, checkSum = self._readOnePacket()  # read a packet's data -- 4)
        if (not self._checkSumIsOk(payloadBytes, checkSum)): # Is checksum invalid?
            print("checksum of packet was not correct, discarding packet...")
            return self._readDataPointsFromOnePacket();
        else: # checksum is valid
            dataPoints = self._readDataPointsFromPayload(payloadBytes) # split the payload data into defined length
        self._mindwaveMobileRawReader.clearAlreadyReadBuffer() # reset a memory
        return dataPoints
    
    # Because BLE packet payload starts with two bytes HEAD, we have to call getByte() twice.
    def _goToStartOfNextPacket(self):
        while(True):
            byte = self._mindwaveMobileRawReader.getByte()
            if(byte == MindwaveMobileRawReader.START_OF_PACKET_BYTE): # if read byte is equal to payload's address
                byte = self._mindwaveMobileRawReader.getByte()
                if (byte == MindwaveMobileRawReader.START_OF_PACKET_BYTE):
                    # now at the start of the payload..
                    return;

    def _readOnePacket(self):
            payloadLength = self._readPayloadLength()
            payloadBytes, checkSum = self._readPacket(payloadLength)
            return payloadBytes, checkSum
    
    def _readPayloadLength(self):
        payloadLength = self._mindwaveMobileRawReader.getByte()
        return payloadLength

    def _readPacket(self, payloadLength):
        payloadBytes = self._mindwaveMobileRawReader.getBytes(payloadLength) # read a useful data on packet
        checkSum = self._mindwaveMobileRawReader.getByte() # checksum == 1 Byte
        return payloadBytes, checkSum

    def _checkSumIsOk(self, payloadBytes, checkSum):
        sumOfPayload = sum(payloadBytes)
        lastEightBits = sumOfPayload % 256
        invertedLastEightBits = self._computeOnesComplement(lastEightBits) #1's complement!
        return invertedLastEightBits == checkSum
    
    def _computeOnesComplement(self, lastEightBits):
        return ~lastEightBits + 256
        
    def _readDataPointsFromPayload(self, payloadBytes):
        payloadParser = MindwavePacketPayloadParser(payloadBytes)
        return payloadParser.parseDataPoints()

