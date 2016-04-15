#!/usr/bin/env python
#
# W. H. Bell
#
# A python script to show the orginal MagPi logo on the screen
# of a Nokia LCD display.
#
import time
from nokiaSPI import NokiaSPI

# Create a noki object
noki = NokiaSPI()

try:
  print("Type CTRL-C to exit.")

  # Load the image on the screen
  noki.load_bitmap("../images/MagPi-nokia-bw-rotated-mc.bmp",True)

  # Keep the image on the screen
  while 1:
    time.sleep(100)

# Clean up the noki object if CTRL-C is pressed
except KeyboardInterrupt:
  print("Exiting")
  noki.cleanup()
