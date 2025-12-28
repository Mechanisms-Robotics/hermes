# Troubleshooting

## Common Issues

### Board Not Detected
**Symptoms:** MicroPython can't connect to the RP2350 board, or flashing fails.

**Solutions:**
1. **Check USB Connection:**
   - Ensure the USB cable is properly connected
   - Try a different USB port or cable
   - Verify the board has power (use multimeter)

2. **Driver Issues:**
   - Install appropriate USB-to-serial drivers for your board
   - On Windows: Check Device Manager for COM port
   - On Linux/Mac: Check `/dev/tty*` devices

3. **Board Selection:**
   - In Thonny or your IDE, select the correct board type (Raspberry Pi Pico)
   - Ensure you're using MicroPython firmware for Waveshare RP2350-CAN board (THIS IS CRITICAL)

### CAN Bus Errors
**Symptoms:** CAN initialization fails, or no messages are received/sent.

**Solutions:**
1. **Hardware Connections:**
   - Verify SPI connections: MOSI, MISO, SCK, CS pins
   - Check CAN transceiver power and connections
   - Ensure proper CAN bus termination (120Ω resistors at both ends)

2. **SPI Configuration:**
   ```python
   # Verify SPI pins match your hardware
   spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
   ```

3. **CAN Transceiver Issues:**
   - Check with a self loopback test
   - Test with a known working CAN device

### Device Not Responding
**Symptoms:** CAN messages are sent but no response from target device.

**Solutions:**
1. **Device Number Conflicts:**
   - Ensure no two devices have the same device number
   - Check device numbers with `can.get_device_number()`

2. **CAN ID Mismatch:**
   - Verify the target device is configured for the correct device type
   - Check that CAN IDs are constructed correctly (FRC format)

3. **Filter Configuration:**
   - Ensure the receiving device has proper acceptance filters
   - Check that filters match the expected CAN ID range

## Debugging Tips

### Checking Connections
```python
# Test SPI connection to CAN controller
from machine import SPI, Pin
import time

cs = Pin(5, Pin.OUT, value=1)  # Chip select
spi = SPI(0, baudrate=1000000, sck=Pin(2), mosi=Pin(3), miso=Pin(4))

def test_spi():
    cs.value(0)
    # Send reset command to MCP2515/XL2515
    spi.write(b'\xC0')  # RESET command
    time.sleep(0.01)
    cs.value(1)
    print("SPI test command sent")

test_spi()
```

### Using Diagnostic Tools
```python
# Use diagnostic methods to check CAN controller health
can = RP2350_CAN(device_number=1)

# Check CAN controller status
status = can.get_status()
print(f"CAN Status: 0x{status:02X}")

# Read error counters
tx_errors, rx_errors = can.get_error_counts()
print(f"TX Errors: {tx_errors}, RX Errors: {rx_errors}")
```

### Reading CAN Messages
```python
from rp2350_can import RP2350_CAN, ALL_MSGS
import time

# Monitor all CAN traffic (use ALL_MSGS to receive all messages on the bus)
can = RP2350_CAN(device_number=1, filter_mode=ALL_MSGS)

print("Monitoring CAN bus...")
while True:
    msg = can.recv()
    if msg:
        can_id = can.get_last_can_id()
        print(f"ID: 0x{can_id:08X}, Data: {[hex(b) for b in msg]}")
    time.sleep(0.1)
```

### Loopback Testing
```python
from rp2350_can import RP2350_CAN, ALL_MSGS
import time

# Test CAN interface by sending to yourself
# Use ALL_MSGS filter to receive all messages including your own
can = RP2350_CAN(device_number=1, filter_mode=ALL_MSGS)

# Send test message to your own CAN ID
test_data = [0xAA, 0xBB, 0xCC, 0xDD]
can.send(can.get_can_id(), test_data)

time.sleep(0.1)  # Allow time for processing

# Check if message was received
received = can.recv()
if received and list(received) == test_data:
    print("✅ Loopback test passed!")
else:
    print("❌ Loopback test failed!")
    print(f"Expected: {test_data}")
    print(f"Received: {list(received) if received else None}")
```

## Performance Issues

### High CPU Usage
**Problem:** The RP2350 seems slow or unresponsive.

**Solutions:**
- Reduce CAN message frequency
- Use interrupt-driven receiving instead of polling
- Optimize your main loop timing
- Check for infinite loops or blocking operations

### Message Loss
**Problem:** Some CAN messages are not being received.

**Solutions:**
- Increase buffer sizes if possible
- Process received messages faster
- Check for buffer overflow conditions
- Verify CAN bus baud rate settings match

### Timing Issues
**Problem:** Sensor readings or control loops are inconsistent.

**Solutions:**
```python
# Use consistent timing
import time

last_time = time.ticks_ms()
interval = 10  # 10ms = 100Hz

while True:
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_time) >= interval:
        # Do periodic tasks here
        last_time = current_time
    # Do other tasks
```

---

See [setup.md](setup.md) and [usage.md](usage.md) for more help.
