#!/usr/bin/env python
#
# W. H. Bell
#
# A python script to show the current IP address(s) on the screen
# of a Nokia LCD display.
#

import netifaces
import time
from nokiaSPI import NokiaSPI

#---------------------------------------------------

def addresses():
  interfaces = netifaces.interfaces()

  addrs=[]
  for i in interfaces:
    if i == 'lo':
      continue
    iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
    if iface != None:
      for j in iface:
        addrs += [j['addr']]

  return addrs

#---------------------------------------------------

def fillStr(text):
  newStr = ""
  nchar = len(text)
  for i in xrange(14):
    if i < nchar:
      newStr += text[i]
    else:
      newStr += " "
  return newStr
  

#---------------------------------------------------

noki = NokiaSPI((0,0),5000000, 0)
noki.cls()
noki.text("\x7f \x7f \x7f \x7f \x7f \x7f \x7f ")
noki.text(fillStr("Checking the "))
noki.text(fillStr("IP address..."))
time.sleep(3)

try:
  print("Type CTRL-C to exit.")
  while 1:
    noki.cls()
    addrs = addresses()
    noki.text(fillStr("IP address:"))
    for a in addrs:
      noki.text(fillStr(a))
    time.sleep(2)
except KeyboardInterrupt:
  print("Exiting")
  noki.cleanup()
finally:
  print("Finished")
