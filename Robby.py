#!/usr/bin/python
###################################################################################
# To test and develop, I have been using debug modes and stepping through the logic
# and setting next statement to get into the logic associated with each key press.
###################################################################################
'''
Robby.py is a Python program developed to enable development of the
flow and control logic that will be needed for a Raspberry Pi project I
created to animate a plastic toy Robby The Robot.  This toy will have several
LEDs added at key locations to mimic the light effects as shown in the movie
Forbidden Planet version of Robby the Robot.

This program was created by Chris Schnick on Aug 14, 2018

VARIABLE KEY
'morseCodeText'  -> character representation of the message to be sent by morse code
'morseCOde'      -> morse code encrypted message to be sent
'tick'           -> the current iteration countq
'states'         -> list of the 4 states used 0=dome 1=laser 2=scanner 3 = morse code.
                    states is used to turn features on and off
'statesHold'     -> states shadow to enable detection of state changes
'debug'          -> flag to enable debugging messages
'DirL'           -> used by the scanner to set direction of the scan to Left scanning
'DirR'           -> used by the scanner to set direction of the scan to Right scanning
'scannerDirection' -> is the current scan direction of the scanner. Default is to the Right
'scanner' = ['X', 'X', 'X', 'X'] -> rerpesents the 4 LEDs of the scanner at the bottom
                                   of the chest plate
'lasers' = ['X', 'X'] -> rerpesents the 2 LEDs of the lasers on each side of the head
'dome' = ['X']        -> rerpesents the 1 LEDs located in the dome of Robby
'breast' = ['X', 'X'] -> rerpesents the 2 LEDs located in the middle of the chest plate
'morse' = ['X']  -> respresents the LED(s) located in the communications window at the
                   base of the head.  While there may be more then one LED in this area,
                   they will always be on or off at the same time.
'runScanner'     -> boolean used to indicate the Scanner should be running
'runLasers'      -> boolean used to indicate the Lasers should be running
'runMorse'       -> boolean used to indicate the Morse Code should be running
'isMorseRunning' -> boolean used to block multiple instance of the morse event

Morse Code function variables:
'cipher'    -> 'stores the morse translated form of the english string'
'decipher'  -> 'stores the english translated form of the morse string'
'citext'    -> 'stores morse code of a single character'
'i'         -> 'keeps count of the spaces between morse characters'
'message'   -> 'stores the string to be encoded or decoded'
'''

'''
International Morse Code Timing durations
 one time unit standard is 50ms = time.sleep(.05) - time sleep is used to hold the state of the LED on or off for that duration
 1. short mark, dot or "dit" (▄▄▄▄): "dot duration" is one time unit long 
 2. longer mark, dash or "dah" (▄▄▄▄▄▄): three time units long 
 3. inter-element gap between the dots and dashes within a character: 
    one dot duration or one unit long 
 4. short gap (between letters):  three time units long 
 5. medium gap (between words): seven time units long
'''

# Multitreading example used
# from https://www.tutorialspoint.com/python/python_multithreading.htm

# Morse Code translator example used
# from https://www.geeksforgeeks.org/morse-code-translator-python/

# Config File Parser
# from https://docs.python.org/3.4/library/configparser.html


import keyboard
# keyboard fixed as per the following article
# https://github.com/boppreh/keyboard#keyboard.add_hotkey
# https://github.com/boppreh/keyboard/commit/f23d1f29302c673a138929f1e243c79958870c51  
import threading
import time
import os
import configparser


config = configparser.ConfigParser()
config.sections()
config.read('Robby.config')
morseCodeText =  config['Robby']['message']


###################################################################################
# Dictionary representing the morse code chart
###################################################################################
MORSE_CODE_DICT = {'A': '.-',    'B': '-...',
                   'C': '-.-.',  'D': '-..',     'E': '.',
                   'F': '..-.',  'G': '--.',     'H': '....',
                   'I': '..',    'J': '.---',    'K': '-.-',
                   'L': '.-..',  'M': '--',      'N': '-.',
                   'O': '---',   'P': '.--.',    'Q': '--.-',
                   'R': '.-.',   'S': '...',     'T': '-',
                   'U': '..-',   'V': '...-',    'W': '.--',
                   'X': '-..-',  'Y': '-.--',    'Z': '--..',
                   '1': '.----', '2': '..---',   '3': '...--',
                   '4': '....-', '5': '.....',   '6': '-....',
                   '7': '--...', '8': '---..',   '9': '----.',
                   '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.',  '-': '-....-',
                   '(': '-.--.',  ')': '-.--.-'}


###################################################################################
# Function to encrypt the string
# according to the morse code chart
###################################################################################
def encrypt(message):
    cipher = ''
    for letter in message:
        if letter != ' ':

            # Looks up the dictionary and adds the
            # correspponding morse code
            # along with a space to separate
            # morse codes for different characters
            cipher += MORSE_CODE_DICT[letter] + ' '
        else:
            # 1 space indicates different characters
            # and 2 indicates different words
            cipher += ' '

    return cipher


###################################################################################
# Function to decrypt the string
# from morse to english
###################################################################################
def decrypt(message):

    # extra space added at the end to access the
    # last morse code
    message += ' '

    i = 0

    decipher = ''
    citext = ''
    for letter in message:

        # checks for space
        if letter != ' ':

            # counter to keep track of space
            i = 0

            # storing morse code of a single character
            citext += letter

        # in case of space
        else:
            # if i = 1 that indicates a new character
            i += 1

            # if i = 2 that indicates a new word
            if i == 2:
                # adding space to separate words
                decipher += ' '
            else:
                # accessing the keys using their values (reverse of encryption)
                decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT.values()).index(citext)]
                citext = ''

    return decipher


# morseCodeText = "Welcome to Schnicks Gameroom"  # the message will be in a user config file with a defaulted value
morseCode = encrypt(morseCodeText.upper())

# controller
tick = 0

exitNow = False
states = [False, False, False, False]
stateHold = [False, False, False, False]  # state shadow to know if state changed

delay = .15
delayLong = .25
delayShort = .1

debug = False

DirR = "R"
DirL = "L"
scannerDirection = DirR

# light effects
scanner = ['X', 'X', 'X', 'X']
lasers = ['X', 'X']
dome = ['X']
breast = ['X', 'X']
morse = ['X']

runScanner = False
runLasers = False
runMorse = False
isMorseRunning = False


###################################################################################
# Function to clear the screen so that the X's and O's appear to change in place
###################################################################################
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def triggerExit():
    global exitNow
    exitNow = True


def triggerState0():
    global states
    if states[0] is False:
        states[0] = True
    else:
        states[0] = False


def triggerState1():
    global states
    if states[1] is False:
        states[1] = True
    else:
        states[1] = False


def triggerState2():
    global states
    if states[2] is False:
        states[2] = True
    else:
        states[2] = False


def triggerState3():
    global states
    if states[3] is False:
        states[3] = True
    else:
        states[3] = False


###################################################################################
# Class to define the thread that monitors the current state of the application.
# This captureskeyboard imput to turn on and off flags used to turn on and off
# features.
# In the RPi implemetation, the states will be triggered by IO input based
# lights in the pinball machine being turned on and off by the pinball machine.
###################################################################################
class MonitorState (threading.Thread):
    ###################################################################################
    # Function to define the thread
    ###################################################################################
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    ###################################################################################
    # Function to run the thread - this is the main() thread of this application
    ###################################################################################
    def run(self):
        global tick
        global states
        global delay
        global exitNow

        while True:  # making a loop1111q
            if exitNow:   # if key 'q' is pressed
                    break  # finishing the loop
            # elif is_pressed('1'):   # if key '1' is pressed
            #     if states[0] is False:
            #         states[0] = True
            #     else:
            #         states[0] = False
            # elif is_pressed('2'):  # if key '2' is pressed
            #     if states[1] is False:
            #         states[1] = True
            #     else:
            #         states[1] = False
            # elif is_pressed('3'):  # if key '3' is pressed
            #     if states[2] is False:
            #         states[2] = True
            #     else:
            #         states[2] = False
            # elif is_pressed('4'):  # if key '4' is presse1423qd
            #     if states[3] is False:
            #         states[3] = True
            #     else:
            #         states[3] = False
            else:
                pass

            if process_current_state():
                if debug:
                    print('============= S T A T E   C H A N G E D ==============')
                copy_state_to_hold()
            else:
                if debug:
                    print('****************************************')

            if debug:
                print("state is: " + str(states))
                print("stateHold is: " + str(stateHold))

            print(" ")

            if dome[0] == 'On':
                print("      O")
            else:
                print("      X")

            run_laser_show()
            run_morse_show()
            run_scanner_show()

            tick += 1
            print(tick)

            time.sleep(.25)

            cls()


###################################################################################
# Class to define the thread the runs the Morse Code.
# Morse Code gets its own thread beacause the timing of the flashes needs to be
# independent of the other LEDs being imploemented in Robby.
###################################################################################
class RunMorseCode (threading.Thread):
    ###################################################################################
    # Function to initialize the thread
    ###################################################################################
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    ###################################################################################
    # Function to run the thread
    ###################################################################################
    def run(self):
        global isMorseRunning
        global morseCode

        isMorseRunning = True

        print(morseCode)

        for dotdash in morseCode:
            if dotdash == '.':
                short_blink()
            elif dotdash == '-':
                long_blink()
            else:
                long_off()

        isMorseRunning = False


###################################################################################
# Function used by the run Morse Code to produce a pause used between characters
###################################################################################
def short_off():
    if debug:
        print("In short_off()")
    print("")
    time.sleep(.05)

	
###################################################################################
# Function used by the run Morse Code to produce a long pause used between 
# characters and words.  The encrypt method inserts one space between letters and
# two spaces between words so only one method is needed to handle both cases
###################################################################################
def long_off():
    if debug:
        print("In word_off()")
    print(" ")
    time.sleep(.17)	
		
		
###################################################################################
# TODO: This needs to be coded to blink the LED according to the morse code
# Function used by the run Morse Code to produce a short blink like a 'dot'
###################################################################################
def short_blink():
    if debug:
        print("In short_blink()")
    print(".")
    time.sleep(.05)
    short_off()


###################################################################################
# Function used by the run Morse Code to produce a long blink like a 'dash'
###################################################################################
def long_blink():
    if debug:
        print("In long_blink()")
    print("-")
    time.sleep(.15)
    short_off()


###################################################################################
# Function run morse show determines if Morse is already running and if it is not and it
# needs to be, trigger the thread
###################################################################################
def run_morse_show():
    global runMorse
    global isMorseRunning

    if debug:
        print("In run_morse_show()")

    if runMorse and not isMorseRunning:
        runMorseThread = RunMorseCode(1)
        runMorseThread.start()
    else:
        print(" ")


###################################################################################
# Function used to run the lasers show
###################################################################################
def run_laser_show():
    global runLasers

    if debug:
        print("In run_laser_show()")

    if runLasers:
        if lasers[0] == 'O':
            lasers[0] = 'X'
            lasers[1] = 'O'
        else:
            lasers[0] = 'O'
            lasers[1] = 'X'
    else:
        lasers[0] = 'X'
        lasers[1] = 'X'
    print(' ' + lasers[0] + '         ' + lasers[1])


###################################################################################
# Function used to run the scanner show
###################################################################################
def run_scanner_show():
    global runScanner
    global scanner
    global scannerDirection

    if debug:
        print("In run_scanner_show()")

    if runScanner:
        if scannerDirection == DirR:
            if scanner[0] == 'O':
                scanner[0] = 'X'
                scanner[1] = 'O'
            elif scanner[1] == 'O':
                scanner[1] = 'X'
                scanner[2] = 'O'
            elif scanner[2] == 'O':
                scanner[2] = 'X'
                scanner[3] = 'O'
            else:
                scannerDirection = DirL
        else:
            if scanner[3] == 'O':
                scanner[2] = 'O'
                scanner[3] = 'X'
            elif scanner[2] == 'O':
                scanner[1] = 'O'
                scanner[2] = 'X'
            elif scanner[1] == 'O':
                scanner[0] = 'O'
                scanner[1] = 'X'
            else:
                scannerDirection = DirR
    else:
        scanner = ['X', 'X', 'X', 'X']

    print('   ' + scanner[0] + ' ' + scanner[1] + ' ' + scanner[2] + ' ' + scanner[3])


###################################################################################
# Function used to copy the current state to the hold state
###################################################################################
def copy_state_to_hold():
    if debug:
        print("In copy_state_to_hold()")

    i = 0
    for state in states:
        stateHold[i] = state
        i += 1


###################################################################################
# Function used to analyze the state and any changes that may have occured
# and then to also turn on and off the various features accordingly
###################################################################################
def process_current_state():
    global runLasers
    global runScanner
    global runMorse

    if debug:
        print("In process_current_state()")

    _stateChanged = False
    if states[0] is True and stateHold[0] is False:
        # state[0] changed to On - Do stuff
        _stateChanged = True
        dome[0] = 'On'
    elif states[0] is False and stateHold[0] is True:
        # state[0] changed to Off - Do stuff
        _stateChanged = True
        dome[0] = 'Off'
    else:
        pass

    if states[1] is True and stateHold[1] is False:
        # state[1] changed to On - Do stuff
        _stateChanged = True
        runLasers = True
    elif states[1] is False and stateHold[1] is True:
        # state[1] changed to Off - Do stuff
        _stateChanged = True
        runLasers = False
    else:
        pass

    if states[2] is True and stateHold[2] is False:
        # state[2] changed to On - Do stuff
        _stateChanged = True
        runScanner = True
        scanner[0] = "O"
    elif states[2] is False and stateHold[2] is True:
        # state[2] changed to Off - Do stuff
        _stateChanged = True
        runScanner = False
        scanner[0] = 'X'
        scanner[1] = 'X'
        scanner[2] = 'X'
        scanner[3] = 'X'
    else:
        pass

    if states[3] is True and stateHold[3] is False:
        # state[3] changed to On - Do stuff
        _stateChanged = True
        runMorse = True
    elif states[3] is False and stateHold[3] is True:
        # state[3] changed to Off - Do stuff
        _stateChanged = True
        runMorse = False
    else:
        pass

    return _stateChanged


keyboard.add_hotkey('q', triggerExit)
keyboard.add_hotkey('1', triggerState0)
keyboard.add_hotkey('2', triggerState1)
keyboard.add_hotkey('3', triggerState2)
keyboard.add_hotkey('4', triggerState3)


###################################################################################
# Create new thread for main
###################################################################################
thread = MonitorState(1)

###################################################################################
# start main process as a thread
###################################################################################
thread.start()
