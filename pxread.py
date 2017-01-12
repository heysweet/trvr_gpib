import os.path
import serial
import sys
import time
import csv

# Use this is terminal to get longer descriptions of connected usb devices
# `ioreg -p IOUSB -l -b | grep -E "@|PortNum|USB Serial Number"`
#

# To get the serialPortName:
#
# `ls /dev/tty.*`
#
# The result can be read like this:
# screen /dev/tty.[serialPortName] [yourBaudRate]

# COM Port : "/dev/tty.usbserial-PX93V05T"
# GPID Address : 28 (default) 


COM_PORT = "/dev/tty.usbserial-PX93V05T"
GPIB_ADDRESS = 28

MIN_FREQ = 20
MAX_FREQ = 10000

# 1 or 2
GRANULARITY = 1

#==============================================================================

# IF SENDING ANY OF THESE CHARACTERS, MUST ESCAPE
def IsSpecial(data):
    return data in (LF, CR, ESC, PLUS)
#==============================================================================

# Units to use
# 20hz -- 10khz

CODE_TABLE = {
    # Functions
    'startFreq' : 'FA',
    'stopFreq' : 'FB',
    'plotLimit' : 'PL',
    'freq' : 'FR',
    'freqIncrement' : 'FN',
    'ampIncrement' : 'AN',

    # Data
    'clear' : 'CL',

    # Units
    'kHz' : 'KZ',
    'V' : 'VL',
    'upperLimit' : 'UL',
    'Hz' : 'HZ',
    'mV' : 'MV',
    'lowerLimit' : 'LL',
    'dB' : 'DB',
    'dBV' : 'DV',
}

def buildFreqMessage(freq, isAC):
    # Access the global CODE_TABLE
    global CODE_TABLE

    automaticOp = "AU"

    units = CODE_TABLE['Hz']
    if freq > 1000:
        freq /= 1000.0
        units = CODE_TABLE['kHz']

    sourceFreq = CODE_TABLE['freq'] + str(freq) + units
    sourceAmp = "AP0.1VL"
    if isAC:
        acOrDistortionLevel = "M1" # AC Level
    else:
        acOrDistortionLevel = "M3" # Distortion
    lowPass = "L2"
    lin = "LN"
    triggerWithSettling = "T2"

    return automaticOp +\
        sourceFreq +\
        sourceAmp +\
        acOrDistortionLevel +\
        lowPass +\
        lin +\
        triggerWithSettling

def resetToLocalControl(ser):
    print "Resetting to local control."
    ser.write("GTL\n")
    time.sleep(1.1)
    ser.write("IFC\n")

def queryACLevel(ser, freq):
    cmd = buildFreqMessage(freq, True)
    ser.write(cmd + "\n")
    time.sleep(2.0)

def getACLevelAndDistortion(ser, freq):
    cmd = buildFreqMessage(freq, False)
    ser.write(cmd + "\n")

    s = True
    result = ''

    time.sleep(2)
    while s:
        s = ser.read(256);
        result += s

    return result

def beep():
    print '\a'

def stepLog(freq):
    return 10 ** (len(str(freq)) - GRANULARITY)

if __name__ == '__main__':

    if len( sys.argv ) != 3:
        print "Possible Usage: ", os.path.basename( sys.argv[0] ), "<COM port> <GPIB address>"
    else:
        COM_PORT = sys.argv[1];
        GPIB_ADDRESS = sys.argv[2];

    comport = COM_PORT
    addr = GPIB_ADDRESS
    
    ser = serial.Serial()

    f = False
    
    try:
        success = True
        
        ser = serial.Serial( comport, 9600, timeout=0.5 )

        freq = MIN_FREQ        

        timestr = time.strftime("%Y_%m_%d_%H%M%S")
        filename = 'amp_sweep_%s' % timestr

        with open(filename + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Frequency', 'AC Level', 'Distortion'])

            while freq <= MAX_FREQ:
                queryACLevel(ser, freq)
                time.sleep(1)
                results = getACLevelAndDistortion(ser, freq)

                (acLevel, distortion) = results.split()[:2]

                writer.writerow([freq, acLevel, distortion])
                print "freq: %d hz, ac Level: %s, distortion: %s" % (freq, acLevel, distortion)
                
                freq += stepLog(freq)

        resetToLocalControl(ser)

        # Make a sound to let you know it's finished
        beep()
        beep()
        
    except serial.SerialException, e:
        print e
        
    except KeyboardInterrupt, e:
        resetToLocalControl(ser)
        ser.close()