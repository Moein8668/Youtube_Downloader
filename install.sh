#!/bin/bash

# --- Configuration ---
APP_NAME="yt-url-downloader"
INSTALL_DIR="/opt/$APP_NAME"
DOWNLOAD_DIR="/var/yt-downloads"
SERVICE_USER="yt-downloader"
CLI_COMMAND="yt-url-d"

# --- Script Start ---

# 1. Check for Root Privileges
if [ "$EUID" -ne 0 ]; then
  echo "❌ This script must be run as root. Please use 'sudo bash $0'."
  exit 1
fi

echo "🚀 Starting the YouTube URL Downloader installation..."

# 2. Install Dependencies
echo "📦 Installing system dependencies (git, python, pip, venv, ffmpeg, dos2unix)..."
apt-get update
apt-get install -y git python3 python3-pip python3-venv ffmpeg dos2unix

# 3. Create User and Directories
echo "🔧 Setting up user and directories..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /bin/false $SERVICE_USER
fi
mkdir -p "$INSTALL_DIR"
mkdir -p "$DOWNLOAD_DIR"

# 4. Copy Application Files
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
echo "📂 Copying application files to '$INSTALL_DIR'..."
cp -r "$SCRIPT_DIR/app.py" "$SCRIPT_DIR/yt-url-d.py" "$SCRIPT_DIR/templates" "$SCRIPT_DIR/static" "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# 5. Fix Line Endings
echo "📜 Converting text file line endings to Unix format..."
dos2unix "$INSTALL_DIR/app.py"
dos2unix "$INSTALL_DIR/yt-url-d.py"

# 6. Set up Python Virtual Environment
echo "🐍 Creating Python virtual environment and installing packages..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"
pip install -r "$INSTALL_DIR/requirements.txt"
deactivate

# 7. Set Permissions
echo "🔐 Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$DOWNLOAD_DIR"
chmod +x "$INSTALL_DIR/yt-url-d.py"

# 8. Create the systemd Service File
echo "⚙️ Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=YouTube URL Downloader Web Service
After=network.target

[Service]
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 9. Create the CLI command (More Robustly)
echo "🔗 Creating the '$CLI_COMMAND' command..."
if [ -f "$INSTALL_DIR/yt-url-d.py" ]; then
    ln -sf "$INSTALL_DIR/yt-url-d.py" "/usr/local/bin/$CLI_COMMAND"
    echo "   - Command link created successfully."
else
    echo "   - ⚠️ WARNING: Could not find '$INSTALL_DIR/yt-url-d.py'. The '$CLI_COMMAND' command was NOT created."
fi

# 10. Finalize Service
echo "🚀 Reloading, enabling, and starting the service..."
systemctl daemon-reload
systemctl enable "$APP_NAME.service"
systemctl restart "$APP_NAME.service"

echo "✅ Installation Complete!"
echo "--------------------------------------------------"
echo "Your downloader should now be running."
echo "Access it at: http://$(hostname -I | awk '{print $1'}):2082"
echo ""
echo "To manage the application, use the command: sudo $CLI_COMMAND"
echo "--------------------------------------------------"