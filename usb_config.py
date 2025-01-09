import subprocess
import re
import sys

# Be sure to "pip install pyusb" first!
try:
    import usb.core
    import usb.util
except ImportError:
    print(
        "The 'pyusb' library is required to run this script. "
        "Please install it by running:\n\n\tpip install pyusb\n"
    )
    sys.exit(1)


def find_device(device_name):
    """
    Find the idVendor and idProduct of a USB device by name using ioreg.
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
            return None, None

        # Parse the output to find the device
        lines = result.stdout.splitlines()
        vendor_id, product_id = None, None
        for i, line in enumerate(lines):
            if device_name in line:
                for subline in lines[i : i + 30]:  # Look in the next 30 lines for IDs
                    if (not vendor_id) and ("idVendor" in subline):
                        vendor_id = int(re.search(r"= (\d+)", subline).group(1))
                    if (not product_id) and ("idProduct" in subline):
                        product_id = int(re.search(r"= (\d+)", subline).group(1))
                break

        if vendor_id and product_id:
            return vendor_id, product_id
        else:
            print(f"Device '{device_name}' not found.")
            return None, None
    except Exception as e:
        print(f"Error finding device: {e}")
        return None, None


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
        device.set_configuration()
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
        print("Usage: python3 script.py <device_name>")
        device_name = default_device_name
    else:
        device_name = sys.argv[1]

    # Find the device
    vendor_id, product_id = find_device(device_name)
    if not vendor_id or not product_id:
        sys.exit(1)

    # Configure the device
    if not configure_device(vendor_id, product_id):
        sys.exit(1)


if __name__ == "__main__":
    main()
