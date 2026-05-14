from machine import Pin, SPI, PWM, I2C
import time

# some constants
FILTER_MSGS = 0x00
ALL_MSGS = 0x60

XL2515_SPI_PORT = 1
XL2515_SCLK_PIN = 10
XL2515_MOSI_PIN = 11
XL2515_MISO_PIN = 12
XL2515_CS_PIN = 9
XL2515_INT_PIN = 8

################################################################
## FRC CAN Constants
FRC_MANUFACTURER = 8  # Team Use
FRC_DEFAULT_DEVICE_TYPE = 10  # Misc - Team Device Type

## HERMES DEFAULTS:
HERMES_DEFAULT_DEVICE_NUMBER = 1
HERMES_FILTER_MODE = FILTER_MSGS   # FILTER_MSGS or ALL_MSGS
##
################################################################

class RP2350_CAN:
    def __init__(self, device_number = HERMES_DEFAULT_DEVICE_NUMBER, device_type = FRC_DEFAULT_DEVICE_TYPE, filter_mode = HERMES_FILTER_MODE, rate_kbps = "1000KBPS", tx_mode = 'normal', spi_cs = XL2515_CS_PIN, irq = XL2515_INT_PIN, spi_port = XL2515_SPI_PORT, spi_clk = XL2515_SCLK_PIN,spi_mosi = XL2515_MOSI_PIN, spi_miso = XL2515_MISO_PIN,  spi_freq=10_000_000, debug=False):
        """Initialize the RP2350 CAN interface.
        
        Args:
            device_number (int): Device number (1-16) for CAN ID construction
            device_type (int): FRC device type for CAN ID construction  
            filter_mode (int): Message filtering mode (FILTER_MSGS or ALL_MSGS)
            rate_kbps (str): CAN bus speed ("1000KBPS", "500KBPS", etc.)
            tx_mode (str): Transmission mode - 'normal' for bus operation, 'loopback' for testing
            spi_cs (int): SPI chip select pin
            irq (int): Interrupt pin for CAN messages
            spi_port (int): SPI bus port number
            spi_clk (int): SPI clock pin
            spi_mosi (int): SPI MOSI pin
            spi_miso (int): SPI MISO pin
            spi_freq (int): SPI frequency in Hz
            debug (bool): Enable debug print statements
        """
        # CAN bus timing configuration values for different bit rates
        # Used to fill CNF1, CNF2, CNF3 registers
        self.can_rate_arr = {
            "5KBPS"   : [0xBF, 0xFF, 0x87],
            "10KBPS"  : [0x5F, 0xFF, 0x87],
            "20KBPS"  : [0x18, 0XA4, 0x04],
            "50KBPS"  : [0x09, 0XA4, 0x04],
            "100KBPS" : [0x04, 0x9E, 0x03],
            "125KBPS" : [0x03, 0x9E, 0x03],
            "250KBPS" : [0x01, 0x1E, 0x03],
            "500KBPS" : [0x00, 0x9E, 0x03],
            "800KBPS" : [0x00, 0x92, 0x02],
            "1000KBPS": [0x00, 0x82, 0x02],
        }

        # validate device number is in range
        if device_number < 1 or device_number > 16:
            raise ValueError("Device number must be between 1 and 16")
        
        self.device_number = device_number
        self.device_type = device_type
        self.can_id = self._construct_can_id()
        self.filter_mode = filter_mode
        self.tx_mode = tx_mode
        self.debug = debug

        self.spi = SPI(spi_port, spi_freq, polarity = 0, phase = 0, bits = 8, sck = Pin(spi_clk), mosi = Pin(spi_mosi), miso = Pin(spi_miso))
        self.cs = Pin(spi_cs, Pin.OUT)
        self.cs(1)
        self.int = Pin(irq, Pin.IN, Pin.PULL_UP)
        # map callback method to INTERRUPT
        self.int.irq(handler = self._int_callback, trigger = Pin.IRQ_FALLING)
        self.recv_flag = False
        self._reset()
        time.sleep(0.1)
        self._config(rate_kbps)
        
    def _construct_can_id(self):
        """Construct a 29-bit CAN ID compliant with FRC spec."""
        return (self.device_type << 24) | (FRC_MANUFACTURER << 16) | (self.device_number << 2)
    
    def _debug_print(self, *args, **kwargs):
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(*args, **kwargs)
    
    def get_can_id(self):
        """Return the current CAN ID."""
        return self.can_id
    
    def set_can_id(self, new_id):
        """Set a new CAN ID and update the filter.
        
        Args:
            new_id (int): The new 29-bit CAN ID to set. Bottom 2 bits must be 0.
        """

        # validate bottom two bits are not used
        if new_id & 0x3 != 0:
            raise ValueError("Bottom two bits of extended CAN ID cannot be used")
        
        self.can_id = new_id
        self._configure_can_id_filter()

    def get_device_number(self):
        """Return the current device number."""
        return self.device_number

    def set_device_number(self, new_device_number):
        """Set a new device number, update CAN ID, and reconfigure filter.
        
        Args:
            new_device_number (int): The new device number (1-16)
        """
        
        # validate device number is in range
        if new_device_number < 1 or new_device_number > 16:
            raise ValueError("Device number must be between 1 and 16")

        self.device_number = new_device_number
        self.can_id = self._construct_can_id()
        self._configure_can_id_filter()
    
    def get_device_type(self):
        """Return the current device type."""
        return self.device_type
    
    def set_device_type(self, new_device_type):
        """Set a new device type, update CAN ID, and reconfigure filter.
        
        Args:
            new_device_type (int): The new device type
        """

        self.device_type = new_device_type
        self.can_id = self._construct_can_id()
        self._configure_can_id_filter()
        
    def _config(self, rate_kbps):
        """Configure the CAN controller with the specified baud rate and initialize buffers.
        
        Args:
            rate_kbps (str): CAN bus speed ("1000KBPS", "500KBPS", "250KBPS", etc.)
        """

        CNF3 = 0x28
        CNF2 = 0x29
        CNF1 = 0x2A
        
        TXB0SIDH = 0x31
        TXB0SIDL = 0x32
        TXB0DLC = 0x35
        
        RXB0SIDH = 0x61
        RXB0SIDL = 0x62
        RXB0CTRL = 0x60
        RXB0DLC = 0x65
        
        CANINTF = 0x2C
        CANINTE = 0x2B
        
        CANCTRL = 0x0F
        REQOP_NORMAL = 0x00
        REQOP_LOOPBACK = 0x40
        CLKOUT_ENABLED = 0x04
        CANSTAT = 0x0E
        OPMODE_NORMAL = 0x00
        OPMODE_LOOPBACK = 0x40
        
        # Select operation mode based on tx_mode parameter
        if self.tx_mode == 'loopback':
            reqop_mode = REQOP_LOOPBACK
            expected_opmode = OPMODE_LOOPBACK
        else:
            reqop_mode = REQOP_NORMAL
            expected_opmode = OPMODE_NORMAL
        
        # configure registers for CAN baud rate
        self._write_byte(CNF1, self.can_rate_arr[rate_kbps][0])
        self._write_byte(CNF2, self.can_rate_arr[rate_kbps][1])
        self._write_byte(CNF3, self.can_rate_arr[rate_kbps][2])
    
        # initialize tx buffer, this will be overwritten by tx messages
        self._write_byte(TXB0SIDH, 0xFF)
        self._write_byte(TXB0SIDL, 0xE0)
        self._write_byte(TXB0DLC, 0x40 | 0x08)

        # initialize rx buffer
        self._write_byte(RXB0SIDH, 0x00)
        self._write_byte(RXB0SIDL, 0x60)
        self._write_byte(RXB0DLC, 0x08)

        ## NOTE: This value tells controller to only accept messages
        ##        with matching can_id (FILTER_MSGS) or all messages (ALL_MSGS).
        ##        See filter_mode parameter.
        ## 
        ## NOTE: The bottom 2 bits of an extended CAN ID are not filterable,
        ##       so they are ignored in the filter/mask setup below
        self._write_byte(RXB0CTRL, self.filter_mode)

        self._configure_can_id_filter()

        # can int
        self._write_byte(CANINTF, 0x00)  # clean interrupt flag
        self._write_byte(CANINTE, 0x01)  # Receive Buffer 0 Full Interrupt Enable Bit

        self._write_byte(CANCTRL, reqop_mode | CLKOUT_ENABLED)
        dummy = self._read_byte(CANSTAT)
        if ((dummy & 0xe0) != expected_opmode):
            self._debug_print(f"Mode check: expected 0x{expected_opmode:02X}, got 0x{dummy & 0xe0:02X}")
            self._write_byte(CANCTRL, reqop_mode | CLKOUT_ENABLED)  # retry setting mode
        
    def _configure_can_id_filter(self):
        """Configure the CAN message filter registers for the current can_id."""

        RXF0SIDH = 0x00
        RXF0SIDL = 0x01
        RXM0SIDH = 0x20
        RXM0SIDL = 0x21
        
        RXF0EID8 = 0x02
        RXF0EID0 = 0x03
        RXM0EID8 = 0x22
        RXM0EID0 = 0x23

        # Extended CAN ID filter configuration (29-bit ID split across registers)
        # Bits 28-21 (upper 8 bits of standard ID portion)
        self._write_byte(RXF0SIDH, (self.can_id >> 21) & 0xFF)

        # Bits 20-18 (lower 3 bits of standard ID) + extended ID flag
        self._write_byte(RXF0SIDL, ((self.can_id >> 18) & 0x07) << 5 | 0x08)

        # Bits 17-10 (upper 8 bits of extended portion)
        self._write_byte(RXF0EID8, (self.can_id >> 10) & 0xFF)

        # Bits 9-2 (middle 8 bits of extended portion) - Note: bits 1-0 are lost
        self._write_byte(RXF0EID0, (self.can_id >> 2) & 0xFF)

        # Mask configuration - all bits must match exactly
        self._write_byte(RXM0SIDH, 0xFF)    # Match all bits 28-21
        self._write_byte(RXM0SIDL, 0xE8)    # Match bits 20-18 + extended flag
        self._write_byte(RXM0EID8, 0xFF)    # Match all bits 17-10
        self._write_byte(RXM0EID0, 0xFC)    # Match bits 9-2 (upper 6 bits), ignore bits 1-0 since they are lost anyway
        
    def send(self, can_id, data):
        """Send a CAN message with the specified ID and data.
        
        Args:
            can_id (int): 29-bit extended CAN ID to send to
            data (list): List of bytes to send (max 8 bytes)
        """

        TXB0CTRL = 0x30
        TXB0SIDH = 0x31
        TXB0SIDL = 0x32
        TXB0EID8 = 0x33
        TXB0EID0 = 0x34
        TXB0DLC  = 0x35
        TXB0D0   = 0x36
        dly = 0

        while ((self._read_byte(TXB0CTRL) & 0x08) and (dly < 50)):
            dly += 1
            time.sleep_ms(1)
        
        # For extended 29-bit CAN ID
        # Bits 28-21 (standard ID high byte)
        self._write_byte(TXB0SIDH, (can_id >> 21) & 0xFF)

        # Bits 20-18 (standard ID low bits) + extended flag (0x08)
        self._write_byte(TXB0SIDL, ((can_id >> 18) & 0x07) << 5 | 0x08)

        # Bits 17-10 (extended ID high byte)
        self._write_byte(TXB0EID8, (can_id >> 10) & 0xFF)

        # Bits 9-2 (extended ID low byte)
        self._write_byte(TXB0EID0, (can_id >> 2) & 0xFF)

        self._write_byte(TXB0DLC, len(data))
        for i in range(len(data)):
            self._write_byte(TXB0D0 + i, data[i])
        self._write_byte(TXB0CTRL, 0x08)
    
    def recv(self):
        """Receive a CAN message if available.
        
        Returns:
            bytearray or None: Received data bytes, or None if no message available
        """
        RXB0SIDH = 0x61
        RXB0SIDL = 0x62
        RXB0EID8 = 0x63
        RXB0EID0 = 0x64
        CANINTF = 0x2C
        CANINTE = 0x2B
        RXB0DLC = 0x65
        RXB0D0 = 0x66
        
        if self.recv_flag == False:
            return None
        self.recv_flag = False
        
        sid_h = self._read_byte(RXB0SIDH)
        sid_l = self._read_byte(RXB0SIDL)
        eid_h = self._read_byte(RXB0EID8)
        eid_l = self._read_byte(RXB0EID0)

        # Check if it's an extended ID (bit 3 of SIDL)
        if sid_l & 0x08:
            # Reconstruct 29-bit extended ID
            can_id = (sid_h << 21) | ((sid_l >> 5) << 18) | (eid_h << 10) | (eid_l << 2)
            self._debug_print("Extended ID:", hex(can_id))
        else:
            # Standard 11-bit ID
            can_id = (sid_h << 3) | (sid_l >> 5)
            self._debug_print("Standard ID:", hex(can_id))
        
        while True:
            if (self._read_byte(CANINTF) & 0x01):
                len = self._read_byte(RXB0DLC)
                buf = bytearray(len)
                for i in range(len):
                   buf[i] = self._read_byte(RXB0D0 + i)
                self._write_byte(CANINTF, 0)
                self._write_byte(CANINTE, 0x01)  # enable
                self._write_byte(RXB0SIDH, 0x00) # clean
                self._write_byte(RXB0SIDL, 0x60)
                return buf
            
    def _int_callback(self, pin):
        """Interrupt callback for CAN message reception.
        
        Args:
            pin: The pin that triggered the interrupt
        """
        self.recv_flag = True

    def _reset(self):
        """Reset the CAN controller."""

        CAN_RESET = 0xC0
        self.cs(0)
        self.spi.write(bytearray([CAN_RESET]))
        self.cs(1)

    def _read_byte(self, reg):
        """Read a byte from the specified CAN controller register.
        
        Args:
            reg (int): Register address to read from
            
        Returns:
            int: The byte value read from the register
        """
        CAN_READ = 0x03
        self.cs(0)
        self.spi.write(bytearray([CAN_READ, reg]))
        data = self.spi.read(1)
        self.cs(1)
        
        return data[0]
    
    def get_status(self):
        """Get the current CAN controller status.
        
        Returns:
            int: Status byte from CANSTAT register containing operation mode and other flags
        """
        CANSTAT = 0x0E
        return self._read_byte(CANSTAT)
    
    def get_error_counts(self):
        """Get the current transmit and receive error counts.
        
        Returns:
            tuple: (tx_errors, rx_errors) - Transmit and receive error counter values
        """
        TEC = 0x1C  # Transmit Error Counter register
        REC = 0x1D  # Receive Error Counter register
        tx_errors = self._read_byte(TEC)
        rx_errors = self._read_byte(REC)
        return tx_errors, rx_errors
    
    def _write_byte(self, reg, data):
        """Write a byte to the specified CAN controller register.
        
        Args:
            reg (int): Register address to write to
            data (int): Byte value to write
        """
        CAN_WRITE = 0x02
        self.cs(0)
        self.spi.write(bytearray([CAN_WRITE, reg, data]))
        self.cs(1)
