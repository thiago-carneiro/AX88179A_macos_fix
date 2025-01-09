import subprocess
import re
import sys
import usb.core
import usb.util


def find_devices(device_name):
    """
    Find the idVendor and idProduct of USB devices by name using ioreg.
    """
    try:
        # Run ioreg to get USB device info
        result = subprocess.run(
            ["ioreg", "-p", "IOUSB", "-w0", "-l"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            print(f"Error running ioreg: {result.stderr}")
            return []

        # Parse the output to find the devices
        lines = result.stdout.splitlines()
        devices = []
        for i, line in enumerate(lines):
            if device_name in line:
                vendor_id, product_id = None, None
                for subline in lines[i : i + 30]:  # Look in the next 30 lines for IDs
                    if (not vendor_id) and ("idVendor" in subline):
                        vendor_id = int(re.search(r"= (\d+)", subline).group(1))
                    if (not product_id) and ("idProduct" in subline):
                        product_id = int(re.search(r"= (\d+)", subline).group(1))
                if vendor_id and product_id:
                    devices.append((vendor_id, product_id))

        if devices:
            return devices
        else:
            print(f"Device '{device_name}' not found.")
            return []
    except Exception as e:
        print(f"Error finding devices: {e}")
        return []


def configure_device(vendor_id, product_id):
    """
    Configure the USB device using pyusb.
    """
    try:
        # Find the USB device
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if not device:
            print(
                f"Device with idVendor={vendor_id}, idProduct={product_id} not found."
            )
            return False

        # Set the configuration
        device.set_configuration(2)
        print(
            f"Successfully configured device with idVendor={vendor_id}, idProduct={product_id}."
        )
        return True

    except usb.core.USBError as e:
        print(f"Failed to configure device: {e}")
        return False


def main():
    # Set default device name
    default_device_name = "AX88179A"

    if len(sys.argv) != 2:
        print(f"Using default device name: '{default_device_name}'")
        print(
            "If you want to configure another device, specify its name as an argument:"
        )
        print("Usage: python3 usb_config.py <device_name>")
        device_name = default_device_name
    else:
        device_name = sys.argv[1]

    # Find the devices
    devices = find_devices(device_name)
    if not devices:
        sys.exit(1)

    print(f"Found {len(devices)} devices with name '{device_name}':")

    # Configure each device
    for vendor_id, product_id in devices:
        if not configure_device(vendor_id, product_id):
            sys.exit(1)


if __name__ == "__main__":
    main()
