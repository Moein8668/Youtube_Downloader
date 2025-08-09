# YouTube URL Downloader & Web Interface

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)  
[![Built with yt-dlp](https://img.shields.io/badge/yt--dlp-supported-brightgreen.svg)](https://github.com/yt-dlp/yt-dlp)

> A self-hosted web app that makes downloading YouTube videos and playlists simple.  
> Clean UI, playlist selection, audio-only downloads, and a small CLI for server management.

---

## ✨ Features

- **Simple Web UI** — paste a YouTube URL (video or playlist) and the app detects it automatically.  
- **Video & Audio** — download full video in available resolutions or extract audio-only (MP3).  
- **Playlist Support & Selection** — detect playlists and let you pick individual videos from a playlist to download.  
- **File Browser** — browse, stream, download, and delete files from the server through the UI.  
- **Robust Installer** — one `install.sh` script configures the app and a Python virtual environment on Debian/Ubuntu.  
- **CLI Tool (`yt-url-d`)** — manage the service, view logs, and update components from the command line.  
- **Systemd Service** — runs as a background service and can be enabled on boot.

---

## 🔧 Requirements

- Debian/Ubuntu-based server (tested on Ubuntu/Debian).  
- Python 3.9+ (the installer creates/uses a virtualenv).  
- `ffmpeg` installed for audio/video processing.  
- (Optional) SOCKS5 proxy if YouTube is blocked in your region.

---

## 🚀 Quick Install

```bash
# clone & run installer (must be run as root or with sudo)
git clone https://github.com/Moein8668/Youtube_Downloader.git
cd Youtube_Downloader
sudo bash install.sh
```

The installer will create a virtual environment, install dependencies (including `yt-dlp`), and create a systemd service for the app.

---

## ⚙️ Proxy configuration (important)

By default the app is configured to use a **SOCKS5** proxy to help users in regions where YouTube may be blocked.

- **If you DO NOT need a proxy**, edit the app after installation:

```bash
sudo nano /opt/yt-url-downloader/app.py
# remove any occurrences of: ("--proxy", proxy_url)
# Save (Ctrl+O) and exit (Ctrl+X)
```

Then restart the service via the CLI tool:

```bash
sudo yt-url-d
# choose "Restart Service"
```

---

## 🌐 Usage — Web interface

Open your browser and visit:

```
http://<your_server_ip>:2082
```

Paste a video or playlist URL and the UI will detect the content.  
When a playlist is detected the UI shows all items — check the videos you want and download them in batch or individually. Choose audio-only to download just the MP3.

---

## 🧰 CLI tool

The included `yt-url-d` tool (installed as a system command) helps you:

- Start / Stop / Restart the systemd service
- View recent logs
- Update the application or `yt-dlp`

Run:

```bash
sudo yt-url-d
```

and follow the menu.

---

## 🔄 Update yt-dlp (manual)

If you prefer manual updating:

```bash
sudo pip install --upgrade yt-dlp
```

Or use the `yt-url-d` CLI updater.

---

## 🔐 Security & best-practices

- Run behind a firewall and only open required ports.  
- Consider using an Nginx reverse proxy with HTTPS (Let's Encrypt) if you expose the app to the internet.  
- Limit access with a VPN or HTTP auth if the instance is reachable from public networks.

---

## 📁 File browser

Use the built-in file browser page to:

- Stream media directly in the browser
- Download files to your machine
- Delete files you no longer need

Files are stored in the configured downloads directory (see `install.sh` / config).

---

## 🧩 Extensibility & notes

- The app uses `yt-dlp` as its backend downloader; it supports many sites and formats.  
- Audio extraction requires `ffmpeg` to be installed on the host.  
- Systemd is used for service management so the app can run in the background and start on boot.

---

## ⚖️ Disclaimer

This project is intended for **personal and educational use only**. The ability to download content is provided to allow users to create backups of their own content or to download publicly available, non-copyrighted media. You are responsible for ensuring your use complies with local laws and the terms of service of the sites you access. The maintainers are not responsible for misuse.

---

## 🧾 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Please open an issue or a pull request with a clear description.

---

## 📬 Contact

If you find bugs or want to suggest improvements, open an issue on the repo or submit a PR.

---

## Changelog & TODO

- v1 — Initial release with web UI, playlist selection, file browser, systemd service.  
- TODO: Add optional authentication, improved CLI tool.

