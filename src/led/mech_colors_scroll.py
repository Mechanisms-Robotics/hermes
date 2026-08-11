from machine import Pin
from neopixel import NeoPixel
import time

num_leds = 100
np = NeoPixel(Pin(2), num_leds)

def status_light_on():
    led = Pin(25, Pin.OUT)
    led.on()
    
def status_light_off():
    led = Pin(25, Pin.OUT)
    led.off()
    
def clear_leds():
    for i in range(num_leds):
        set_led(i, off)
    np.write()

# color is an array of RGB values ranging 0 to 255
def set_led(index, color):
    # unpack the colors
    r, g, b = color
    
    # flip the red and green because WS2811 LED is weird
    np[index] = (g, r, b)

status_light_on()

off    = (0,0,0)
gold = (50, 7, 0)
white = (20, 20, 15)

# Mech Colors
mech_colors = [
    white,
    gold,
    white,
    gold,
    white,
    gold,
    white,
    gold,
    white,
    gold
]

# Build up the mech colors first (LEDs 0-6)
for step in range(len(mech_colors)):
    # Turn all off
    for j in range(num_leds):
        set_led(j, off)
    
    # Light up LEDs 0 through step with rainbow colors
    for i in range(step + 1):
        set_led(i, mech_colors[i])
    
    np.write()
    time.sleep(0.1)

# Now scroll the complete mech colors across the strip
# since we already have the mech colors at position 0, this loop
# starts at position 1
for position in range(1, num_leds - len(mech_colors) + 1):
    # Turn all off
    for j in range(num_leds):
        set_led(j, off)
        
    # Draw rainbow starting at position
    for i in range(len(rainbow)):
        set_led(position + i, mech_colors[i])
    
    np.write()
    time.sleep(0.1)

clear_leds()