# Modified NeoPixel earrings example.
#
# Change mode by touching A0.
# Change color by touching A1.

import board
import neopixel
import time
from touchio import TouchIn
import adafruit_dotstar as dotstar
try:
	import urandom as random  # for v1.0 API support
except ImportError:
	import random

# Neopixel ring
numpix = 16  # Number of NeoPixels (e.g. 16-pixel ring)
pixpin = board.D0  # Pin where NeoPixels are connected
strip  = neopixel.NeoPixel(pixpin, numpix, brightness=.015, bpp=4,
                           auto_write=False)

# Turn off the onboard dotstar RGB to avoid distractions
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)
dot[0] = (0, 0, 0)
dot.show()

# Capacitive touch on A0 (change mode) and A1 (change color)
modepin = board.A0
nextmode = TouchIn(modepin)
colorpin = board.A1
nextcolor = TouchIn(colorpin)

def wheel(pos):
	# Input a value 0 to 255 to get a color value.
	# The colours are a transition r - g - b - back to r.
	if (pos < 0) or (pos > 255):
		return [0, 0, 0, 0]
	elif (pos < 85):
		return [int(pos * 3), int(255 - (pos * 3)), 0, 0]
	elif (pos < 170):
		pos -= 85
		return [int(255 - pos * 3), 0, int(pos * 3), 0]
	else:
		pos -= 170
		return [0, int(pos * 3), int(255 - pos * 3), 0]

def rainbow_cycle(wait):
	for j in range(0, 255, 16):
		for i in range(len(strip)):
			idx = int ((i * 256 / len(strip)) + j)
			strip[i] = wheel(idx & 255)
		strip.show()
		if nextmode.value:
			return # yes, step to next, abort this function
		time.sleep(wait)

mode     = 0  # Current animation effect
offset   = 0  # Position of spinner animation
hue      = 0  # Starting hue
color    = wheel(hue & 255)  # hue -> RGB color

while True:  # Loop forever...
	if mode == 0:  # Random sparkles - lights just one LED at a time
		i = random.randint(0, numpix - 1)  # Choose random pixel
		strip[i] = color   # Set it to current color
		strip.show()      # Refresh LED states
		# Set same pixel to "off" color now but DON'T refresh...
		# it stays on for now...both this and the next random
		# pixel will be refreshed on the next pass.
		strip[i] = [0,0,0,0]
		time.sleep(0.008)  # 8 millisecond delay
	elif mode == 1:  # Spinny wheel (4 LEDs on at a time)
		for i in range(numpix):  # For each LED...
			if ((offset + i) & 7) < 2:  # 2 pixels out of 8...
				strip[i] = color    # are set to current color
			else:
				strip[i] = [0,0,0,0]  # other pixels are off
		strip.show()    # Refresh LED states
		time.sleep(0.04) # 40 millisecond delay
		offset += 1      # Shift animation by 1 pixel on next frame
		if offset >= 8: offset = 0
	elif mode == 2: # rainbow cycle
		rainbow_cycle(0.1) # 1 ms delay per step
	# Additional animation modes could be added here!

	if nextmode.value:
		mode += 1               # Advance to next mode
		if mode > 2:            # End of modes?
			mode  =  0      # Start over from beginning
		strip.fill([0,0,0,0])   # Turn off all pixels
		time.sleep(0.5)         # Give some time to release the finger

	if nextcolor.value:
		hue  += 80                    # And change color
		color = wheel(hue & 255)
		time.sleep(0.5)               # Give some time to release the finger
