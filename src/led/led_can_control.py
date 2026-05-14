from machine import Pin
from neopixel import NeoPixel
import time
from rp2350_can import RP2350_CAN, ALL_MSGS

# --- LED SETUP ---
num_leds = 10
np = NeoPixel(Pin(2), num_leds)
off = (0,0,0)

def set_all_leds(color):
    r, g, b = color
    # Your GRB fix for WS2811
    for i in range(num_leds):
        np[i] = (g, r, b) 
    np.write()
    
# --- CAN SETUP ---
# device_number 1, mode normal to listen to the robot bus
#can = RP2350_CAN(device_number=1, filter_mode=FILTER_MSGS, tx_mode='normal')

# testing mode by sending a message to itself
can = RP2350_CAN(device_number=1, filter_mode=ALL_MSGS, tx_mode='loopback')

# --- COLOR DICTIONARY ---
# We map a Byte (Key) to an RGB Value
# Let's pretend: 0x01 is "searching", 0x02 is "found", and 0x03 is "error"
commands = {
    0x00: (0, 0, 0),    # All LED's Off
    0x01: (0, 0, 100),   # Dim Blue (Searching)
    0x02: (0, 100, 0),   # Dim Green (Found!)
    0x03: (100, 0, 0)    # Dim Red (Error/Stop)
}

# Ensure we start with LEDs off
set_all_leds(off)

# 2. TEST MODE: Send a sequence to ourselves
# This sends Blue (0x01), Green (0x02), Red (0x03), then Off (0x00)
test_sequence = [0x01, 0x02, 0x03, 0x00]
print(f"Loopback Test: Sending sequence {test_sequence} to ID {hex(can.get_can_id())}")

can.send(can.get_can_id(), test_sequence)

print ("Listening for Messages...")

while True:
    data = can.recv() 
    
    if data:
        print(f"Received sequence: {[hex(b) for b in data]}")
        
        # Cycle through each byte in the received message
        for byte in data:
            if byte in commands:
                color_to_show = commands[byte]
                set_all_leds(color_to_show)
                
                # How long each color stays on (2 seconds)
                time.sleep(2) 

        print("Sequence complete.")

    time.sleep(0.01)