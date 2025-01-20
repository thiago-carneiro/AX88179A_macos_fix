# AX88179A macOS Fix

The [ASIX AX88179](https://www.asix.com.tw/en/product/USBEthernet/Super-Speed_USB_Ethernet/AX88179) chip is widely used in USB network interface controllers (NICs). I encountered issues using these devices with both macOS and OPNsense. While searching for a solution for OPNsense, I found [this comment](https://forum.opnsense.org/index.php?msg=174987), which resolved the issue for me on FreeBSD.

However, there isn't a direct substitute for `usbconfig` on macOS, so I developed a small script (`usb_config.py`) that uses [libusb](https://pypi.org/project/libusb/) to address this problem.

This script should also work with other devices that require `set_config`.

## Installation

To automatically run this fix on macOS for your user, you can execute the `install.py` script.

### Steps:

1. Ensure you have Python and `pip` installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the repository directory.
4. Run the `install.py` script:

```sh
python install.py
```

This will create a monitoring script and a Launch Agent plist file to automatically apply the fix for all the matching devices every 5 seconds.

## Usage

The `usb_config.py` script can be used to manually configure the USB device. By default, it looks for a device named "AX88179A" and sets the configuration value to 2.

To run the script manually:

```sh
python usb_config.py [device_name] [config_value]
```

- `device_name` (optional): The name of the USB device to configure (default: "AX88179A").
- `config_value` (optional): The configuration value to set (default: 2).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.