# RobbyForWindowsPrototype

Author: Chris Schnick
email: chris@schnick.net
Intial release: August 17, 2018

This is my first Pyhon and Github project.  If I have violated any rules of
this community/environment, please let me know and I will correct accordingly.

Robby is a project that is going to target a Raspberry Pi to run an LED light 
show of LEDs mounted inside a Masudaya plastic toy Robby the Robot to be 
eventually added to a Twilight Zone pinball machine. 

This Robby runs in a Windows environment and has been created to develop the 
flow and control logic to eventually be uused in the RPi version. This program
will display X's and 'O's in relative positions as LEDs. An X indicates the LED
in that position is Off and an O indicates the LED in that position is On. This
Robby uses keyboard input to change states whereas the RPi version will use 
lights in the pinball machine to trigger states.

Robby uses threading and a config file.

On the Windows version, keyboard input is used to trigger the events to alter 
the light show as follows: 
   Pressing a 'q' quits the program. 
   Pressing a '1' toggles the dome light on and off. 
   Pressing a '2' primarily toggles the Laser LEDs on and off. 
   Pressing a '3' toggles the scanner LED light show on and off. 
   Pressing a '4' toggles the communications LED show which is an LED blinking 
                  Morse Code. In this case, the Morse Code is depicted as 
				  dots '.' and dashes '-' being displayed. Spaces are used 
				  for the pause between letters and words. The timing of the 
				  morse code complies with International Morse Code Standards.
				  The Morse Code is run in its own thread so that the timing 
				  is Not interferred. This application also uses a config 
				  file to allow the implimentation to specifiy the message that 
				  Robby will blink in Morse Code.  

'keyboard' is included as it has been modified from the base keyboard-0.13.2 
distribution had a bug in the _winkeyboard.py file that has been fixed 
according to the author' s instruction but not included in the current (as 
of this writing) release of keyboard.  Apparently this bug only revealed 
iself on Python 3.7.


