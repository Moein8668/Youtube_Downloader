# YouTube URL Downloader & Web Interface

A self-hosted web application that allows you to download YouTube videos and playlists with a clean user interface. The project includes a powerful command-line tool for easy server management.

## Features

-   **Simple Web UI**: Clean, responsive interface for detecting and downloading videos.
-   **Video & Audio**: Download videos in various resolutions or as audio-only MP3 files.
-   **Playlist Support**: Detects playlists and allows you to select specific videos to download.
-   **File Browser**: A built-in page to browse, play, download, and delete your files.
-   **Robust Installer**: A single `install.sh` script to set up everything on a Debian/Ubuntu server.
-   **Powerful CLI**: A command-line tool (`yt-url-d`) for easy service management, log viewing, and updates.
-   **Systemd Service**: Runs as a proper background service that can be configured to start on boot.

## Installation

This application is designed to be installed on a Debian-based Linux server (like Ubuntu).

```bash
git https://github.com/Moein8668/Youtube_Downloader.git
cd Youtube_Downloader
sudo bash install.sh
```

# Important: Proxy Configuration
By default, this application is configured to use a SOCKS5 proxy. This is useful for users in regions where YouTube may be blocked or restricted.

If you do NOT have or need a proxy, you MUST manually edit the app.py file after installation.

Follow these steps:

Open the application's main file for editing:

sudo nano /opt/yt-url-downloader/app.py

Find and delete this part ("--proxy", proxy_url) in any part you can see it.

Save the file (Ctrl+O, then Enter) and exit (Ctrl+X).


Restart the service for the changes to take effect. The easiest way is to use the command-line tool:

sudo yt-url-d

Then choose the "Restart Service" option.

Usage
Web Interface

You can access the web application in your browser at:
http://<your_server_ip>:2082


Manual yt-dlp Update

The command-line tool (sudo yt-url-d) provides the easiest way to update yt-dlp. However, if you need to do it manually, you can run the following command:
sudo /opt/yt-url-downloader/venv/bin/pip install --upgrade yt-dlp

Disclaimer
This project is intended for personal and educational use only. The ability to download content is provided to allow users to create personal backups of their own content or publicly available, non-copyrighted media.
Users are solely responsible for the content they choose to download and must comply with their local laws and the terms of service of any website they use with this tool. The developers of this project hold no responsibility for any misuse of this application.


License

This project is licensed under the MIT License. See the LICENSE file for details.
