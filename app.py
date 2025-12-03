import platform
import subprocess
import sys
from pathlib import Path


# Figure out project layout based on this file location
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "src" / "website" / "backend"
FRONTEND_DIR = ROOT_DIR / "src" / "website" / "frontend"

# Use the same Python that is running this script
PYTHON = sys.executable


def start_mosquitto():
    """Start or remind about Mosquitto, depending on OS."""
    system = platform.system()

    if system == "Darwin":
        # macOS, try to start via Homebrew
        try:
            print("Checking Mosquitto service with Homebrew...")
            subprocess.run(
                ["brew", "services", "start", "mosquitto"],
                check=False,
            )
        except FileNotFoundError:
            print("[!] Homebrew not found. Please start Mosquitto manually:")
            print("    brew install mosquitto")
            print("    brew services start mosquitto")
    elif system == "Windows":
        print("[i] On Windows, make sure your Mosquitto broker is running on port 1883.")
        print("    For example, start it from Command Prompt with:")
        print("    mosquitto -v")
    else:
        print("[i] Non macOS or Windows detected. Start your MQTT broker on port 1883 manually.")


def open_terminal_mac(title: str, command: str):
    """Open a new macOS Terminal window and run a command."""

    # Escape any double quotes inside the command
    command_escaped = command.replace('"', '\\"')

    osa_script = f'''
    tell application "Terminal"
        do script "echo '===== {title} ====='; {command_escaped}"
        activate
    end tell
    '''
    subprocess.run(["osascript", "-e", osa_script])


def open_terminal_windows(title: str, command: str):
    """Open a new Windows cmd window and run a command."""
    full_cmd = f'start "{title}" cmd /k "{command}"'
    subprocess.Popen(full_cmd, shell=True)


def open_terminal_default(title: str, command: str):
    """Dispatch to the correct terminal opener based on OS."""
    system = platform.system()

    if system == "Darwin":
        open_terminal_mac(title, command)
    elif system == "Windows":
        open_terminal_windows(title, command)
    else:
        # Fallback for Linux or other environments
        # This uses bash if available
        subprocess.Popen(["bash", "-lc", command])


def main():
    print("\n==============================")
    print("   WiCyS WatchTower Launcher")
    print("==============================\n")

    # 1. MQTT broker
    start_mosquitto()

    # 2. Commands for each part
    scanner_cmd = f'cd "{BACKEND_DIR}" && "{PYTHON}" nmap_scanner.py'
    simulator_cmd = f'cd "{BACKEND_DIR}" && "{PYTHON}" simple_simulator.py'
    frontend_cmd = f'cd "{FRONTEND_DIR}" && npm run dev'

    # 3. Launch each in its own terminal window
    open_terminal_default("WatchTower Scanner", scanner_cmd)
    open_terminal_default("IoT Simulator", simulator_cmd)
    open_terminal_default("Frontend Dashboard", frontend_cmd)

    print("\nAll WatchTower components launched. Check the new terminal windows.\n")


if __name__ == "__main__":
    main()
