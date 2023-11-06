#!/usr/bin/env python3
# 7 segment neopixel display
# This is meant to be just a part of a neopixel chain
# The entire neopixel chain needs to be instantiated outside of this file
# and then passed in with an offset
import time
import board
import neopixel
import asyncio
from logger import log as log

# the 7 seg is a series of 7 (4 pixel) segments
# the order of segments is as follow
# described using an index 0..6
#   3 3 3 3
#  2       4
#  2       4
#  2       4
#  2       4
#   5 5 5 5
#  1       6
#  1       6
#  1       6
#  1       6
#   0 0 0 0
# we can define characters as an array of segment indicies
# order of indicies doesn't matter
lookup = {} # dict to use string as index
lookup['0'] = [0,1,2,3,4,6]
lookup['1'] = [4,6]
lookup['2'] = lookup['Z'] = lookup['z'] = [3,4,5,1,0]
lookup['3'] = [0,6,5,4,3]
lookup['4'] = [2,4,5,6]
lookup['5'] = lookup['S'] = lookup['s'] = [3,2,5,6,0]
lookup['6'] = [3,2,5,6,1,0]
lookup['7'] = [3,4,6]
lookup['8'] = [2,3,4,5,1,6,0]
lookup['9'] = [2,3,4,5,6,0]
lookup['A'] = lookup['a'] = [1,6,5,2,3,4]
lookup['B'] = lookup['b'] = [1,2,5,6,0]
lookup['C'] = lookup['c'] = [3,2,1,0]
lookup['D'] = lookup['d'] = [1,5,0,6,7]
lookup['E'] = lookup['e'] = [2,3,5,1,0]
lookup['F'] = lookup['f'] = [1,2,5,3]
lookup['G'] = lookup['g'] = [3,2,1,0,6]
lookup['H'] = lookup['h'] = [2,5,1,6]
lookup['I'] = lookup['i'] = [6]
lookup['J'] = lookup['j'] = [4,6,0,1]
lookup['K'] = lookup['k'] = [2,5,1,6,3]
lookup['L'] = lookup['l'] = [2,1,0]
lookup['M'] = lookup['m'] = [1,5,6,3]
lookup['N'] = lookup['n'] = [1,6,5]
lookup['O'] = lookup['o'] = [1,5,6,0]
lookup['P'] = lookup['p'] = [1,5,2,3,4]
lookup['Q'] = lookup['q'] = [5,2,3,4,6]
lookup['R'] = lookup['r'] = [1,5]
lookup['T'] = lookup['t'] = [0,1,5,2]
lookup['U'] = lookup['u'] = [2,1,0,6,4]
lookup['V'] = lookup['v'] = [1,2,3]
lookup['W'] = lookup['w'] = [2,5,4,0]
lookup['X'] = lookup['x'] = [2,4,5,1,6]
lookup['Y'] = lookup['y'] = [2,4,5,6,0]
lookup['-'] = [5]

green = (0, 255, 0)
red = (255, 0, 0)

# 'digits' input is a list of integers describing the per-segment pixel count
# this is to support multiple 7seg characters that have different sizes
# length of this list is the number of digits

class Neo7Seg:
    def __init__(self, pixels, offset, digits):
        self._pixels = pixels  # the already instantiated neopixel object
        self._offset = offset   # the stringing offset of the first pix in the neopixel chain
        self._num_digits = len(digits)
        self._digits = digits
        self._value = "00"
        self._color = green
        self.clear()

    def clear(self):
        for p in range(len(self._pixels)):
            self._pixels[p] = (0,0,0)
        self._pixels.show()

    # pixels = neopixels instantiated outside this function
    # offset = the offset for the first pixel in 7seg in the entire neopixel chain
    # value = character to display
    # color = (r,b,g)
    def set(self, value, color = green, wait = 0.5):
        self._value = value
        self._color = color
        self.clear()

        if isinstance(value, float):
            val = int(value)
            string = str(val).zfill(2)
        elif isinstance(value, int):
            string = str(value).zfill(2)
        else:
            string = value

        c = 0
        char_pixel_start = self._offset
        for char in string:
            # account for out of order lookup definition
            # so we can track char_pixel_start properly
            character = sorted(lookup[char])
            pix_per_seg = self._digits[c]
            #log.debug(f"char_pixel_start {char_pixel_start} char {char} pix_per_seg {pix_per_seg} character {character}")
            for s in character:
                for p in range (0, pix_per_seg):
                    next_pixel = char_pixel_start + (s * pix_per_seg) + p
                    self._pixels[next_pixel] = color
                    #log.debug(f"next_pixel {next_pixel}")
            char_pixel_start += 7 * pix_per_seg
            c += 1
        self._pixels.show()

#        if len(string) > self._num_digits:
            # cycles through the characters in the string

    # not a good idea to use _value to keep track of a score or something like that.
    # but this is here is case the app wants to get the current state of the 7seg(s)
    def get(self):
        return self._value

    async def rainbow_digits(self, duration_sec):
        log.debug("rainbox digits")
        red = (255,0,0)
        orange = (255,127,0)
        yellow = (255,255,0)
        green = (0,255,0)
        blue = (0,0,255)
        teal = (0,255,255)
        violet = (148,0,211)
        rb = [red, orange, yellow, green, blue, teal, violet]
        start = t = time.monotonic()

        i = 0
        while time.monotonic() <= (start + duration_sec):
            c = 0
            char_pixel_start = self._offset
            for char in string:
                # account for out of order lookup definition
                # so we can track char_pixel_start properly
                character = sorted(lookup[char])
                pix_per_seg = self._digits[c]
                for s in character:
                    for p in range (0, pix_per_seg):
                        next_pixel = char_pixel_start + (s * pix_per_seg) + p
                        self._pixels[next_pixel] = rb[(i + s) % 7]
                char_pixel_start += 7 * pix_per_seg
                c += 1
                        
            i += 1
            self._pixels.show()
            await asyncio.sleep(0.05)
        # restore previous setting after animation is done.
        self.set(self._value, self._color)