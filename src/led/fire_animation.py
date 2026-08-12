from machine import Pin
from neopixel import NeoPixel
import time
import random

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
orange = (240,15,0)
yellow = (210,40,0)
white  = (85, 85, 85)

# Rainbow
fire = [
    red,
    orange,
    yellow,
    white
]

heat = [0] * num_leds

# Build up the rainbow first (LEDs 0-6)
for step in range(len(fire)):
    # Turn all off
    for j in range(num_leds):
        set_led(j, off)
    
    # Light up LEDs 0 through step with rainbow colors
    for i in range(step + 1):
        set_led(i, fire[i])
    
    np.write()
    time.sleep(0.1)

def fire_frame():
    for i in range(num_leds):
        cooldown = random.randint(0, 4)
        if cooldown > heat[i]:
            heat[i] = 0
        else:
            heat[i] -= cooldown
    for k in range(num_leds - 1, 2, -1):
        heat[k] = int((heat[k-1] + heat[k-2] + heat[k-2])/3)
    


# Now scroll the complete rainbow across the strip
# since we already have the rainbow at position 0, this loop
# starts at position 1
# for position in range(1, num_leds - len(rainbow) + 1):
#     # Turn all off
#     for j in range(num_leds):
#         set_led(j, off)
#         
#     # Draw rainbow starting at position
#     for i in range(len(rainbow)):
#         set_led(position + i, rainbow[i])
#     
#     np.write()
#     time.sleep(0.1)

clear_leds()
