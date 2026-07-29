from machine import Pin
from neopixel import NeoPixel
import time

num_leds = 80
np = NeoPixel(Pin(2), num_leds)

def clear_leds():
    for i in range(num_leds):
        set_led(i, off)
    np.write()
    
def set_led(index, color):
    r, g, b = color # unpack the array
    np[index] = (g, r, b) # WS2811 LED is weird and requires GRB

off = (0,0,0)

colors = [
    (20, 0, 0),
    (20, 0, 0),
    (0, 20, 0),
    (0, 20, 0),
    (0, 0, 20),
    (0, 0, 20)
    ]

for i in range(len(colors)):
    set_led(i, colors[i])
    
np.write()

# wait 3 seconds, and then clear the leds
time.sleep(3)
clear_leds()
