from flask import Flask, request, render_template_string
import subprocess, os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Live Player</title>
<style>
body { background: #000; color: #fff; text-align: center; font-family: sans-serif; margin: 0; padding: 20px; }
h2 { font-size: 20px; }
input { width: 90%; max-width: 500px; padding: 12px; border-radius: 10px; border: none; outline: none; }
button { padding: 12px 20px; border-radius: 10px; border: none; background: #ff0055; color: #fff; font-weight: bold; margin-top: 10px; }
video { width: 100%; max-width: 800px; margin-top: 20px; background: #000; border-radius: 12px; }
.box { margin-top: 15px; font-size: 12px; word-break: break-all; color: #aaa; }
</style>
</head>
<body>
<h2>💖 Live Player 💖</h2>
<form method="POST">
<input type="text" name="link" placeholder="Paste Live Link Here..." required>
<br>
<button type="submit">▶️ Play Live</button>
</form>
{% if m3u8 %}
<video src="{{ m3u8 }}" controls autoplay playsinline></video>
<div class="box">M3U8: {{ m3u8 }}</div>
{% endif %}
{% if error %}
<p style="color:red;">{{ error }}</p>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    m3u8 = None
    error = None
    if request.method == "POST":
        link = request.form.get("link", "").strip()
        try:
            result = subprocess.run(
                ["yt-dlp", "-g", "-f", "best[height<=720]/best", link],
                capture_output=True, text=True, timeout=30
            )
            url = result.stdout.strip().splitlines()
            if url and result.returncode == 0:
                m3u8 = url[0]
            else:
                error = "Live Not Found! Try Again!"
        except Exception as e:
            error = f"Error: {e}"
    return render_template_string(HTML, m3u8=m3u8, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
