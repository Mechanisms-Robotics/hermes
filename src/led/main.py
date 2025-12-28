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
        set_led(i, 0, 0, 0)
    np.write()
    
def set_led(index, r, g, b):
    np[index] = (g, r, b)

status_light_on()

clear_leds()