from rp2350_can import RP2350_CAN, ALL_MSGS
import time

can = RP2350_CAN(device_number=1, filter_mode=ALL_MSGS, debug=True)

print(f"CAN ID: 0x{can.get_can_id():08X}")

# Check initial status
status = can.get_status()
tx_err, rx_err = can.get_error_counts()
print(f"Initial - Status: 0x{status:02X}, TX Err: {tx_err}, RX Err: {rx_err}")

# Don't send yet - just listen
print("Listening for 5 seconds...")
for i in range(5):
    data = can.recv()
    if data:
        print(f"Received: {data}")
    time.sleep(1)

# Check if errors increased just from listening
tx_err, rx_err = can.get_error_counts()
print(f"After listening - TX Err: {tx_err}, RX Err: {rx_err}")
