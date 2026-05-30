from flask import Flask, render_template_string, request, redirect
import socket
import subprocess
import os

app = Flask(__name__)

# =========================
# ESTADO DOS ARQUIVOS
# =========================

# Dicionário para gerenciar o estado dos arquivos.
# "Nome de Exibição": {"filename": "nome_real_do_arquivo.extensao", "active": False}
estado = {
    "HOLOGRAMA": {"filename": "optionalavatarres_commonab_shader.QHkA1UM66uoNm4liVqb0K4NKohM~3D", "active": False},
    # Adicione outros arquivos aqui se necessário
}

# =========================
# DIRETÓRIOS
# =========================

# Local de destino no Free Fire Max
DESTINO_FFMAX = "/sdcard/Android/data/com.dts.freefiremax/files/contentcache/Optional/android/optionalavatarres/gameassetbundles"

# Local para guardar o arquivo original (Music)
PASTA_ORIGINAL = "/sdcard/Music"

# Local onde fica o arquivo modificado (Download)
PASTA_MODIFICADO = "/sdcard/Movies"

adb_online = False

# =========================
# PEGAR IP LOCAL
# =========================

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# =========================
# HTML
# =========================

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>BERLIM SYSTEM</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins', sans-serif;}
html,body{width:100%;height:100%;overflow:hidden;background:#000;color:#fff;}
.top{display:flex;justify-content:space-between;align-items:center;padding:18px;}
.left{display:flex;align-items:center;gap:14px;}
.menu{width:55px;height:55px;border-radius:18px;background:#0b0b0b;border:1px solid #300;color:#ff0000;display:flex;justify-content:center;align-items:center;font-size:28px;cursor:pointer;}
.logo{font-size:30px;font-weight:700;line-height:30px;}
.logo span{color:#ff0000;}
.online_on{color:#00ff66;font-weight:700;}
.online_off{color:#ff3333;font-weight:700;}
.sidebar{position:fixed;top:0;left:-220px;width:210px;height:100%;background:#050505;border-right:1px solid #220000;transition:0.3s;padding-top:90px;z-index:999;}
.sidebar a{display:block;padding:20px;color:white;text-decoration:none;border-bottom:1px solid #111;}
.card{width:92%;margin:auto;margin-top:15px;background:#050505;border-radius:24px;border:1px solid #111;padding:12px 16px;}
.title{color:#ff0000;font-size:14px;letter-spacing:3px;margin-bottom:16px;font-weight:700;}
.item{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid #111;}
.item:last-child{border-bottom:none;}
.switch{position:relative;width:60px;height:32px;background:#1b1b1b;border-radius:100px;}
.circle{position:absolute;width:24px;height:24px;border-radius:50%;top:4px;transition:0.3s;}
.on{right:4px;background:#ff0000;}
.off{left:4px;background:#666;}
button{width:100%;height:45px;border:none;border-radius:14px;background:#ff0000;color:#fff;font-size:15px;font-weight:700;}
input{width:100%;height:45px;background:#0f0f0f;border:1px solid #222;border-radius:14px;color:#fff;padding-left:15px;margin-bottom:12px;}
</style>
</head>
<body>
<div class="sidebar" id="sidebar">
<a href="/">• Berlim SYSTEM</a>
<a href="/connect">• connect</a>
<a href="/config">• config</a>
</div>
<div class="top">
<div class="left">
<div class="menu" onclick="menuOpen()">☰</div>
<div class="logo">BERLIM <br><span>SYSTEM</span></div>
</div>
<div class="{{status_class}}">{{status_text}}</div>
</div>
{{conteudo|safe}}
<script>
function menuOpen(){
    let sidebar = document.getElementById("sidebar");
    sidebar.style.left = (sidebar.style.left == "0px") ? "-220px" : "0px";
}
</script>
</body>
</html>
"""

# =========================
# HOME
# =========================

@app.route("/")
def home():
    conteudo = """<div class="card"><div class="title">FUNCOES</div>"""
    for display_name, data in estado.items():
        classe = "on" if data["active"] else "off"
        conteudo += f"""
        <div class="item">
            <div>
                <h2>{display_name}</h2>
                <p>Injetar holograma</p>
            </div>
            <a href="/toggle/{display_name}">
                <div class="switch">
                    <div class="circle {classe}"></div>
                </div>
            </a>
        </div>
        """
    conteudo += "</div>"
    return render_template_string(
        HTML,
        conteudo=conteudo,
        status_text="● Online" if adb_online else "● Offline",
        status_class="online_on" if adb_online else "online_off"
    )

# =========================
# TOGGLE ARQUIVO (LÓGICA CORRIGIDA)
# =========================

@app.route("/toggle/<display_name>")
def toggle(display_name):
    global adb_online
    if display_name not in estado or not adb_online:
        return redirect("/")

    file_data = estado[display_name]
    filename = file_data["filename"]
    is_active = file_data["active"]

    estado[display_name]["active"] = not is_active

    if not is_active:  # ATIVAR (Modificado entra, Original vai para Music)
        # 1. Move o original do FF Max para Music
        cmd_move_original = f'adb shell "mv {DESTINO_FFMAX}/{filename} {PASTA_ORIGINAL}/{filename}"'
        subprocess.getoutput(cmd_move_original)

        # 2. Move o modificado de Download para o FF Max
        cmd_move_mod = f'adb shell "mv {PASTA_MODIFICADO}/{filename} {DESTINO_FFMAX}/{filename}"'
        subprocess.getoutput(cmd_move_mod)

    else:  # DESATIVAR (Original volta, Modificado vai para Download)
        # 1. Move o modificado do FF Max de volta para Download
        cmd_restore_mod = f'adb shell "mv {DESTINO_FFMAX}/{filename} {PASTA_MODIFICADO}/{filename}"'
        subprocess.getoutput(cmd_restore_mod)

        # 2. Move o original de Music de volta para o FF Max
        cmd_restore_original = f'adb shell "mv {PASTA_ORIGINAL}/{filename} {DESTINO_FFMAX}/{filename}"'
        subprocess.getoutput(cmd_restore_original)

    return redirect("/")

# =========================
# CONNECT ADB
# =========================

@app.route("/connect", methods=["GET", "POST"])
def connect():
    global adb_online
    if request.method == "POST":
        porta_pair = request.form.get("porta_pair")
        codigo = request.form.get("codigo")
        porta_connect = request.form.get("porta_connect")
        ip = get_local_ip()
        subprocess.getoutput(f'adb pair {ip}:{porta_pair} {codigo}')
        connect_res = subprocess.getoutput(f'adb connect {ip}:{porta_connect}')
        adb_online = "connected" in connect_res.lower() or "already connected" in connect_res.lower()
        return redirect("/")

    conteudo = """
    <div class="card">
        <div class="title">CONNECT</div>
        <form method="POST">
            <input name="porta_pair" placeholder="PORTA PAREAMENTO">
            <input name="codigo" placeholder="CODIGO">
            <input name="porta_connect" placeholder="PORTA CONEXAO">
            <button type="submit">CONECTAR</button>
        </form>
    </div>
    """
    return render_template_string(HTML, conteudo=conteudo, 
                                 status_text="● Online" if adb_online else "● Offline",
                                 status_class="online_on" if adb_online else "online_off")

# =========================
# CONFIG
# =========================

@app.route("/config")
def config():
    conteudo = """<div class="card"><div class="title">INFORMACOES</div><div style="font-size:14px;">TEMPO: 999 dias<br><br>DEV: BERLIM SYSTEM</div></div>"""
    return render_template_string(HTML, conteudo=conteudo, 
                                 status_text="● Online" if adb_online else "● Offline",
                                 status_class="online_on" if adb_online else "online_off")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081)
