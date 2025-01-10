import sys
import usb.core
import usb.util
import argparse  # Add argparse import


def find_devices(device_name):
    """
    Find the idVendor and idProduct of USB devices by name using pyusb.
    """
    try:
        # Find all USB devices
        devices = usb.core.find(find_all=True)
        matching_devices = []

        # Get the device's system unique IDs
        for device in devices:
            # Get the device's product strings
            try:
                product = usb.util.get_string(device, device.iProduct)
            except usb.core.USBError:
                continue

            if device_name in product:
                matching_devices.append((device.bus, device.address))

        return matching_devices
    except Exception as e:
        print(f"Error finding devices: {e}")
        return []


def configure_device(device_id, config_value=2):
    """
    Configure the USB device using pyusb.
    """
    unique_id = f"{device_id[0]}-{device_id[1]}"
    try:
        # Find the device
        device = usb.core.find(bus=device_id[0], address=device_id[1])
        if device is None:
            print(f"Device not found at {unique_id}")
            return False

        # Get the current configuration value
        current_config = device.get_active_configuration().bConfigurationValue
        if current_config == config_value:
            print(
                f"Device {unique_id} already configured with config value={config_value}."
            )
            return True

        print(f"Current configuration value for device {unique_id}: {current_config}")

        # Set the new configuration value
        device.set_configuration(config_value)

        print(
            f"Successfully configured device {unique_id} with config value={config_value}."
        )
        return True

    except usb.core.USBError as e:
        print(f"Failed to configure device: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Configure USB devices.")
    parser.add_argument(
        "device_name",
        nargs="?",
        default="AX88179A",
        help="Name of the USB device to configure (default: AX88179A)",
    )
    parser.add_argument(
        "config_value",
        nargs="?",
        type=int,
        default=2,
        help="Configuration value to set (default: 2)",
    )
    args = parser.parse_args()

    device_name = args.device_name
    config_value = args.config_value

    # Find the devices
    device_ids = find_devices(device_name)
    if not device_ids:
        print(f"No devices found with name {device_name}.")
        sys.exit(1)

    print(f"Found {len(device_ids)} devices with name '{device_name}':")

    # Configure each device
    for device_id in device_ids:
        if not configure_device(device_id, config_value):
            sys.exit(1)


if __name__ == "__main__":
    main()
