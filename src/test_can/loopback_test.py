# Loopback test - use loopback mode to test without other CAN devices
from rp2350_can import RP2350_CAN, ALL_MSGS
import time

can = RP2350_CAN(device_number=1, filter_mode=ALL_MSGS, tx_mode='loopback')
test_data = [0xAA, 0xBB, 0xCC]

print("Sending test data...")
can.send(can.get_can_id(), test_data)  # Send to self

time.sleep(0.1)  # Allow time for message processing

received = can.recv()
if received and list(received) == test_data:
    print("✅ Loopback test passed!")
    print(f"Received: {[hex(b) for b in received]}")
else:
    print("❌ Loopback test failed!")
    print(f"Expected: {test_data}")
    print(f"Received: {list(received) if received else None}")

