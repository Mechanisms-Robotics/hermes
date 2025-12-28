# Usage: Programming with hermes

## Writing Code for New Devices

### Basic Setup
When creating a new device that uses CAN communication, start by importing and initializing the RP2350_CAN class:

```python
from src.rp2350_can import RP2350_CAN

# Initialize with default settings (device_number=1, device_type=11)
can = RP2350_CAN()

# Or customize for your specific device
can = RP2350_CAN(device_number=5, device_type=11)
```

### Code Structure
Organize your device code following this pattern:

1. **Import required modules**
2. **Initialize CAN interface**
3. **Configure device-specific settings**
4. **Main application loop**

```python
# 1. Imports
from src.rp2350_can import RP2350_CAN
from machine import Pin
import time

# 2. CAN setup
can = RP2350_CAN(device_number=1)

# 3. Device setup (sensors, outputs, etc.)
sensor_input = Pin(12, Pin.IN)

# 4. Main loop
while True:
    # Read sensors and send data
    sensor_data = read_sensor()
    can.send(0x100, sensor_data)
    
    # Check for commands
    command = can.recv()
    if command:
        process_command(command)
    
    time.sleep(0.1)
```

### Device Number Assignment
Make sure each ```hermes``` device has a unique device number (1-16):

```python
# Good: Unique device numbers
sensor1 = RP2350_CAN(device_number=2)
sensor2 = RP2350_CAN(device_number=3)
led_strip = RP2350_CAN(device_number=9)

# Bad: Duplicate device numbers (will cause CAN conflicts)
sensor1 = RP2350_CAN(device_number=1)
sensor2 = RP2350_CAN(device_number=1)  # Conflict!
```

### Source Code File Management
MicroPython automatically runs `main.py` when the board is powered on, so place your application code there.

## RP2350_CAN Class Reference

The `RP2350_CAN` class is a key component for hermes projects, providing a simple interface to send and receive CAN messages on the RP2350-CAN board. It handles the low-level SPI communication with the XL2515 CAN controller, allowing students to focus on their application logic.

### Constructor
```python
RP2350_CAN(device_number=HERMES_DEFAULT_DEVICE_NUMBER, device_type=FRC_DEVICE_TYPE, filter_mode=HERMES_FILTER_MODE, rate_kbps="1000KBPS", tx_mode='normal', spi_cs=XL2515_CS_PIN, irq=XL2515_INT_PIN, spi_port=XL2515_SPI_PORT, spi_clk=XL2515_SCLK_PIN, spi_mosi=XL2515_MOSI_PIN, spi_miso=XL2515_MISO_PIN, spi_freq=10_000_000, debug=False)
```

- `device_number`: The device number (1-16) used to construct the CAN ID. Default is 1.
- `device_type`: The FRC device type used to construct the CAN ID. Default is 11 (IO Breakout).
- `filter_mode`: Message filtering mode. Use FILTER_MSGS (0x00) to receive only messages matching can_id, or ALL_MSGS (0x60) to receive all messages. Default is FILTER_MSGS as set by HERMES_FILTER_MODE.
- `rate_kbps`: CAN bus speed (e.g., "125KBPS", "500KBPS"). Default is "1000KBPS" per the FRC standard.
- `tx_mode`: Transmission mode - 'normal' for bus operation (default), 'loopback' for testing without other devices.
- `spi_cs`: Chip select pin for SPI. Default is 9.
- `irq`: Interrupt pin for CAN messages. Default is 8.
- `spi_port`: SPI bus number. Default is 1.
- `spi_clk`, `spi_mosi`, `spi_miso`: SPI pins. Defaults are 10, 11, 12.
- `spi_freq`: SPI frequency. Default is 10MHz.
- `debug`: Enable debug print statements. Default is False.

### CAN ID Configuration
The RP2350_CAN class automatically constructs a 29-bit CAN ID compliant with FRC specifications using the manufacturer_number constant along with the device_number and device_type parameters. The CAN ID is calculated as:

CAN_ID = (Device_Type << 24) | (Manufacturer << 16) | (Device_Number << 2)

Where:
- Device_Type = Configurable (default 11 for IO Breakout)
- Manufacturer = 8 (Team Use)
- Device_Number = 1-16 (specified in constructor, will be shifted left 2 bits due to hardware limitations)

For example, device_number=1 results in CAN_ID = 0x0B080004.

The class uses this ID for message filtering, only receiving messages addressed to that ID.

```python
can = RP2350_CAN(device_number=1)  # CAN ID = 0x0B080001
```

See the [FRC CAN Device Specifications](https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html) for full details on CAN ID structure and manufacturer assignments.

### Methods

- `send(can_id, data)`: Send a CAN message with the given ID and data (list of bytes).
- `recv()`: Receive a CAN message if available. Returns the data as a bytearray or None.
- `get_can_id()`: Return the current CAN ID.
- `set_can_id(new_id)`: Set a new CAN ID and update the filter.
- `get_device_number()`: Return the current device number.
- `set_device_number(new_device_number)`: Set a new device number, update CAN ID, and reconfigure filter.
- `get_device_type()`: Return the current device type.
- `set_device_type(new_device_type)`: Set a new device type, update CAN ID, and reconfigure filter.
- `get_status()`: Get the current CAN controller status byte.
- `get_error_counts()`: Get the current transmit and receive error counter values.

### Example Usage
```python
from src.rp2350_can import RP2350_CAN

# Initialize the CAN interface with device number 1
can = RP2350_CAN(device_number=1)

# Send a test message
can.send(0x0B080004, [0x12, 0x34, 0x56, 0x78])

while True:
    # Check for received CAN messages
    data = can.recv()
    if data:
        print("Received:", data)
    # Sleep for 1 second before checking again
    time.sleep(1)
```

For the full source code, see the `src/rp2350_can.py` file in the project repository.

## Best Practices

### Safety Considerations
- **Unique Device Numbers**: Never use duplicate device numbers on the same CAN bus
- **Error Handling**: Always check for CAN communication errors
- **Power Sequencing**: Ensure CAN devices are powered on before initializing communication
- **Bus Termination**: Use proper CAN bus termination (120Ω resistors) for reliable communication

```python
# Safe CAN usage with error handling
try:
    can = RP2350_CAN(device_number=1)
    can.send(0x100, [0x01, 0x02])
except Exception as e:
    print("CAN Error:", e)
    # Implement fallback behavior
```

### Testing Your Code
Test CAN communication in stages:

1. **Basic Connectivity**: Verify the CAN interface initializes without errors
2. **Loopback Test**: Send messages to yourself to test basic functionality
3. **Network Test**: Test communication between multiple devices
4. **Stress Test**: Test under high message loads and error conditions

```python
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
else:
    print("❌ Loopback test failed!")
    print(f"Expected: {test_data}")
    print(f"Received: {list(received) if received else None}")
```

**Note:** Use `tx_mode='loopback'` for testing on a single board. For production use with real CAN devices, use the default `tx_mode='normal'`.

## Next Steps
- [Troubleshooting](troubleshooting.md)
