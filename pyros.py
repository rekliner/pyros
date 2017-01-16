import serial
import time
class Pyros():
    def __init__(self):
        self.mod = 0
        self.state = "Disconnected"
        self.comPortName = None
        self.comPort = None
        self.debug = False

    def erosConnect(self):
        if self.comPortName == None:
            print("COM PORT NOT SET")
        else:
            self.comPort = serial.Serial(self.comPortName, 19200,timeout = .02)
            if self.state == "Disconnected":
                #send test bytes
                if self.debug > 0:
                    print("sending test bytes")
                replies = erosPing(0)
                # tx sent, rx received.  contact is made, now it's time to initialize encryption
                if replies > 3 :
                    if self.debug > 0:
                        print("ping received, sending connection request")
                    message = bytes{[0x2f, 0x00]}
                    self.mod = 0
                    reply = self.txrx(message)
                    checkSum = (reply[0] + reply[1]) % 256
                    if len(reply) < 3 || reply[0] != b'\x21' || checkSum != reply[2]:
                        #the reply must be at least 3 bytes, the first byte must be 0x21, and the checksum must be valid
                        #if not the reply is considered invalid
                        print("no sync")
                    else :
                        self.state = "Connected"
                        self.mod = reply[1] ^ 0x55
                        if self.debug > 0:
                            print("new mod = " + self.mod)

    def erosPing(self,testMod)
        for  i in range(0,10):      #attempt 10 pings
            message=bytes([0x00])   #pinging the eros with 0 values
            replies = 0
            holdMod = self.mod   #save any stored mod value
            self.mod = testMod   #set "official" mod value for txrx function to be the one we want to test
            reply = self.txrx(message)  #send it off and check the reply
            if len(reply) > 0 && reply[0] == b'\x07':
                #if a response from the Eros is received
                replies++ #tally it
                if (replies > 3):
                    break #if there have been three responses then continue to next phase
            else:
                replies = 0 #if nothing was received then start the reply count over
        self.mod = holdMod      #return to previous mod
        return replies            
                    
    def testConnection(self):
        holdMod = self.mod
        
        
    def txrx(self,message):
        #sends bytes, first encrypting with mod value, and returns the reply from an Eros
        checkSum = 0
        if self.debug > 0:
            print(str(len(message)) + " byte message: " + str(message))    
        for i in range(0,len(message)):     #going through each character in the message
            char = message[i]   #only looking at one character of the message
            #by checking for type we can accept both bytes and strings here
            if isinstance( char, str ):     #if it received a string character
                char = ord(char)            #convert it to ordinal value
            checkSum = (checkSum + char) % 256 # calculate checksum.  overflow expected, modulo 256 to make it happen
            moddedChar = bytes([char ^ self.mod])   #encrypt the message with Erostek's method
            self.comPort.write(moddedChar)  #send the message to the comport
        if len(message) > 1:
            self.comPort.write(bytes([checkSum])) #append the checksum if the message is more than one byte
        
        self.comPort.flush()    #clear the pipes
        #wait up to 20ms for a reply
        reply = self.comPort.read(100)
        if self.debug > 0:
            print("reply: " + str(reply))
        if len(reply) == 0:  #if no reply then return state to disconnected
            if self.debug > 0:
                print("No reply. Disconnecting.")
            self.state = "Disconnected"
        return reply
        """
        waitTime = int(round(time.time() * 1000)) + 20  
        while int(round(time.time() * 1000)) > waitTime:
            bytesToRead = ser.inWaiting()
            if bytesToRead > 0 :
                reply+=str(ser.read(bytesToRead).decode("utf-8"))
        """
 
    def getValue(self,key):
        toEros = bytes([0x3C,ord(key) >> 8,ord(key) & 255])
        reply = self.txrx(toEros)
        if len(reply) < 3:
            return -1
        if reply[0] != b'\x22':
            return -1
        if ((reply[0]+reply[1]) % 256) != reply[3]:
            return -1
        return reply[1]
        
    def setValue(self,key,value):
        toEros = bytes([0x4D,ord(key) >> 8,ord(key) & 255,value])
        reply = self.txrx(toEros)
        if len(reply) < 1 or reply != b'\x06':
            return False
        return True
        
    def ping(self):
        key=b'\xAB'
        reply = self.getValue(key)
        self.setValue(key,56)
        #self.mod += 1
