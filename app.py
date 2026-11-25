from flask import Flask, request, jsonify, render_template_string
import subprocess, os, json

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
button, select { padding: 12px 15px; border-radius: 10px; border: none; background: #ff0055; color: #fff; font-weight: bold; margin-top: 10px; cursor: pointer; }
select { background: #222; }
video { width: 100%; max-width: 800px; margin-top: 20px; background: #000; border-radius: 12px; display: none; }
#status { margin-top: 10px; color: #aaa; }
.row { margin-top: 10px; }
</style>
</head>
<body>
<h2>💖 Live Player 💖</h2>
<input id="link" type="text" placeholder="Paste Live Link Here...">
<br>
<button onclick="playLive()">▶️ Play Live</button>
<div class="row">
<label>Quality: </label>
<select id="quality" onchange="changeQuality()">
<option value="-1">Auto ✨</option>
</select>
</div>
<p id="status"></p>
<video id="video" controls autoplay playsinline></video>
<script>
let hls = null;
async function playLive() {
  const link = document.getElementById('link').value;
  const video = document.getElementById('video');
  const status = document.getElementById('status');
  if (!link) { status.innerText = "Please Paste Link Baby!"; return; }
  status.innerText = "Loading... Please Wait Baby... 💖";
  video.style.display = "block";
  if (hls) { hls.destroy(); hls = null; }
  const res = await fetch('/get_m3u8', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({link: link})
  });
  const data = await res.json();
  if (data.m3u8) {
    status.innerText = "Playing... 🥰";
    if (Hls.isSupported()) {
      hls = new Hls();
      hls.loadSource(data.m3u8);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function() {
        video.play();
        // Fill Quality List from m3u8
        const q = document.getElementById('quality');
        q.innerHTML = '<option value="-1">Auto ✨</option>';
        hls.levels.forEach((level, i) => {
          const h = level.height;
          const opt = document.createElement('option');
          opt.value = i;
          opt.text = h + 'p';
          q.appendChild(opt);
        });
      });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = data.m3u8;
      video.play();
    }
  } else {
    status.innerText = "Live Not Found Baby! 🥺";
  }
}
function changeQuality() {
  const q = document.getElementById('quality').value;
  if (hls) {
    hls.currentLevel = parseInt(q);
    document.getElementById('status').innerText = q == -1 ? "Auto Quality ✨" : "Quality Changed 🥰";
  }
}
</script>
</body>
</html>
"""

def get_master_m3u8(link):
    # Get master m3u8 that has ALL qualities inside
    try:
        r = subprocess.run(["yt-dlp", "-j", "--no-playlist", link], capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout)
        # 1. manifest_url is the master m3u8 with all qualities
        if data.get("manifest_url"):
            return data["manifest_url"]
        # 2. Find format that is master / has all
        for f in data.get("formats", []):
            if f.get("format_id") == "hls-0" or "master" in str(f.get("format_note", "")).lower():
                return f.get("url")
    except Exception as e:
        print(f"JSON failed: {e}")
    # 3. Fallback -g
    try:
        r2 = subprocess.run(["yt-dlp", "-g", "-f", "best", link], capture_output=True, text=True, timeout=30)
        urls = r2.stdout.strip().splitlines()
        if urls:
            return urls[0]
    except Exception as e:
        print(e)
    return None

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/get_m3u8", methods=["POST"])
def get_m3u8():
    link = request.json.get("link", "").strip()
    m3u8 = get_master_m3u8(link)
    if m3u8:
        return jsonify({"m3u8": m3u8})
    return jsonify({"error": "Not Found"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
