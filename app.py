from flask import Flask, request, jsonify, render_template_string
import subprocess, os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Live Player</title>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<style>
body { background: #000; color: #fff; text-align: center; font-family: sans-serif; margin: 0; padding: 20px; }
input { width: 90%; max-width: 500px; padding: 12px; border-radius: 10px; border: none; outline: none; }
button { padding: 12px 20px; border-radius: 10px; border: none; background: #ff0055; color: #fff; font-weight: bold; margin-top: 10px; cursor: pointer; }
video { width: 100%; max-width: 800px; margin-top: 20px; background: #000; border-radius: 12px; display: none; }
#status { margin-top: 10px; color: #aaa; }
</style>
</head>
<body>
<h2>💖 Live Player 💖</h2>
<input id="link" type="text" placeholder="Paste Live Link Here...">
<br>
<button onclick="playLive()">▶️ Play Live</button>
<p id="status"></p>
<video id="video" controls autoplay playsinline></video>

<script>
async function playLive() {
  const link = document.getElementById('link').value;
  const video = document.getElementById('video');
  const status = document.getElementById('status');
  if (!link) { status.innerText = "Please Paste Link Baby!"; return; }
  status.innerText = "Loading... Please Wait Baby... 💖";
  video.style.display = "block";
  const res = await fetch('/get_m3u8', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({link: link})
  });
  const data = await res.json();
  if (data.m3u8) {
    status.innerText = "Playing... 🥰";
    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(data.m3u8);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function() { video.play(); });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = data.m3u8;
      video.play();
    } else {
      video.src = data.m3u8;
    }
  } else {
    status.innerText = "Live Not Found Baby! 🥺";
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/get_m3u8", methods=["POST"])
def get_m3u8():
    link = request.json.get("link", "").strip()
    try:
        result = subprocess.run(
            ["yt-dlp", "-g", "-f", "best[height<=720]/best", link],
            capture_output=True, text=True, timeout=30
        )
        url = result.stdout.strip().splitlines()
        if url and result.returncode == 0:
            return jsonify({"m3u8": url[0]})
        return jsonify({"error": "Not Found"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
