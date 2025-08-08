from flask import Flask, request, render_template, jsonify
from flask import send_from_directory, abort
import subprocess
import os
import json
from urllib.parse import quote, unquote
import math


proxy_url = "socks5://yotube:2@127.0.0.1:49087"


# Define the path to your cookies file
COOKIES_FILE_PATH = os.path.expanduser("~/.config/yt-dlp/cookies.txt")


app = Flask(__name__)

def get_video_info(url):
    try:
        cmd = ["yt-dlp", "-j", url, "--proxy", proxy_url, "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"]

        if "playlist" in url or "list=" in url:
            cmd = ["yt-dlp", "-J", url, "--proxy", proxy_url, "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"]

        if os.path.exists(COOKIES_FILE_PATH):
            cmd.extend(["--cookies", COOKIES_FILE_PATH])
        else:
            print(f"WARNING: Cookies file not found at {COOKIES_FILE_PATH}. Bot detection likely.")

        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        return json.loads(process.stdout.strip())

    except subprocess.CalledProcessError as e:
        print("Error during yt-dlp execution (CalledProcessError):")
        print("STDERR:", e.stderr)
        
        if 'Signature extraction failed' in e.stderr or 'yt-dlp -U' in e.stderr:
            return {'error': 'outdated', 'message': 'Processing failed. The server\'s yt-dlp version is likely outdated. Please update it by running "yt-dlp -U" on the server.'}
        
        return None

    except json.JSONDecodeError as e:
        print("JSON Decode Error: Likely non-JSON output from yt-dlp.")
        print("Raw STDOUT:", e.doc)
        return None
    except Exception as e:
        print("An unexpected error occurred:", e)
        return None

def convert_bytes(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/api/detect', methods=['POST'])
def api_detect():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': True, 'message': 'URL is required.'}), 400

    info = get_video_info(url)
    
    if not info:
        return jsonify({'error': True, 'message': 'Failed to detect URL. Please check the URL and try again.'})

    if info.get("error"):
        return jsonify({'error': True, 'message': info['message']})

    response_data = {'error': False}
    if info.get("_type") == "playlist":
        response_data['detected_type'] = "Playlist"
        entries = info.get("entries", [])
        response_data['playlist_count'] = len(entries)
        response_data['playlist_items'] = []
        
        for i, entry in enumerate(entries):
            response_data['playlist_items'].append({
                'index': i + 1,
                'title': (entry.get("title") if entry else "Unavailable Video") or "Untitled"
            })

        if info.get('thumbnails'):
            response_data['thumbnail_url'] = info['thumbnails'][-1]['url']
        elif entries and entries[0] and entries[0].get('thumbnails'):
            response_data['thumbnail_url'] = entries[0]['thumbnails'][-1]['url']
    else:
        response_data['detected_type'] = "Single Video"
        response_data['video_title'] = info.get("title", "Unknown Title")
        if info.get('thumbnails'):
            response_data['thumbnail_url'] = info['thumbnails'][-1]['url']
            
    return jsonify(response_data)

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json()
    url = data.get('url')
    resolution = data.get('resolution', '720')
    playlist_selection = data.get('playlist_selection', '')

    if not url:
        return jsonify({'error': True, 'message': 'URL is required for download.'}), 400

    out_folder = "/var/yt-downloads"
    os.makedirs(out_folder, exist_ok=True)

    base_cmd = [
        "yt-dlp", "--retries", "10", "--fragment-retries", "20", "--ignore-errors",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--proxy", proxy_url,
    ]

    if os.path.exists(COOKIES_FILE_PATH):
        base_cmd.extend(["--cookies", COOKIES_FILE_PATH])

    if resolution == "audio":
        base_cmd.extend([
            "-f", "bestaudio/best", "-x", "--audio-format", "mp3",
            "--audio-quality", "0", "--embed-thumbnail",
        ])
    else:
        base_cmd.extend([
            "-f", f"bestvideo[height<={resolution}]+bestaudio",
            "--merge-output-format", "mp4",
        ])

    output_template = "%(playlist)s/%(playlist_index)02d - %(title)s.%(ext)s" if "playlist" in url or "list=" in url else "%(title)s.%(ext)s"
    
    if ("playlist" in url or "list=" in url) and playlist_selection:
        base_cmd.extend(["--playlist-items", playlist_selection])
    
    cmd = base_cmd + ["-o", output_template, url]
    subprocess.Popen(cmd, cwd=out_folder)
    
    return jsonify({'error': False, 'message': '✅ Download started in the background!'})


@app.route('/files/', methods=["GET", "POST"])
@app.route('/files/<path:subpath>', methods=["GET", "POST"])
def browse_files(subpath=''):
    base_path = '/var/yt-downloads'
    full_path = os.path.join(base_path, subpath)

    if request.method == "POST":
        to_delete_quoted = request.form.get("delete")
        to_delete_unquoted = unquote(to_delete_quoted) 
        delete_path = os.path.join(base_path, to_delete_unquoted)

        if os.path.exists(delete_path):
            try:
                if os.path.isfile(delete_path):
                    os.remove(delete_path)
                elif os.path.isdir(delete_path):
                    if not os.listdir(delete_path):
                        os.rmdir(delete_path)
            except OSError as e:
                print(f"Error deleting {delete_path}: {e}")

    if not os.path.exists(full_path):
        return abort(404)

    if os.path.isfile(full_path):
        return abort(405)

    disk = os.statvfs(base_path)
    free_mb = (disk.f_bavail * disk.f_frsize) // (1024 * 1024)

    files = []
    folders = []
    entries = sorted(os.listdir(full_path))

    for entry in entries:
        entry_rel_path = os.path.join(subpath, entry)
        full_entry_path = os.path.join(full_path, entry)
        if os.path.isfile(full_entry_path):
            file_ext = os.path.splitext(entry)[1].lower()
            file_type = 'video'
            audio_extensions = ['.mp3', '.m4a', '.wav', '.flac', '.ogg', '.opus']
            if file_ext in audio_extensions:
                file_type = 'audio'

            file_size_bytes = os.path.getsize(full_entry_path)
            file_size_human = convert_bytes(file_size_bytes)
            files.append({
                'name': entry,
                'path': quote(entry_rel_path),
                'size': file_size_human,
                'type': file_type
            })
        else:
            folders.append({
                'name': entry,
                'path': quote(entry_rel_path)
            })

    parent_path = os.path.dirname(subpath) if subpath else None

    return render_template("files.html",
                           current_path=subpath,
                           free_mb=free_mb,
                           files=files,
                           folders=folders,
                           parent_path=parent_path)

@app.route('/download/<path:filename>')
def download_file(filename):
    base_path = '/var/yt-downloads'
    return send_from_directory(base_path, filename, as_attachment=True)

@app.route('/play/<path:filename>')
def play_file(filename):
    base_path = '/var/yt-downloads'
    full_file_path = os.path.join(base_path, filename)

    if not os.path.exists(full_file_path) or not os.path.isfile(full_file_path):
        abort(404)

    video_title = os.path.basename(filename)
    video_url = f"/stream/{quote(filename)}"

    return render_template("play_video.html", video_title=video_title, video_url=video_url)

@app.route('/stream/<path:filename>')
def stream_file(filename):
    base_path = '/var/yt-downloads'
    return send_from_directory(base_path, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2082)