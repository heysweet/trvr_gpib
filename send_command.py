import os.path
import serial
import sys

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

if __name__ == '__main__':

    if len( sys.argv ) != 2:
        print "Usage: ", os.path.basename( sys.argv[0] ), "<Command>"
        sys.exit(1)

    cmd = sys.argv[1];
    
    ser = serial.Serial()

    f = False
    
    try:
        ser = serial.Serial( COM_PORT, 9600, timeout=0.5 )
        ser.write(cmd + "\n")
        print "Successfully wrote: %s" % cmd 
        
    except serial.SerialException, e:
        print e
        
    except KeyboardInterrupt, e:
        resetToLocalControl(ser)
        ser.close()