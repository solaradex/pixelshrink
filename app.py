import tempfile
import os
from flask import Flask, request, render_template_string, send_file
from processor import optimize_image
from PIL import Image
from pathlib import Path
import zipfile
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PixelShrink — Image Optimization Studio</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0; padding: 24px 16px 60px;
    background: radial-gradient(ellipse at 50% 0%, #29204d 0%, #101322 48%);
    color: #f5f3ff; font-family: Inter, Arial, sans-serif;
}
.container { max-width: 900px; margin: auto; }
nav {
    display: flex; justify-content: space-between;
    align-items: center; margin: 8px 0 65px;
}
.brand { font-size: 21px; font-weight: 800; color: #c4b5fd; }
.pill {
    border: 1px solid #494064; border-radius: 30px;
    padding: 8px 13px; color: #c4b5fd; font-size: 12px;
}
.hero { text-align: center; margin-bottom: 38px; }
.eyebrow {
    color: #c4b5fd; text-transform: uppercase;
    letter-spacing: 2px; font-size: 11px; font-weight: bold;
}
h1 { font-size: clamp(38px, 8vw, 68px); line-height: 1.05; margin: 18px 0; }
.gradient {
    background: linear-gradient(90deg,#c4b5fd,#8b5cf6,#e9d5ff);
    -webkit-background-clip: text; color: transparent;
}
.subtitle {
    color: #aaa9bd; font-size: 17px;
    line-height: 1.6; max-width: 540px; margin: auto;
}
.visual {
    max-width: 540px; margin: 34px auto 0;
    padding: 18px; border: 1px solid #393252;
    border-radius: 20px; background: #19172b;
    box-shadow: 0 15px 60px #0005;
}
.visual-top { display:flex; justify-content:space-between;
    color:#aaa9bd; font-size:12px; margin-bottom:14px; }
.preview { display:flex; align-items:center; gap:12px; }
.preview-box {
    flex:1; height:105px; border-radius:12px;
    display:flex; flex-direction:column; justify-content:center;
    align-items:center; gap:8px; background:linear-gradient(145deg,#51427d,#29233e);
}
.preview-box:last-child { background:linear-gradient(145deg,#8054c9,#39265f); }
.preview-box {
    height:130px;
    padding:8px;
    box-sizing:border-box;
    justify-content:flex-start;
    overflow:hidden;
}
.preview-box img {
    width:100% !important;
    height:82px !important;
    object-fit:cover;
    display:block;
}
.preview-icon { font-size:30px; }
.preview-label { font-size:11px; color:#e9ddff; }
.arrow { color:#c4b5fd; font-size:22px; }
.save {
    display:inline-block; margin-top:15px; padding:8px 13px;
    border-radius:20px; background:#30264c; color:#c4b5fd;
    font-size:12px; font-weight:bold;
}
.panel {
    max-width:650px; margin:35px auto;
    background:#1b1b30; border:1px solid #34314d;
    border-radius:22px; padding:25px;
    box-shadow:0 20px 60px #0003;
}
.panel h2 { margin-top:0; font-size:21px; }
.drop {
    display:block; padding:28px 14px; text-align:center;
    border:1px dashed #7763ad; border-radius:16px;
    background:#211e38; margin:20px 0;
}
.drop strong { display:block; margin:10px 0 5px; }
.drop small { color:#aaa9bd; }
input[type=file] { max-width:100%; color:#c4b5fd; }
.controls {
    display:flex; align-items:center; justify-content:space-between;
    flex-wrap:wrap; gap:12px; margin-top:18px;
}
.quality { color:#c2bfd4; font-size:14px; }
.quality {
    display:grid;
    grid-template-columns: 1fr auto;
    align-items:center;
    gap:12px;
}
.quality output {
    color:#c4b5fd;
    font-weight:bold;
}
.quality-hint {
    grid-column:1 / -1;
    display:block;
    color:#b5b0c8;
    font-size:14px;
}
input[type=range] {
    flex-basis:100%; width:100%; accent-color:#a855f7;
    cursor:pointer;
}
button {
    border:0; border-radius:12px; padding:14px 22px;
    background:linear-gradient(100deg,#8b5cf6,#a855f7);
    color:white; font-size:15px; font-weight:bold;
    box-shadow:0 5px 25px #8b5cf644;
}
button:active { transform:scale(.98); }
.features {
    display:grid; grid-template-columns:repeat(3,1fr);
    gap:14px; margin:35px 0;
}
.feature {
    background:#19192b; border:1px solid #302e48;
    border-radius:16px; padding:18px;
}
.feature-icon { font-size:23px; }
.feature h3 { font-size:14px; margin:12px 0 7px; }
.feature p { color:#aaa9bd; font-size:12px; line-height:1.5; margin:0; }
.result {
    background:#211e38; border:1px solid #494064;
    padding:20px; border-radius:16px; margin-top:25px;
}
.summary {
    display:grid; grid-template-columns:repeat(2,1fr);
    gap:12px; margin:18px 0;
}
.stat { background:#19172b; padding:15px; border-radius:12px; }
.stat span { display:block; color:#aaa9bd; font-size:12px; }
.stat strong { display:block; font-size:20px; margin-top:8px; }
.green { color:#86efac; }
.download {
    display:block; text-align:center; text-decoration:none;
    color:white; background:#7545c9; border-radius:11px;
    padding:14px; margin:18px 0; font-weight:bold;
}
.table-wrap { overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th,td { padding:12px 8px; text-align:left; border-bottom:1px solid #39344f; }
th { color:#aaa9bd; font-weight:600; }
td { overflow-wrap:anywhere; }
footer { text-align:center; color:#77758d; font-size:12px; margin-top:55px; }
@media(max-width:600px) {
    nav { margin-bottom:48px; }
    .features { grid-template-columns:1fr; }
    .panel { padding:18px; }
    .controls { align-items:stretch; flex-direction:column; }
    .controls button { width:100%; }
    .summary { gap:8px; }
    .stat strong { font-size:17px; }
    table { font-size:12px; }
}
</style>
</head>
<body>
<div class="container">
<nav><div class="brand">✦ PixelShrink</div><div class="pill">IMAGE OPTIMIZATION STUDIO</div></nav>

<section class="hero">
<div class="eyebrow">Less weight. More speed.</div>
<h1>Beautiful images.<br><span class="gradient">Smaller files.</span></h1>
<p class="subtitle">Optimize entire batches of images in seconds. Keep the quality. Lose the unnecessary file size.</p>
<div class="visual">
<div class="visual-top"><span>BEFORE</span><span>AFTER</span></div>
<div class="preview">
<div class="preview-box"><img src="/static/cardinal-original.jpg" alt="Original cardinal photo" style="width:100%;height:100px;object-fit:cover;border-radius:10px;"><div class="preview-label">Original · 1.43 MB</div></div>
<div class="arrow">→</div>
<div class="preview-box"><img src="/static/cardinal-optimized.jpg" alt="Optimized cardinal photo" style="width:100%;height:100px;object-fit:cover;border-radius:10px;"><div class="preview-label">Compressed · 0.96 MB</div></div>
</div>
<div class="save">↓ Less file size. Faster websites.</div>
</div>
</section>

<section class="panel">
<h2>Optimize your images</h2>
<p class="subtitle" style="font-size:14px;text-align:left;margin:0">Upload multiple images and download your optimized batch in one ZIP.</p>
<form method="POST" enctype="multipart/form-data">
<label class="drop">
<div style="font-size:28px;color:#c4b5fd">⇧</div>
<strong>Choose images to optimize</strong>
<small>Select multiple JPG, PNG, or WebP files</small>
<br><br>
<input type="file" name="images" accept="image/*" multiple required>
</label>
<div class="controls">
<label class="quality" for="quality">
  <span>Compression quality</span>
  <span><output id="quality-value">80</output>%</span>
  <small id="quality-hint" class="quality-hint">High quality, balanced compression</small>
  <input type="range" id="quality" name="quality" min="1" max="100" value="80"
         oninput="document.getElementById('quality-value').textContent=this.value;
const hint=document.getElementById('quality-hint');
const q=Number(this.value);
hint.textContent=q>=90?'Highest quality, larger files':
q>=70?'High quality, balanced compression':
q>=40?'Smaller files, noticeable quality trade-offs':
'Maximum compression, possible visible artifacts'">
</label>
<button type="submit">✦ Optimize images</button>
</div>
</form>
{% if result %}
<div class="result">
<h2>Optimization complete ✨</h2>
<p>{{ result.count }} images processed successfully</p>
<div class="summary">
<div class="stat"><span>Original total</span><strong>{{ result.original }} KB</strong></div>
<div class="stat"><span>Optimized total</span><strong>{{ result.optimized }} KB</strong></div>
<div class="stat"><span>Space saved</span><strong class="green">{{ result.savings }}%</strong></div>
<div class="stat"><span>Files processed</span><strong>{{ result.count }}</strong></div>
</div>
<a class="download" href="{{ url_for('download', download_id=result.download_id) }}">↓ Download optimized ZIP</a>
<h3>Individual image results</h3>
<div class="table-wrap">
<table>
<tr><th>Image</th><th>Original</th><th>Optimized</th><th>Saved</th></tr>
{% for image in result.images %}
<tr><td>{{ image.name }}</td><td>{{ image.original }} KB</td><td>{{ image.optimized }} KB</td><td class="green">{{ image.savings }}%</td></tr>
{% endfor %}
</table>
</div>
</div>
{% endif %}
</section>

<section class="features">
<div class="feature"><div class="feature-icon">✧</div><h3>Smart compression</h3><p>Reduce image file sizes while keeping control over quality.</p></div>
<div class="feature"><div class="feature-icon">▦</div><h3>Bulk processing</h3><p>Optimize multiple images together instead of one at a time.</p></div>
<div class="feature"><div class="feature-icon">⇩</div><h3>Easy downloads</h3><p>Get your optimized WebP images packaged in one ZIP.</p></div>
</section>
<footer>PixelShrink · A simpler way to optimize images</footer>
</div>
</body>
</html>
"""

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "pixelshrink-downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        files = request.files.getlist("images")
        quality = request.form.get("quality", 80, type=int)
        files = [f for f in files if f and f.filename]

        if files:
            try:
                zip_buffer = io.BytesIO()
                original_total = 0
                optimized_total = 0
                processed = 0
                image_results = []

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                    for file in files:
                        data = file.read()
                        if not data:
                            continue

                        image = Image.open(io.BytesIO(data))
                        image.verify()
                        optimized, stats = optimize_image(io.BytesIO(data), quality)

                        filename = secure_filename(file.filename.rsplit(".", 1)[0])
                        archive.writestr(f"{filename or 'image'}.webp", optimized)

                        original_total += stats["original"]
                        optimized_total += stats["optimized"]
                        image_results.append({
                            "name": file.filename,
                            "original": round(stats["original"] / 1024, 2),
                            "optimized": round(stats["optimized"] / 1024, 2),
                            "savings": stats["savings"]
                        })
                        processed += 1

                if processed == 0:
                    return "No valid images were uploaded.", 400

                download_id = os.urandom(16).hex()
                zip_path = DOWNLOAD_DIR / f"{download_id}.zip"
                zip_path.write_bytes(zip_buffer.getvalue())

                result = {
                    "count": processed,
                    "images": image_results,
                    "original": round(original_total / 1024, 2),
                    "optimized": round(optimized_total / 1024, 2),
                    "savings": round((1 - optimized_total / original_total) * 100, 2),
                    "download_id": download_id
                }
            except Exception as e:
                app.logger.exception("Bulk image processing failed")
                return f"Image error: {e}", 400

    return render_template_string(HTML, result=result)

@app.route("/download/<download_id>")
def download(download_id):
    if not download_id.isalnum() or len(download_id) != 32:
        return "Download not found or expired.", 404

    zip_path = DOWNLOAD_DIR / f"{download_id}.zip"
    if not zip_path.is_file():
        return "Download not found or expired.", 404

    response = send_file(
        zip_path,
        mimetype="application/zip",
        as_attachment=True,
        download_name="pixelshrink-images.zip"
    )

    @response.call_on_close
    def remove_download():
        try:
            zip_path.unlink(missing_ok=True)
        except OSError:
            app.logger.warning("Could not remove temporary ZIP: %s", zip_path)

    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
