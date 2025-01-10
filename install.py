import os
import subprocess
import sys
import argparse

# Default values for the arguments
DEFAULT_REPO_DIRECTORY = "src/AX88179A_macos_fix"
DEFAULT_DEVICE_NAME = "AX88179A"


def create_monitor_script(venv_path, device_name, config_value):
    """Create the usb_config_monitor.sh script."""
    current_directory = os.getcwd()
    monitoring_script_path = (
        f"{current_directory}/usb_config_monitor_{device_name}_{config_value}.sh"
    )
    if venv_path:
        venv_activation = f"\n    source {venv_path}/bin/activate"
    else:
        venv_activation = ""
    script_content = f"""#!/bin/bash

DEVICE_NAME="{device_name}"
CONFIG_VALUE="{config_value}"
DEVICE_PRESENT=$(system_profiler SPUSBDataType | grep -i $DEVICE_NAME)
if [ ! -z "$DEVICE_PRESENT" ]; then{venv_activation}
    python {current_directory}/usb_config.py $DEVICE_NAME $CONFIG_VALUE
fi
"""

    with open(monitoring_script_path, "w") as script_file:
        script_file.write(script_content)
        print(f"Created script: {monitoring_script_path}")

    # Make the script executable
    os.chmod(monitoring_script_path, os.stat(monitoring_script_path).st_mode | 0o100)
    print(f"Script {monitoring_script_path} is now executable.")

    return monitoring_script_path


def create_plist_file(script_path, device_name, config_value):
    """Create the LaunchAgents plist file."""
    home_path = os.environ.get("HOME")
    username = home_path.split(os.sep)[-1]
    plist_filename = (
        f"com.{username}.usbconfigmonitor.{device_name}.{config_value}.plist"
    )
    plist_path = f"{home_path}/Library/LaunchAgents/{plist_filename}"

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>{plist_filename}</string>
        <key>ProgramArguments</key>
        <array>
            <string>{script_path}</string>
        </array>
        <key>StartInterval</key>
        <integer>5</integer> <!-- The interval between checks in seconds -->
        <key>RunAtLoad</key>
        <true/>
        <key>StandardOutPath</key>
        <string>/tmp/usb_config_monitor.log</string>
        <key>StandardErrorPath</key>
        <string>/tmp/usb_config_monitor_error.log</string>
    </dict>
</plist>
"""

    with open(plist_path, "w") as plist_file:
        plist_file.write(plist_content)
        print(f"Created plist: {plist_path}")

    return plist_path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate monitor USB script and Launch Agent plist."
    )
    parser.add_argument(
        "device_name",
        nargs="?",
        default="AX88179A",
        help="Name of the USB device to configure (default: AX88179A)",
    )
    parser.add_argument(
        "config_value",
        nargs="?",
        default="2",
        help="Configuration value to set (default: 2)",
    )
    parser.add_argument(
        "venv_path",
        nargs="?",
        default="",
        help="Path to venv (default: try to autodetect)",
    )
    return parser.parse_args()


def get_venv_path():
    """Detect the virtual environment path, handling both Conda and Python's venv."""
    # First check if we're in a Conda environment
    conda_prefix = os.getenv("CONDA_PREFIX")
    if conda_prefix:
        print(f"Detected Conda environment at {conda_prefix}")
        return conda_prefix  # Return Conda venv path

    # If not Conda, check for Python venv
    # Python's venv usually has a pyvenv.cfg file
    venv_path = os.getenv("VIRTUAL_ENV")
    if venv_path and os.path.exists(f"{venv_path}/pyvenv.cfg"):
        print(f"Detected Python venv at {venv_path}")
        return venv_path  # Return Python venv path

    print("No virtual environment detected.")
    user_input = (
        input("Do you want to continue without a venv? (yes/no): ").strip().lower()
    )
    if user_input != "yes":
        print("Exiting...")
        exit(1)

    return None


def install_libusb():
    """
    Install or upgrade the libusb package.
    """
    print("Installing/upgrading libusb package...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "libusb"]
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to install/upgrade libusb: {e}")
        sys.exit(1)


def main():
    args = parse_arguments()

    if args.venv_path:
        venv_path = args.venv_path
    else:
        # Try to detect the virtual environment path (Conda or venv)
        venv_path = get_venv_path()

    # Upgrade libusb package
    install_libusb()

    # Create the monitor script
    try:
        script_path = create_monitor_script(
            venv_path, args.device_name, args.config_value
        )
    except Exception as e:
        print(f"Failed to create monitor script: {e}")
        sys.exit(1)

    # Create the plist file
    try:
        create_plist_file(script_path, args.device_name, args.config_value)
    except Exception as e:
        print(f"Failed to create plist file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
