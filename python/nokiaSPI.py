#!/usr/bin/env python
# 
# A Python package to drive a Nokia 5110/3310 monochrome LCD
# 
# This code started life on the Raspberry Pi forum.  Since that time, the
# dependency on wiringpi has been removed.
#
# Comments from the forum:
#=========================================
# code improvements
#  9/10/12
######
# WGG - picked up from Raspberry Pi forums and modified with a heavy hand
# -- added spidev support
# -- testing with PIL
# 16-Jan-2013
# -- initial NokiaSPI class
#=========================================

import time
import spidev
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO

# White backlight
CONTRAST = 0xbb

# Blue backlight
#CONTRAST = 0xa4

ROWS = 6
COLUMNS = 14
PIXELS_PER_ROW = 6
ON = 1
OFF = 0

# GPIO pins, using the BCM numbering scheme
DC   = 22
RST  = 17
LED  = 18

CLSBUF=[0]*(ROWS * COLUMNS * PIXELS_PER_ROW)

FONT = {
  ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
  '!': [0x00, 0x00, 0x5f, 0x00, 0x00],
  '"': [0x00, 0x07, 0x00, 0x07, 0x00],
  '#': [0x14, 0x7f, 0x14, 0x7f, 0x14],
  '$': [0x24, 0x2a, 0x7f, 0x2a, 0x12],
  '%': [0x23, 0x13, 0x08, 0x64, 0x62],
  '&': [0x36, 0x49, 0x55, 0x22, 0x50],
  "'": [0x00, 0x05, 0x03, 0x00, 0x00],
  '(': [0x00, 0x1c, 0x22, 0x41, 0x00],
  ')': [0x00, 0x41, 0x22, 0x1c, 0x00],
  '*': [0x14, 0x08, 0x3e, 0x08, 0x14],
  '+': [0x08, 0x08, 0x3e, 0x08, 0x08],
  ',': [0x00, 0x50, 0x30, 0x00, 0x00],
  '-': [0x08, 0x08, 0x08, 0x08, 0x08],
  '.': [0x00, 0x60, 0x60, 0x00, 0x00],
  '/': [0x20, 0x10, 0x08, 0x04, 0x02],
  '0': [0x3e, 0x51, 0x49, 0x45, 0x3e],
  '1': [0x00, 0x42, 0x7f, 0x40, 0x00],
  '2': [0x42, 0x61, 0x51, 0x49, 0x46],
  '3': [0x21, 0x41, 0x45, 0x4b, 0x31],
  '4': [0x18, 0x14, 0x12, 0x7f, 0x10],
  '5': [0x27, 0x45, 0x45, 0x45, 0x39],
  '6': [0x3c, 0x4a, 0x49, 0x49, 0x30],
  '7': [0x01, 0x71, 0x09, 0x05, 0x03],
  '8': [0x36, 0x49, 0x49, 0x49, 0x36],
  '9': [0x06, 0x49, 0x49, 0x29, 0x1e],
  ':': [0x00, 0x36, 0x36, 0x00, 0x00],
  ';': [0x00, 0x56, 0x36, 0x00, 0x00],
  '<': [0x08, 0x14, 0x22, 0x41, 0x00],
  '=': [0x14, 0x14, 0x14, 0x14, 0x14],
  '>': [0x00, 0x41, 0x22, 0x14, 0x08],
  '?': [0x02, 0x01, 0x51, 0x09, 0x06],
  '@': [0x32, 0x49, 0x79, 0x41, 0x3e],
  'A': [0x7e, 0x11, 0x11, 0x11, 0x7e],
  'B': [0x7f, 0x49, 0x49, 0x49, 0x36],
  'C': [0x3e, 0x41, 0x41, 0x41, 0x22],
  'D': [0x7f, 0x41, 0x41, 0x22, 0x1c],
  'E': [0x7f, 0x49, 0x49, 0x49, 0x41],
  'F': [0x7f, 0x09, 0x09, 0x09, 0x01],
  'G': [0x3e, 0x41, 0x49, 0x49, 0x7a],
  'H': [0x7f, 0x08, 0x08, 0x08, 0x7f],
  'I': [0x00, 0x41, 0x7f, 0x41, 0x00],
  'J': [0x20, 0x40, 0x41, 0x3f, 0x01],
  'K': [0x7f, 0x08, 0x14, 0x22, 0x41],
  'L': [0x7f, 0x40, 0x40, 0x40, 0x40],
  'M': [0x7f, 0x02, 0x0c, 0x02, 0x7f],
  'N': [0x7f, 0x04, 0x08, 0x10, 0x7f],
  'O': [0x3e, 0x41, 0x41, 0x41, 0x3e],
  'P': [0x7f, 0x09, 0x09, 0x09, 0x06],
  'Q': [0x3e, 0x41, 0x51, 0x21, 0x5e],
  'R': [0x7f, 0x09, 0x19, 0x29, 0x46],
  'S': [0x46, 0x49, 0x49, 0x49, 0x31],
  'T': [0x01, 0x01, 0x7f, 0x01, 0x01],
  'U': [0x3f, 0x40, 0x40, 0x40, 0x3f],
  'V': [0x1f, 0x20, 0x40, 0x20, 0x1f],
  'W': [0x3f, 0x40, 0x38, 0x40, 0x3f],
  'X': [0x63, 0x14, 0x08, 0x14, 0x63],
  'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
  'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
  '[': [0x00, 0x7f, 0x41, 0x41, 0x00],
  '\\': [0x02, 0x04, 0x08, 0x10, 0x20],
  ']': [0x00, 0x41, 0x41, 0x7f, 0x00],
  '^': [0x04, 0x02, 0x01, 0x02, 0x04],
  '_': [0x40, 0x40, 0x40, 0x40, 0x40],
  '`': [0x00, 0x01, 0x02, 0x04, 0x00],
  'a': [0x20, 0x54, 0x54, 0x54, 0x78],
  'b': [0x7f, 0x48, 0x44, 0x44, 0x38],
  'c': [0x38, 0x44, 0x44, 0x44, 0x20],
  'd': [0x38, 0x44, 0x44, 0x48, 0x7f],
  'e': [0x38, 0x54, 0x54, 0x54, 0x18],
  'f': [0x08, 0x7e, 0x09, 0x01, 0x02],
  'g': [0x0c, 0x52, 0x52, 0x52, 0x3e],
  'h': [0x7f, 0x08, 0x04, 0x04, 0x78],
  'i': [0x00, 0x44, 0x7d, 0x40, 0x00],
  'j': [0x20, 0x40, 0x44, 0x3d, 0x00],
  'k': [0x7f, 0x10, 0x28, 0x44, 0x00],
  'l': [0x00, 0x41, 0x7f, 0x40, 0x00],
  'm': [0x7c, 0x04, 0x18, 0x04, 0x78],
  'n': [0x7c, 0x08, 0x04, 0x04, 0x78],
  'o': [0x38, 0x44, 0x44, 0x44, 0x38],
  'p': [0x7c, 0x14, 0x14, 0x14, 0x08],
  'q': [0x08, 0x14, 0x14, 0x18, 0x7c],
  'r': [0x7c, 0x08, 0x04, 0x04, 0x08],
  's': [0x48, 0x54, 0x54, 0x54, 0x20],
  't': [0x04, 0x3f, 0x44, 0x40, 0x20],
  'u': [0x3c, 0x40, 0x40, 0x20, 0x7c],
  'v': [0x1c, 0x20, 0x40, 0x20, 0x1c],
  'w': [0x3c, 0x40, 0x30, 0x40, 0x3c],
  'x': [0x44, 0x28, 0x10, 0x28, 0x44],
  'y': [0x0c, 0x50, 0x50, 0x50, 0x3c],
  'z': [0x44, 0x64, 0x54, 0x4c, 0x44],
  '{': [0x00, 0x08, 0x36, 0x41, 0x00],
  '|': [0x00, 0x00, 0x7f, 0x00, 0x00],
  '}': [0x00, 0x41, 0x36, 0x08, 0x00],
  '~': [0x10, 0x08, 0x08, 0x10, 0x08],
  '\x7f': [0x00, 0x7e, 0x42, 0x42, 0x7e],
}

ORIGINAL_CUSTOM = FONT['\x7f']

def bit_reverse(value, width=8):
  result = 0
  for _ in xrange(width):
    result = (result << 1) | (value & 1)
    value >>= 1

  return result

BITREVERSE = map(bit_reverse, xrange(256))

class NokiaSPI:
    def __init__(self, dev=(0,0),speed=5000000, brightness=256, contrast=CONTRAST):
        self.spi = spidev.SpiDev()
        self.speed = speed
        self.dev = dev
        self.spi.open(self.dev[0],self.dev[1])
        self.spi.max_speed_hz=self.speed
        self.dc = DC
        self.rst = RST

        # Setup the GPIO pins
        GPIO.setmode(GPIO.BCM)
        for pin in [self.dc, self.rst]:
          GPIO.setup(pin,GPIO.OUT)

        self.contrast=contrast
        self.brightness=brightness
       
        # Toggle RST low to reset.
        GPIO.output(self.rst, 0)
        time.sleep(0.1)
        GPIO.output(self.rst, 1)

        # Extended mode, bias, vop, basic mode, non-inverted display.
        GPIO.output(self.dc, 0)
        self.spi.writebytes([0x21, 0x14, self.contrast, 0x20, 0x0c])
        # cls()

        self.ledpin = LED
        GPIO.setup(self.ledpin, GPIO.OUT)
        GPIO.output(self.ledpin, 1)

    def lcd_cmd(self,value):
        GPIO.output(self.dc, 0)
        self.spi.writebytes([value])

    def lcd_data(self,value):
        GPIO.output(self.dc, 1)
        self.spi.writebytes([value])

    def gotoxy(self, x, y):
        GPIO.output(self.dc, 0)
        self.spi.writebytes([x+128,y+64])

    def cls(self):
        self.gotoxy(0, 0)
        GPIO.output(self.dc, 1)
        self.spi.writebytes(CLSBUF)

    def led(self, led_value):
        ##if self.ledpin == 1:
        ##    wiringpi.pwmWrite(self.ledpin,led_value)
        ##else:
            if led_value == 0:
                GPIO.output(self.ledpin, 0)
            else:
                GPIO.output(self.ledpin, 1)

    def load_bitmap(self, filename, reverse=False):
        mask = 0xff if reverse else 0x00
        self.gotoxy(0, 0)
        with open(filename, 'rb') as bitmap_file:
            for x in xrange(6):
              for y in xrange(84):
                bitmap_file.seek(0x3e + y * 8 + x)
                self.lcd_data(BITREVERSE[ord(bitmap_file.read(1))] ^ mask)

    def show_custom(self, font=FONT):
        self.display_char('\x7f', font)

    def define_custom(self, values):
        FONT['\x7f'] = values

    def restore_custom(self):
        self.define_custom(ORIGINAL_CUSTOM)

    def alt_custom(self):
        self.define_custom([0x00, 0x50, 0x3C, 0x52, 0x44])

    def pi_custom(self):
        self.define_custom([0x19, 0x25, 0x5A, 0x25, 0x19])

    def display_char(self, char, font=FONT):
        try:
            GPIO.output(self.dc, 1)
            self.spi.writebytes(font[char]+[0])

        except KeyError:
            pass # Ignore undefined characters.

    def text(self, string, font=FONT):
        for char in string:
            self.display_char(char, font)


    def gotorc(self, r, c):
        self.gotoxy(c*6,r)

    def centre_word(self, r, word):
        self.gotorc(r, max(0, (COLUMNS - len(word)) // 2))
        self.text(word)

    def show_image(self,im):
        # Rotate and mirror the image
        rim = im.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)

        # Change display to vertical write mode for graphics
        GPIO.output(self.dc, 0)
        self.spi.writebytes([0x22])

        # Start at upper left corner
        self.gotoxy(0, 0)
        # Put on display with reversed bit order
        GPIO.output(self.dc, 1)
        self.spi.writebytes( [ BITREVERSE[ord(x)] for x in list(rim.tostring()) ] )

        # Switch back to horizontal write mode for text
        GPIO.output(self.dc, 0)
        self.spi.writebytes([0x20])

    def cleanup(self):
        self.led(0)
        self.spi.close()
        GPIO.cleanup()


