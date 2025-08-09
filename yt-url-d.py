#!/usr/bin/env python3
import os
import sys
import subprocess

# --- Configuration ---
APP_NAME = "yt-url-downloader"
SERVICE_FILE = f"{APP_NAME}.service"
# This must match the directory in the install.sh script
INSTALL_DIR = f"/opt/{APP_NAME}"

# --- Helper Functions ---

def check_root():
    """Checks if the script is run as root, exits if not."""
    if os.geteuid() != 0:
        print(f"❌ This command requires root privileges. Please run with 'sudo {sys.argv[0]}'")
        sys.exit(1)

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def press_enter_to_continue():
    """Pauses execution until the user presses Enter."""
    input("\nPress Enter to return to the menu...")

# --- Core Logic Functions ---

def manage_service(action):
    """Handles start, stop, and restart actions for the systemd service."""
    print(f"⚙️ Attempting to {action} the {APP_NAME} service...")
    try:
        subprocess.run(["systemctl", action, SERVICE_FILE], check=True, capture_output=True)
        print(f"✅ Success! The service has been {action}ed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Failed to {action} the service.")
        print(f"   Details: {e.stderr.strip()}")
    press_enter_to_continue()

def manage_startup(enable):
    """Enables or disables the service from starting on boot."""
    action = "enable" if enable else "disable"
    print(f"⚙️ Attempting to {action} service startup...")
    try:
        subprocess.run(["systemctl", action, SERVICE_FILE], check=True, capture_output=True)
        if enable:
            print("✅ Success! The service is now enabled to start on boot.")
        else:
            print("✅ Success! The service is now disabled from starting on boot.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Failed to {action} service startup.")
        print(f"   Details: {e.stderr.strip()}")
    press_enter_to_continue()

def view_live_log():
    """Shows the live output of the service log."""
    print(f"🔴 Showing live log for {APP_NAME}. Press Ctrl+C to exit.")
    try:
        # We don't capture output here, we let it run in the foreground
        subprocess.run(["journalctl", "-u", SERVICE_FILE, "-f", "-n", "50"])
    except FileNotFoundError:
        print("❌ Error: 'journalctl' command not found.")
    except KeyboardInterrupt:
        # This allows a clean exit back to the menu
        print("\n✅ Log view stopped.")
    press_enter_to_continue()

def update_yt_dlp():
    """Updates the yt-dlp package within the application's virtual environment."""
    pip_path = os.path.join(INSTALL_DIR, "venv/bin/pip")
    
    if not os.path.exists(pip_path):
        print(f"❌ Error: Could not find pip at '{pip_path}'. Is the app installed correctly?")
        press_enter_to_continue()
        return

    print("🌐 Attempting to update yt-dlp using pip...")
    try:
        # We run the pip command from the virtual environment
        process = subprocess.run(
            ["pip" , "install", "--upgrade", "yt-dlp"],
            check=True, capture_output=True, text=True
        )
        print("✅ Update process finished. See details below:")
        print("-------------------------------------------")
        print(process.stdout)
        print("-------------------------------------------")
    except subprocess.CalledProcessError as e:
        print("❌ Error: The update command failed.")
        print("-------------------------------------------")
        print(e.stdout)
        print(e.stderr)
        print("-------------------------------------------")
    press_enter_to_continue()

# --- Main Menu ---

def main_menu():
    """Displays the main settings menu and handles user input."""
    while True:
        clear_screen()
        print("======================================")
        print(f"  Control Panel for {APP_NAME}")
        print("======================================")
        print("\n--- Service Actions ---")
        print("  1. Start Service")
        print("  2. Stop Service")
        print("  3. Restart Service")
        print("\n--- Startup Actions ---")
        print("  4. Enable Startup on Boot")
        print("  5. Disable Startup on Boot")
        print("\n--- Diagnostics & Updates ---")
        print("  6. View Live Log")
        print("  7. Update yt-dlp")
        print("\n  8. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1': manage_service("start")
        elif choice == '2': manage_service("stop")
        elif choice == '3': manage_service("restart")
        elif choice == '4': manage_startup(True)
        elif choice == '5': manage_startup(False)
        elif choice == '6': view_live_log()
        elif choice == '7': update_yt_dlp()
        elif choice == '8':
            print("\nExiting.")
            break
        else:
            print("\nInvalid choice, please try again.")
            press_enter_to_continue()

if __name__ == "__main__":
    check_root()

    main_menu()
