from flask import Flask, request, send_file, render_template_string, session
import google.generativeai as genai
from PIL import Image
import io
import os # buat ambil key dari Render

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kunci_rahasia_default") 

# ========== SETTING AMAN ==========
# Key diambil dari Environment Variable, bukan ditulis di sini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)
KUOTA_GRATIS = 5
# ==================================

HTML = """
<!DOCTYPE html>
<html>
<head><title>Tools by Andik</title>
<style>
    body{font-family:Arial; text-align:center; padding:30px; background:#f5f5f5}
 .box{background:white; padding:30px; border-radius:12px; max-width:500px; margin:auto; box-shadow:0 4px 10px rgba(0,0,0,0.1)}
    button{padding:12px 20px; margin:10px; border:none; border-radius:8px; cursor:pointer; font-weight:bold}
 .pro{background:#ff4d4d; color:white}
    input{margin:10px 0}
    #popup{display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); justify-content:center; align-items:center}
 .popup-box{background:white; padding:30px; border-radius:15px; width:90%; max-width:400px}
 .harga-corett{text-decoration:line-through; color:gray}
 .paket{border:2px solid #ff4d4d; padding:15px; border-radius:10px; margin:10px 0}
</style>
</head>
<body>
    <div class="box">
    <h2>TOOLS BY ANDIK</h2>
    <p>Kuota Gratis Kamu: <b id="kuota">{{kuota}}</b>/5</p>
    <form id="form-generate" method="post" enctype="multipart/form-data">
        <p>1. Upload Foto Orang</p>
        <input type="file" name="orang" required><br>
        <p>2. Upload Foto Baju</p>
        <input type="file" name="baju" required><br><br>
        <button class="pro" type="submit">Generate Sekarang</button>
    </form>
    </div>

    <div id="popup">
        <div class="popup-box">
            <h2> KUOTA HABIS!</h2>
            <p>Kamu sudah 5x generate minggu ini<br>Upgrade ke Premium untuk UNLIMITED</p>

            <div class="paket">
                <h3>PAKET MINGGUAN</h3>
                <p><span class="harga-corett">15rb</span> <b>6rb</b></p>
                <p>Unlimited + HD Upscale + Remove BG</p>
                <button onclick="alert('Transfer 6rb ke DANA 08xx ya bang')">Upgrade</button>
            </div>

            <div class="paket" style="background:#fff0f0">
                <h3>PAKET BULAN </h3>
                <p><span class="harga-corett">60rb</span> <b>18rb</b></p>
                <p>Semua Fitur Mingguan + Face Swap + Prioritas</p>
                <button style="background:green; color:white" onclick="alert('Transfer 18rb ke DANA 08xx ya bang')">Paling Worth</button>
            </div>
            <button onclick="document.getElementById('popup').style.display='none'">Nanti Dulu</button>
        </div>
    </div>

<script>
let kuota = {{kuota}};
document.getElementById('form-generate').onsubmit = async function(e){
    e.preventDefault();
    if(kuota >= 5){
        document.getElementById('popup').style.display='flex';
        return;
    }
    let formData = new FormData(this);
    let res = await fetch('/', {method:'POST', body:formData});
    if(res.status == 403){
        document.getElementById('popup').style.display='flex';
        return;
    }
    let blob = await res.blob();
    let url = URL.createObjectURL(blob);
    window.open(url);
    kuota++;
    document.getElementById('kuota').innerText = kuota;
}
</script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if "count" not in session: session["count"] = 0

    if request.method == "POST":
        if session["count"] >= KUOTA_GRATIS:
            return "KUOTA HABIS", 403 

        img_orang = Image.open(request.files["orang"])
        img_baju = Image.open(request.files["baju"])

        model = genai.GenerativeModel("gemini-2.5-flash-image-preview")
        prompt = "Ganti baju orang di foto pertama dengan baju di foto kedua. Pertahankan wajah, pose, background 100%. Hasil photorealistic, real photo, 4K"
        result = model.generate_content([prompt, img_orang, img_baju])
        img_bytes = result.parts[0].inline_data.data

        session["count"] += 1
        return send_file(io.BytesIO(img_bytes), mimetype="image/jpeg")

    return render_template_string(HTML, kuota=session["count"])

if __name__ == "__main__":
    app.run(debug=True, port=5000)