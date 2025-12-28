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
red    = (255,0,0)
orange = (255,127,0)
yellow = (255,255,0)
green  = (0,255,0)
blue   = (0,0,255)
indigo = (75,0,130)
violet = (148,0,211)

# Rainbow
rainbow = [
    red,
    orange,
    yellow,
    green,
    blue,
    indigo,
    violet
]

# Build up the rainbow first (LEDs 0-6)
for step in range(len(rainbow)):
    # Turn all off
    for j in range(num_leds):
        set_led(j, off)
    
    # Light up LEDs 0 through step with rainbow colors
    for i in range(step + 1):
        set_led(i, rainbow[i])
    
    np.write()
    time.sleep(0.1)

# Now scroll the complete rainbow across the strip
# since we already have the rainbow at position 0, this loop
# starts at position 1
for position in range(1, num_leds - len(rainbow) + 1):
    # Turn all off
    for j in range(num_leds):
        set_led(j, off)
        
    # Draw rainbow starting at position
    for i in range(len(rainbow)):
        set_led(position + i, rainbow[i])
    
    np.write()
    time.sleep(0.1)

clear_leds()