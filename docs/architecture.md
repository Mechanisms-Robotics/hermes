# Architecture: How hermes Works

## Overview
hermes uses RPI-CAN boards to connect IO devices (sensors, outputs) to the robot CAN bus. This allows distributed control and easy expansion.

The hermes system is designed to offload simple input/output (IO) tasks from the main robot controller by using distributed microcontroller boards (such as the Waveshare RP2350-CAN) that communicate over the CAN bus. This enables modular, scalable, and robust robot architectures.

## CAN Bus Basics

**What is CAN?**
The Controller Area Network (CAN) is a robust, real-time communication protocol originally developed for automotive applications. It allows multiple devices (nodes) to communicate over a single pair of wires, using message IDs for addressing and prioritization.

**Why use CAN for FRC?**
- CAN is already used by most FRC motor controllers and sensors, so it integrates seamlessly with existing robot systems.
- It supports multiple devices on the same bus, reducing wiring complexity.
- CAN is robust against electrical noise and supports real-time, prioritized messaging.

## Board Architecture

### Hardware Overview
- **Microcontroller:** Waveshare RP2350-CAN board
- **CAN Transceiver:** XL2515 CAN controller, fully supports CAN V2.0B technical specifications, with a communication speed of up to 1 Mbps
- **IO Pins:** Exposed for connecting sensors, actuators, and other devices
- **Power:** Can be powered via USB-C or external supply (with common ground)

#### Pinout and Connections

Below are the key pin assignments for connecting the RP2350 to the XL2515 CAN controller chip:

**XL2515_SPI_PORT = 1**
- The RP2350 has multiple SPI buses (SPI0, SPI1). This says we're using SPI bus #1.

**XL2515_SCLK_PIN = 10**
- **SCLK** = Serial Clock. This is the timing signal that synchronizes data transfer between the RP2350 and XL2515.

**XL2515_MOSI_PIN = 11**
- **MOSI** = Master Out, Slave In. This sends data FROM the RP2350 TO the XL2515.

**XL2515_MISO_PIN = 12**
- **MISO** = Master In, Slave Out. This receives data FROM the XL2515 TO the RP2350.

**XL2515_CS_PIN = 9**
- **CS** = Chip Select. The RP2350 sets this pin LOW when it wants to talk to the XL2515, and HIGH when done. This tells the XL2515 "pay attention to me now."

**XL2515_INT_PIN = 8**
- **INT** = Interrupt. The XL2515 pulls this pin LOW when it has received a CAN message and wants to notify the RP2350.

Together, these 6 pins allow full two-way communication between the RP2350 and the CAN controller chip.

### Firmware/Software Layers
1. **MicroPython Runtime:** Runs on the RP2350-CAN board, providing a simple environment for writing device logic. There is also a C-sdk available, but python was chosen for hermes to simplify the process and remove the dependency on compilers.
2. **hermes Application Code:** User-written Python scripts handle IO, process CAN messages, and implement device-specific logic. Scripts are to be maintained within the ```hermes``` github repo for proper version control and governance. Each individual script for a specific module can be installed onto the required module as needed.
3. **CAN Communication Library:** Handles sending/receiving CAN messages, message parsing, and error handling. This is largely taken from the Waveshare demo resources, with just a few modifications to make configuration easier.

### Message Flow
1. The main robot controller (e.g., RoboRIO) sends a CAN message to the hermes board with a specific message ID and data payload.
2. The hermes board receives the message, parses the ID and data, and performs the requested IO action (e.g., set an output, read a sensor).
3. The hermes board can also send CAN messages back to the main controller, reporting sensor values or status.

## Design Philosophy

**Modularity:**
Each hermes board is independent and can be programmed for a specific function (e.g., LED control, sensor input). Boards can be added or removed from the CAN bus as needed, making the system flexible and scalable.

**Ease of Use for Students:**
hermes is designed so students can write simple Python scripts to add new sensors or outputs, without needing to modify the main robot code. The use of MicroPython and Thonny IDE makes programming accessible and beginner-friendly.

## See Also
- [Setup](setup.md)
- [How to Use](usage.md)
