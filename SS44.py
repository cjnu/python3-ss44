#!/usr/bin/python3

import serial
import time

class SS44:
    """This class is for the control of the Broadcast Tools SS 4.4 Stereo
    Matrix Switcher"""


    def __init__(self, port='/dev/ttyUSB0', baud=9600, unit=0):
        """Initialize the serial port, and set the unit number (defaults to 0)"""
        self.ser  = serial.Serial(port, baud, timeout=1)
        self.u = unit


    def _writeSerial(self, c):
        """Write the formatted command to the serial port, flushing after
        write"""
        self.ser.write(bytes(c.encode('utf-8')))
        self.ser.flush()


    def muteAll(self):
        """Mutes all outputs"""
        command = f'*{self.u}MA'
        self._writeSerial(command)


    def mute(self, ii, o):
        """Mute a specific input ii on output o"""
        command = f'*{self.u}{ii:02d}M{o}'
        self._writeSerial(command)


    def connect(self, ii, o):
        """Connects a specific input ii to output o"""
        command = f'*{self.u}{ii:02d}{o}'
        self._writeSerial(command)


    def readState(self):
        """Read the status output from the SS 4.4.  After every change of state
        (i.e. mute or connect) the SS 4.4 will output a 4 line status output.
        Parse this into a dictionary of lists"""
        results = {}        # initialize dict

        # read 4 lines of input until we see the newline.  Decode to UTF-8, and
        # strip off the CR/NL at the end.
        lines = []
        for x in range(4):
            lines.append(self.ser.read_until().decode('utf-8').strip())

        # Output lines look like:
        # S0L1,0,1,0,0
        # S0L2,0,0,0,1
        # S0L3,0,0,0,1
        # S0L4,0,0,0,1
        # Where S means status, 0 is the unit number, L1, L2, L3, L4 are the
        # outputs, and then the next 4 0's and 1's represent which input is
        # connected to the output.  We'll split on the comma's, and only
        # include the 0's and 1's.
        # This is a bit tricky.  I want to have a list of booleans (True/False)
        # that corresponds to the index of the input, but lists in python start
        # at 0.  So, I create a list that has a none in the zero'th position,
        # then Trues and Falses based on inputs 1-4.
        i = 1
        for line in lines:
            results[i] = [ None ] + [ j == '1' for j in line.split(',')[1:5] ]
            i += 1

        return results


    def printState(self):
        """Print a simple string of 16 ones and zeros to indicate the state of
        the switcher"""
        command = f'*{self.u}SL'
        self._writeSerial(command)
        state = self.readState()
        for o in sorted(state):
            inputs = state[o][1:]
            for ii in inputs:
                if ii:
                    print('1', end='')
                else:
                    print('0', end='')
        print()


    def switchOutput(self, ii, o):
        """connect input ii to output o, muting any other active inputs on that
        output.  Simulates pressing the button on the front panel."""
        # Connect the input to the output
        self.connect(ii, o)

        # After every change of state, the switcher prints the new status, read
        # that.
        results = self.readState()

        # Verify it switched
        if results[o][ii] != True:
            print("Error, didn't connect input {i} to output {o}")

        # When we connect an input, we want to find what previous input was
        # connected, and mute that one.  Go through the list, find the input
        # that's true that's NOT the input we were asked to connect, and mute
        # it.
        for i in range(len(results[o])):
            if i != ii and results[o][i] == True:
                self.mute(i, o)
                # We've changed the state, (by muting) so we'll get a status
                # from the switcher.  Read it and make sure we're now off.
                newstatus = self.readState()
                if newstatus[o][i] != False:
                    print("Error, didn't mute input {i} on output {o}")



if __name__ == '__main__':
    import sys

    print(f'Communicating to SS 4.4 on port {sys.argv[1]}')

    # Create out ss44 object
    ss44 = SS44(port=sys.argv[1])

    # Print the initial state
    ss44.printState()

    # Excercize the outputs
    print('Excercise output 1')
    ss44.switchOutput(1, 1)
    ss44.switchOutput(2, 1)
    ss44.switchOutput(3, 1)
    ss44.switchOutput(4, 1)

    print('Excercise output 2')
    ss44.switchOutput(1, 2)
    ss44.switchOutput(2, 2)
    ss44.switchOutput(3, 2)
    ss44.switchOutput(4, 2)

    print('Excercise output 3')
    ss44.switchOutput(1, 3)
    ss44.switchOutput(2, 3)
    ss44.switchOutput(3, 3)
    ss44.switchOutput(4, 3)

    print('Excercise output 4')
    ss44.switchOutput(1, 4)
    ss44.switchOutput(2, 4)
    ss44.switchOutput(3, 4)
    ss44.switchOutput(4, 4)

    ss44.printState()

    print('sleeping for 2 seconds')
    time.sleep(2)

    print('Mute All')
    ss44.muteAll()
