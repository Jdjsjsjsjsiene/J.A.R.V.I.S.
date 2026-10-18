# 1. Standart kütüphaneler
import os
import re
import time
import ctypes
import datetime
import subprocess
import win32con
import win32process
import threading
import winsound
import sys
import urllib.request
import urllib.parse

# 2. 3. parti kütüphaneler
import psutil
import queue
import pyttsx3
import pyperclip
import requests
import wikipedia
import webbrowser
import serial
import speech_recognition as sr
import speedtest
import json
import base64
import hashlib
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    Fernet = None
import socket
import struct
import ipaddress
try:
    import qrcode
    from PIL import Image, ImageTk
    HAS_QR = True
except:
    HAS_QR = False
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    HAS_EMAIL = True
except:
    HAS_EMAIL = True  # smtplib standart kütüphane
try:
    import whois
    HAS_WHOIS = True
except:
    HAS_WHOIS = False
from flask import Flask, request, jsonify, render_template_string
# 3. GUI kütüphaneleri
import tkinter as tk
from tkinter import ttk, messagebox

# ── Paramiko (SSH) ──
try:
    import paramiko
    HAS_SSH = True
except ImportError:
    HAS_SSH = False

# ── Google Gemini ──
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

from flags import StegoApp

ESP_IP = "192.168.1.106"

# =========================
# CİHAZ TANIMI (Entegrasyon)
# =========================
CIHAZLAR = {
    "J.A.R.V.I.S_Watch_W1": {
        "tip": "watch", "ip": "192.168.1.101",
        "mac": "AA:BB:CC:DD:EE:01", "isim": "J.A.R.V.I.S Watch W1",
    },
    "J.A.R.V.I.S_TV": {
        "tip": "samsung_tv", "ip": "192.168.1.130",
        "mac": "AA:BB:CC:DD:EE:02", "port": 8001, "isim": "Samsung LED 49",
    },
    "xiaomi_13pro": {
        "tip": "telefon", "ip": "192.168.1.101",
        "mac": "88:6C:60:18:D8:8C", "isim": "Xiaomi Redmi Note 13 Pro",
    },
    "xiaomi_12pro": {
        "tip": "telefon", "ip": "192.168.1.141",
        "mac": "AA:BB:CC:DD:EE:04", "isim": "Xiaomi Redmi Note 12 Pro",
    },
    "oppo_a3": {
        "tip": "telefon", "ip": "192.168.1.142",
        "mac": "AA:BB:CC:DD:EE:05", "isim": "Oppo A3",
    },
    "ana_sistem": {
        "tip": "windows_pc", "ip": "192.168.1.100",
        "isim": "Ana Sistem", "ssh": False,
    },
    "eray_laptop": {
        "tip": "windows_pc", "ip": "192.168.1.150",
        "mac": "AA:BB:CC:DD:EE:06", "isim": "Eray Laptop",
        "ssh_kullanici": "Eray", "ssh_sifre": "sifre", "ssh": True,
    },
    "kali": {
        "tip": "linux_pc", "ip": "192.168.1.160",
        "isim": "Kali Linux", "ssh_kullanici": "kali",
        "ssh_sifre": "kali", "ssh": True,
    },
    "deney_win11": {
        "tip": "windows_pc", "ip": "192.168.1.161",
        "mac": "AA:BB:CC:DD:EE:07", "isim": "Deney Win11",
        "ssh_kullanici": "kullanici", "ssh_sifre": "sifre", "ssh": True,
    },
    "esp_fi": {
        "tip": "esp32", "ip": "192.168.1.106",
        "isim": "J.A.R.V.I.S F.I (ESP Web)",
    },
}

TELEGRAM = {
    "bot_token": "BURAYA_TOKEN",
    "chat_id":   "BURAYA_CHAT_ID",
    "aktif":     False,
}

FLASK_PORT  = 5000
TIP_IKON    = {
    "watch": "⌚", "samsung_tv": "📺", "telefon": "📱",
    "windows_pc": "💻", "linux_pc": "🐧", "esp32": "⚡",
}

_cihaz_durum = {k: None for k in CIHAZLAR}
_ping_lock   = threading.Lock()


def ping_cihaz(ip, timeout_ms=600) -> bool:
    try:
        r = subprocess.run(["ping", "-n", "1", "-w", str(timeout_ms), ip],
                           capture_output=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def _telegram_async(mesaj, emoji="🤖"):
    def _gonder():
        if not TELEGRAM["aktif"]: return
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM['bot_token']}/sendMessage",
                json={"chat_id": TELEGRAM["chat_id"],
                      "text": f"{emoji} *J.A.R.V.I.S*\n{mesaj}",
                      "parse_mode": "Markdown"}, timeout=5)
        except Exception:
            pass
    threading.Thread(target=_gonder, daemon=True).start()


def _ping_worker_fn(key, cihaz):
    onceki = _cihaz_durum.get(key)
    simdi  = ping_cihaz(cihaz["ip"])
    with _ping_lock:
        _cihaz_durum[key] = simdi
    if onceki is not None and onceki != simdi:
        _telegram_async(
            f"{'✅' if simdi else '❌'} {cihaz['isim']} {'aga baglandi' if simdi else 'agdan dustu'}"
        )


def tum_cihazlari_tara():
    threads = [threading.Thread(target=_ping_worker_fn, args=(k, c), daemon=True)
               for k, c in CIHAZLAR.items()]
    for t in threads: t.start()
    for t in threads: t.join(timeout=4)


def surekli_izle(aralik_sn=30):
    def _dongu():
        while True:
            tum_cihazlari_tara()
            try: yabanci_cihaz_tara()
            except Exception: pass
            time.sleep(aralik_sn)
    threading.Thread(target=_dongu, daemon=True).start()


def _tv_ip():   return CIHAZLAR["J.A.R.V.I.S_TV"]["ip"]
def _tv_mac():  return CIHAZLAR["J.A.R.V.I.S_TV"]["mac"]
def _tv_port(): return CIHAZLAR["J.A.R.V.I.S_TV"]["port"]


def tv_wake_on_lan() -> bool:
    mac = _tv_mac().replace(":", "").replace("-", "").upper()
    if len(mac) != 12: return False
    paket = bytes.fromhex("FF" * 6 + mac * 16)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(paket, ("<broadcast>", 9))
        return True
    except Exception:
        return False


def tv_ac_mi() -> bool:
    try:
        r = requests.get(f"http://{_tv_ip()}:{_tv_port()}/api/v2/", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def samsung_tv_komut(tus_kodu: str) -> bool:
    try:
        r = requests.post(f"http://{_tv_ip()}:{_tv_port()}/api/v2/keys/{tus_kodu}", timeout=3)
        return r.status_code in (200, 204)
    except Exception:
        return False


def tv_uygulama_ac(uygulama_id: str) -> bool:
    try:
        r = requests.post(f"http://{_tv_ip()}:{_tv_port()}/api/v2/applications/{uygulama_id}", timeout=5)
        return r.status_code in (200, 201)
    except Exception:
        return False


def tv_gui():
    win = tk.Toplevel()
    win.title("Samsung TV Uzaktan Kumanda")
    win.geometry("320x530")
    win.configure(bg="#0d1117")
    win.resizable(False, False)

    def tv_btn(parent, text, komut, r, c):
        tk.Button(parent, text=text, font=("Consolas", 10, "bold"),
                  bg="#1f2937", fg="cyan", activebackground="#374151",
                  width=7, height=2, relief="flat",
                  command=lambda: threading.Thread(
                      target=samsung_tv_komut, args=(komut,), daemon=True).start()
                  ).grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

    tk.Label(win, text="TV Uzaktan Kumanda", font=("Orbitron", 12, "bold"),
             fg="cyan", bg="#0d1117").pack(pady=8)
    durum_lbl = tk.Label(win, text="Kontrol ediliyor...", font=("Consolas", 10),
                         fg="white", bg="#0d1117")
    durum_lbl.pack()

    def durum_guncelle():
        acik = tv_ac_mi()
        durum_lbl.config(text="TV Acik" if acik else "TV Kapali",
                         fg="lime" if acik else "red")
        win.after(5000, durum_guncelle)
    durum_guncelle()

    frame = tk.Frame(win, bg="#0d1117"); frame.pack(padx=10, pady=5)
    tv_btn(frame, "Guc",    "KEY_POWER",   0, 1)
    tv_btn(frame, "Mute",   "KEY_MUTE",    0, 2)
    tv_btn(frame, "Kaynak", "KEY_SOURCE",  0, 0)
    tv_btn(frame, "VOL+",   "KEY_VOLUP",   1, 0)
    tv_btn(frame, "Yukari", "KEY_UP",      1, 1)
    tv_btn(frame, "CH+",    "KEY_CHUP",    1, 2)
    tv_btn(frame, "Sol",    "KEY_LEFT",    2, 0)
    tv_btn(frame, "OK",     "KEY_ENTER",   2, 1)
    tv_btn(frame, "Sag",    "KEY_RIGHT",   2, 2)
    tv_btn(frame, "VOL-",   "KEY_VOLDOWN", 3, 0)
    tv_btn(frame, "Asagi",  "KEY_DOWN",    3, 1)
    tv_btn(frame, "CH-",    "KEY_CHDOWN",  3, 2)
    tv_btn(frame, "Home",   "KEY_HOME",    4, 0)
    tv_btn(frame, "Geri",   "KEY_RETURN",  4, 1)
    tv_btn(frame, "Cikis",  "KEY_EXIT",    4, 2)

    tk.Label(win, text="Uygulamalar", fg="#4b5563", bg="#0d1117",
             font=("Consolas", 9)).pack(pady=(6, 0))
    app_frame = tk.Frame(win, bg="#0d1117"); app_frame.pack(pady=4)
    for i, (ad, uid) in enumerate([("YouTube","111299001912"),("Netflix","11812021"),
                                    ("Spotify","3201606009684"),("Prime","3201910019365")]):
        tk.Button(app_frame, text=ad, font=("Consolas", 9), bg="#1f2937", fg="cyan",
                  relief="flat", padx=6,
                  command=lambda u=uid: threading.Thread(
                      target=tv_uygulama_ac, args=(u,), daemon=True).start()
                  ).grid(row=0, column=i, padx=2, pady=2)

    tk.Button(win, text="Wake-on-LAN ile AC", font=("Consolas", 10),
              bg="#1f2937", fg="lime", relief="flat",
              command=lambda: threading.Thread(target=tv_wake_on_lan, daemon=True).start()
              ).pack(pady=6)


def ssh_komut_gonder(cihaz_key: str, komut: str):
    if not HAS_SSH: return False, "paramiko kurulu degil: pip install paramiko"
    cihaz = CIHAZLAR.get(cihaz_key)
    if not cihaz or not cihaz.get("ssh"): return False, "SSH tanimlanmamis"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(cihaz["ip"], username=cihaz.get("ssh_kullanici",""),
                    password=cihaz.get("ssh_sifre",""), timeout=5)
        _, stdout, stderr = ssh.exec_command(komut)
        cikti = stdout.read().decode("utf-8", errors="ignore")
        hata  = stderr.read().decode("utf-8", errors="ignore")
        ssh.close()
        return True, cikti or hata
    except Exception as e:
        return False, str(e)


def uzak_pc_gui():
    win = tk.Toplevel()
    win.title("Uzak Bilgisayar Kontrolu")
    win.geometry("600x500")
    win.configure(bg="#0d1117")
    tk.Label(win, text="Uzak Bilgisayar Kontrolu",
             font=("Orbitron", 13, "bold"), fg="cyan", bg="#0d1117").pack(pady=10)

    ssh_cihazlar = {k: v for k, v in CIHAZLAR.items() if v.get("ssh")}
    secim_var = tk.StringVar(value=list(ssh_cihazlar.keys())[0] if ssh_cihazlar else "")

    secim_frame = tk.Frame(win, bg="#0d1117"); secim_frame.pack(pady=5)
    tk.Label(secim_frame, text="Cihaz:", bg="#0d1117", fg="white").pack(side="left")
    for key, cihaz in ssh_cihazlar.items():
        tk.Radiobutton(secim_frame, text=cihaz["isim"], variable=secim_var, value=key,
                       bg="#0d1117", fg="cyan", selectcolor="#1f2937").pack(side="left", padx=5)

    tk.Label(win, text="Komut:", bg="#0d1117", fg="white").pack()
    komut_entry = tk.Entry(win, width=60, bg="#161b22", fg="white", font=("Consolas", 11))
    komut_entry.pack(pady=5)
    cikti_box = tk.Text(win, height=15, bg="#161b22", fg="#00ff00", font=("Consolas", 10))
    cikti_box.pack(fill="both", expand=True, padx=15, pady=5)

    def gonder():
        key = secim_var.get(); cmd = komut_entry.get().strip()
        if not cmd: return
        cikti_box.insert("end", f"\n$ {cmd}\n")
        def _run():
            ok, cikti = ssh_komut_gonder(key, cmd)
            cikti_box.insert("end", cikti + ("\n[OK]\n" if ok else "\n[HATA]\n"))
            cikti_box.see("end")
        threading.Thread(target=_run, daemon=True).start()
        komut_entry.delete(0, "end")

    komut_entry.bind("<Return>", lambda e: gonder())
    btn_frame = tk.Frame(win, bg="#0d1117"); btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Gonder", command=gonder,
              bg="#1f2937", fg="cyan", font=("Consolas", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Kapat",
              command=lambda: ssh_komut_gonder(secim_var.get(), "shutdown /s /t 10"),
              bg="#1f2937", fg="red", font=("Consolas", 11)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Yeniden Baslat",
              command=lambda: ssh_komut_gonder(secim_var.get(), "shutdown /r /t 10"),
              bg="#1f2937", fg="orange", font=("Consolas", 11)).pack(side="left", padx=5)


# ── Flask telefon sunucu ──
_flask_sunucu_aktif = False

TELEFON_KONTROL_HTML = """<!DOCTYPE html><html lang="tr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>JARVIS Kontrol</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{background:#0d1117;color:#fff;font-family:'Segoe UI',sans-serif}
h1{text-align:center;color:cyan;padding:20px;font-size:1.4rem;letter-spacing:3px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:16px}
.btn{background:#1f2937;color:cyan;border:1px solid #374151;border-radius:12px;padding:18px 8px;font-size:1rem;cursor:pointer;text-align:center;transition:.2s}
.btn:active{background:#374151;transform:scale(.96)}.full{grid-column:span 2}
.log{margin:16px;background:#161b22;border-radius:8px;padding:12px;font-size:.85rem;color:#9ca3af;height:120px;overflow-y:auto;white-space:pre-wrap}
input{width:100%;padding:12px;border-radius:8px;border:1px solid #374151;background:#161b22;color:#fff;font-size:1rem;margin-bottom:8px}
.status{text-align:center;font-size:.8rem;color:#6b7280;padding:8px}</style></head>
<body><h1>J.A.R.V.I.S</h1>
<div class="grid">
<button class="btn" onclick="cmd('salon_lamba_ac')">Salon Ac</button>
<button class="btn" onclick="cmd('salon_lamba_kapat')">Salon Kapat</button>
<button class="btn" onclick="cmd('tv_ac')">TV Ac</button>
<button class="btn" onclick="cmd('tv_kapat')">TV Kapat</button>
<button class="btn" onclick="cmd('tum_lambalar_ac')">Tum Isiklar Ac</button>
<button class="btn" onclick="cmd('tum_lambalar_kapat')">Tum Isiklar Kapat</button>
<button class="btn" onclick="cmd('muzik_durdur')">Muzik Duraklat</button>
<button class="btn" onclick="cmd('sonraki_sarki')">Sonraki Sarki</button>
<button class="btn" onclick="cmd('bilgisayar_kilitle')">Ekran Kilitle</button>
<button class="btn" onclick="cmd('hava_durumu')">Hava Durumu</button></div>
<div style="padding:0 16px">
<input id="serbest" placeholder="Serbest komut..." onkeydown="if(event.key==='Enter')serbest_gonder()">
<button class="btn full" onclick="serbest_gonder()" style="width:100%;margin-bottom:8px">Komutu Gonder</button></div>
<div class="log" id="log">Hazir...\\n</div>
<div class="status" id="status">Bagli</div>
<script>function log(t){var e=document.getElementById('log');e.textContent+=t+'\\n';e.scrollTop=e.scrollHeight}
function cmd(k){fetch('/komut',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({komut:k})}).then(r=>r.json()).then(d=>log(d.mesaj)).catch(()=>log('Hata'))}
function serbest_gonder(){var k=document.getElementById('serbest').value.trim();if(!k)return;cmd(k);document.getElementById('serbest').value=''}
setInterval(()=>{fetch('/durum').then(r=>r.json()).then(d=>{document.getElementById('status').textContent='Bagli | '+d.saat}).catch(()=>{document.getElementById('status').textContent='Baglanti yok'})},3000);</script></body></html>"""


def flask_sunucu_baslat():
    global _flask_sunucu_aktif
    if _flask_sunucu_aktif: return
    app_flask = Flask(__name__ + "_tel")
    import logging; logging.getLogger("werkzeug").setLevel(logging.ERROR)

    @app_flask.route("/")
    def _index(): return render_template_string(TELEFON_KONTROL_HTML)

    @app_flask.route("/durum")
    def _durum():
        return jsonify({"saat": time.strftime("%H:%M:%S"),
                        "cihazlar": {k: _cihaz_durum.get(k) for k in CIHAZLAR}})

    @app_flask.route("/komut", methods=["POST"])
    def _komut():
        data = request.get_json(force=True)
        komut = data.get("komut", "").strip().lower()
        mapping = {
            "salon_lamba_ac":     lambda: control_relay(1, "on"),
            "salon_lamba_kapat":  lambda: control_relay(1, "off"),
            "tum_lambalar_ac":    lambda: [control_relay(i, "on") for i in range(1, 5)],
            "tum_lambalar_kapat": lambda: [control_relay(i, "off") for i in range(1, 5)],
            "tv_ac":              lambda: tv_wake_on_lan(),
            "tv_kapat":           lambda: samsung_tv_komut("KEY_POWER"),
            "muzik_durdur":       lambda: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0),
            "sonraki_sarki":      lambda: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0),
            "bilgisayar_kilitle": lambda: ctypes.windll.user32.LockWorkStation(),
        }
        if komut in mapping:
            try: mapping[komut](); return jsonify({"mesaj": f"'{komut}' calistirildi"})
            except Exception as e: return jsonify({"mesaj": f"Hata: {e}"})
        return jsonify({"mesaj": f"Komut iletildi: {komut}"})

    threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=FLASK_PORT, debug=False),
                     daemon=True).start()
    _flask_sunucu_aktif = True


# ── Gemini AI ──
GEMINI_API_KEY = "AIzaSyA8DvD91cAjgTiYVSbV_YGseM-mEvcQcmM"
_gemini_model  = None
_gemini_gecmis = []
GEMINI_SISTEM  = (
    "Sen J.A.R.V.I.S adında bir yapay zeka ev asistanısın. "
    "Türkçe konuş, kısa ve net cevaplar ver. "
    "Ev otomasyonu, ağ yönetimi ve genel sorularda yardımcı ol."
)

def gemini_baslat():
    global _gemini_model
    if not HAS_GEMINI: return False, "google-generativeai kurulu değil: pip install google-generativeai"
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(model_name="gemini-2.0-flash",
                                               system_instruction=GEMINI_SISTEM)
        return True, "Gemini hazır."
    except Exception as e: return False, str(e)

def gemini_sor(soru: str, _deneme: int = 0) -> str:
    global _gemini_model, _gemini_gecmis
    if _gemini_model is None:
        ok, msg = gemini_baslat()
        if not ok: return f"[Gemini] {msg}"
    if _deneme == 0:
        _gemini_gecmis.append({"role": "user", "parts": [soru]})
    try:
        chat  = _gemini_model.start_chat(history=_gemini_gecmis[:-1])
        yanit = chat.send_message(soru)
        metin = yanit.text.strip()
        _gemini_gecmis.append({"role": "model", "parts": [metin]})
        if len(_gemini_gecmis) > 40: _gemini_gecmis = _gemini_gecmis[-40:]
        return metin
    except Exception as e:
        hata = str(e)
        if "429" in hata or "quota" in hata.lower():
            bekleme = 65
            m = re.search(r"retry.*?(\d+)\s*second", hata, re.IGNORECASE)
            if m: bekleme = int(m.group(1)) + 2
            if _deneme < 2: time.sleep(bekleme); return gemini_sor(soru, _deneme + 1)
            return "[Gemini] Kota limiti. Birkaç dakika bekle."
        return f"[Gemini Hata] {hata}"

def gemini_gui():
    win = tk.Toplevel(); win.title("Gemini AI Sohbet"); win.geometry("680x540"); win.configure(bg="#0d1117")
    tk.Label(win, text="Gemini AI — J.A.R.V.I.S", font=("Orbitron", 13, "bold"), fg="cyan", bg="#0d1117").pack(pady=8)
    durum_lbl = tk.Label(win, text="", font=("Consolas", 9), bg="#0d1117"); durum_lbl.pack()
    if not HAS_GEMINI:
        durum_lbl.config(text="pip install google-generativeai", fg="red")
    else:
        durum_lbl.config(text="Gemini hazir", fg="lime")

    chat_frame = tk.Frame(win, bg="#0d1117"); chat_frame.pack(fill="both", expand=True, padx=12, pady=4)
    sb = tk.Scrollbar(chat_frame); sb.pack(side="right", fill="y")
    sohbet_box = tk.Text(chat_frame, bg="#0d1117", fg="white", font=("Consolas", 11),
                         wrap="word", yscrollcommand=sb.set, state="disabled")
    sohbet_box.pack(fill="both", expand=True); sb.config(command=sohbet_box.yview)
    sohbet_box.tag_config("kullanici", foreground="cyan")
    sohbet_box.tag_config("jarvis",    foreground="#a3e635")
    sohbet_box.tag_config("hata",      foreground="#f87171")
    sohbet_box.tag_config("dim",       foreground="#4b5563")

    def sohbet_yaz(metin, tag="jarvis"):
        sohbet_box.config(state="normal"); sohbet_box.insert("end", metin+"\n", tag)
        sohbet_box.see("end"); sohbet_box.config(state="disabled")
    sohbet_yaz("J.A.R.V.I.S Gemini hazır.\n","dim")

    giris_frame = tk.Frame(win, bg="#0d1117"); giris_frame.pack(fill="x", padx=12, pady=6)
    giris = tk.Entry(giris_frame, bg="#1f2937", fg="white", font=("Consolas", 12),
                     relief="flat", insertbackground="cyan")
    giris.pack(side="left", fill="x", expand=True, ipady=6, padx=(0,6))
    gonder_btn = tk.Button(giris_frame, text="Gönder", bg="#1f2937", fg="cyan",
                           font=("Consolas", 11), relief="flat", padx=12)
    gonder_btn.pack(side="right")
    tk.Button(win, text="Geçmişi Temizle", bg="#0d1117", fg="#4b5563", font=("Consolas",9),
              relief="flat",
              command=lambda: (_gemini_gecmis.clear(),
                               sohbet_box.config(state="normal"),
                               sohbet_box.delete("1.0","end"),
                               sohbet_box.config(state="disabled"),
                               sohbet_yaz("Gecmis temizlendi.\n","dim"))).pack(pady=2)

    def gonder(event=None):
        soru = giris.get().strip()
        if not soru: return
        giris.delete(0,"end"); sohbet_yaz(f"Sen: {soru}","kullanici")
        gonder_btn.config(state="disabled", text="⏳")
        def _sor():
            yanit = gemini_sor(soru)
            win.after(0, lambda: (
                sohbet_yaz(f"J.A.R.V.I.S: {yanit}", "jarvis" if "[Gemini" not in yanit else "hata"),
                gonder_btn.config(state="normal", text="Gönder")))
        threading.Thread(target=_sor, daemon=True).start()
    giris.bind("<Return>", gonder); gonder_btn.config(command=gonder); giris.focus()


# ── Yabancı cihaz izleme ──
BILINEN_MACLER: set = set()

def _bilinen_macleri_yukle():
    for cihaz in CIHAZLAR.values():
        mac = cihaz.get("mac","")
        if mac: BILINEN_MACLER.add(mac.upper().replace("-",":"))

_bilinen_macleri_yukle()
_yabanci_uyari_log: list = []

def _arp_tablosunu_tara() -> list:
    cihazlar = []
    try:
        cikti = subprocess.check_output("arp -a", shell=True,
                                        stderr=subprocess.DEVNULL).decode("cp1254", errors="ignore")
        for satir in cikti.splitlines():
            parcalar = satir.split()
            if len(parcalar) >= 2:
                ip  = parcalar[0].strip()
                mac = parcalar[1].strip().upper().replace("-",":")
                if (re.match(r"^\d+\.\d+\.\d+\.\d+$", ip) and
                        re.match(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$", mac) and
                        not mac.startswith("FF:FF") and not mac.startswith("01:")):
                    cihazlar.append({"ip": ip, "mac": mac})
    except Exception: pass
    return cihazlar

def yabanci_cihaz_tara(speak_fn=None, write_fn=None):
    bulunanlar = _arp_tablosunu_tara()
    yeni = []
    for c in bulunanlar:
        if c["mac"] not in BILINEN_MACLER and not any(x["mac"]==c["mac"] for x in _yabanci_uyari_log):
            _yabanci_uyari_log.append({"mac":c["mac"],"ip":c["ip"],"zaman":time.strftime("%H:%M:%S")})
            yeni.append(c)
    for c in yeni:
        _telegram_async(f"UYARI: Bilinmeyen cihaz!\nIP: {c['ip']}\nMAC: {c['mac']}","🚨")
        if write_fn: write_fn(f"[AG UYARI] Yabancı: {c['ip']} / {c['mac']}")
        if speak_fn: speak_fn(f"Uyarı! Ağda bilinmeyen cihaz: {c['ip']}")
    return yeni

def yabanci_cihaz_gui():
    win = tk.Toplevel()
    win.title("Ag Guvenlik Izleme")
    win.geometry("680x540")
    win.configure(bg="#0d1117")

    tk.Label(win, text="Ağ Güvenlik İzleme",
             font=("Orbitron", 13, "bold"), fg="cyan", bg="#0d1117").pack(pady=8)

    # Üst bilgi satırı
    bilgi_frame = tk.Frame(win, bg="#0d1117")
    bilgi_frame.pack(fill="x", padx=12)
    bilinen_lbl = tk.Label(bilgi_frame, text=f"Bilinen MAC: {len(BILINEN_MACLER)}",
                           fg="#4b5563", bg="#0d1117", font=("Consolas", 9))
    bilinen_lbl.pack(side="left")
    secim_lbl = tk.Label(bilgi_frame, text="Seçmek için satıra tıklayın",
                         fg="#3a6175", bg="#0d1117", font=("Consolas", 8))
    secim_lbl.pack(side="right")

    # Log kutusu
    log_frame = tk.Frame(win, bg="#0d1117")
    log_frame.pack(fill="both", expand=True, padx=12, pady=6)
    log_sb = tk.Scrollbar(log_frame); log_sb.pack(side="right", fill="y")
    log_box = tk.Text(log_frame, bg="#0d1117", fg="white", font=("Consolas", 10),
                      yscrollcommand=log_sb.set, state="disabled", cursor="hand2")
    log_box.pack(fill="both", expand=True)
    log_sb.config(command=log_box.yview)

    log_box.tag_config("uyari",   foreground="#f87171")
    log_box.tag_config("secili",  foreground="#0d1117", background="#f87171")
    log_box.tag_config("temiz",   foreground="#4ade80")
    log_box.tag_config("baslik",  foreground="cyan")
    log_box.tag_config("dim",     foreground="#4b5563")

    # Seçili MAC takibi
    _secili = {"mac": None, "ip": None}

    def gecmisi_goster():
        _secili["mac"] = None
        _secili["ip"]  = None
        ekle_btn.config(state="disabled", text="Güvenilir Ekle  ＋", fg="#3a6175")
        bilinen_lbl.config(text=f"Bilinen MAC: {len(BILINEN_MACLER)}")

        log_box.config(state="normal")
        log_box.delete("1.0", "end")

        log_box.insert("end", "=== Ağdaki Cihazlar ===\n", "baslik")
        bulunanlar = _arp_tablosunu_tara()

        for c in bulunanlar:
            bilinen = c["mac"] in BILINEN_MACLER
            tag     = "temiz" if bilinen else "uyari"
            durum   = "BİLİNEN  " if bilinen else "YABANCI !"
            satir   = f"  {durum}  {c['ip']:<18}  {c['mac']}\n"
            log_box.insert("end", satir, tag)

        if _yabanci_uyari_log:
            log_box.insert("end", "\n=== Uyarı Geçmişi ===\n", "baslik")
            for u in _yabanci_uyari_log:
                log_box.insert("end",
                    f"  {u['zaman']}  {u['ip']:<18}  {u['mac']}\n", "uyari")

        log_box.config(state="disabled")

    # Satıra tıklayınca MAC seç
    def _satir_sec(event):
        log_box.config(state="normal")
        # Tıklanan satırı al
        idx   = log_box.index(f"@{event.x},{event.y}")
        line  = int(idx.split(".")[0])
        satir = log_box.get(f"{line}.0", f"{line}.end").strip()

        # MAC formatı: XX:XX:XX:XX:XX:XX
        m = re.search(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", satir)
        if not m:
            log_box.config(state="disabled")
            return

        mac = m.group(0).upper()

        # Zaten bilinen MAC — seçilemez
        if mac in BILINEN_MACLER:
            log_box.config(state="disabled")
            return

        # IP'yi de oku
        ip_m = re.search(r"\d+\.\d+\.\d+\.\d+", satir)
        ip   = ip_m.group(0) if ip_m else "?"

        _secili["mac"] = mac
        _secili["ip"]  = ip
        ekle_btn.config(state="normal",
                        text=f"Güvenilir Ekle  ＋  {mac}",
                        fg="#00ff88")
        log_box.config(state="disabled")

    log_box.bind("<Button-1>", _satir_sec)

    # Alt buton çubuğu
    btn_frame = tk.Frame(win, bg="#0d1117")
    btn_frame.pack(fill="x", padx=12, pady=(0, 10))

    # Güvenilir Ekle
    def _guvenliye_ekle():
        mac = _secili.get("mac")
        if not mac:
            return
        BILINEN_MACLER.add(mac)
        # Uyarı geçmişinden de temizle
        _yabanci_uyari_log[:] = [x for x in _yabanci_uyari_log if x["mac"] != mac]
        gecmisi_goster()

    ekle_btn = tk.Button(
        btn_frame, text="Güvenilir Ekle  ＋",
        font=("Consolas", 10, "bold"),
        fg="#3a6175", bg="#0d1117",
        activeforeground="white", activebackground="#003a1a",
        relief="flat", bd=0, cursor="hand2",
        state="disabled", padx=10, pady=4,
        command=_guvenliye_ekle
    )
    ekle_btn.pack(side="left", padx=(0, 8))

    tk.Button(
        btn_frame, text="Şimdi Tara",
        font=("Consolas", 10), fg="cyan", bg="#1f2937",
        relief="flat", cursor="hand2", padx=10, pady=4,
        command=lambda: threading.Thread(
            target=lambda: win.after(0, gecmisi_goster), daemon=True).start()
    ).pack(side="left", padx=4)

    tk.Button(
        btn_frame, text="Geçmişi Temizle",
        font=("Consolas", 10), fg="#f87171", bg="#1f2937",
        relief="flat", cursor="hand2", padx=10, pady=4,
        command=lambda: (_yabanci_uyari_log.clear(), gecmisi_goster())
    ).pack(side="left", padx=4)

    # Güvenilir MAC listesi butonu
    def _goster_liste():
        lst_win = tk.Toplevel(win)
        lst_win.title("Güvenilir MAC Listesi")
        lst_win.geometry("480x400")
        lst_win.configure(bg="#0d1117")
        tk.Label(lst_win, text="Güvenilir MAC Adresleri",
                 font=("Consolas", 11, "bold"), fg="cyan", bg="#0d1117").pack(pady=8)
        frame = tk.Frame(lst_win, bg="#0d1117"); frame.pack(fill="both", expand=True, padx=10)
        sb = tk.Scrollbar(frame); sb.pack(side="right", fill="y")
        t  = tk.Text(frame, bg="#0d1117", fg="#4ade80", font=("Consolas", 10),
                     yscrollcommand=sb.set); t.pack(fill="both", expand=True)
        sb.config(command=t.yview)
        for mac in sorted(BILINEN_MACLER):
            t.insert("end", f"  {mac}\n")
        t.config(state="disabled")

        def _mac_sil():
            # Seçili satırdaki MAC'i sil
            try:
                idx  = t.index("insert")
                line = t.get(f"{idx.split('.')[0]}.0", f"{idx.split('.')[0]}.end").strip()
                m    = re.search(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", line)
                if m:
                    BILINEN_MACLER.discard(m.group(0).upper())
                    t.config(state="normal"); t.delete("1.0","end")
                    for mac in sorted(BILINEN_MACLER):
                        t.insert("end", f"  {mac}\n")
                    t.config(state="disabled")
                    gecmisi_goster()
            except Exception: pass

        tk.Button(lst_win, text="Seçili MAC'i Listeden Çıkar",
                  font=("Consolas", 9), fg="#f87171", bg="#1f2937",
                  relief="flat", cursor="hand2", padx=8, pady=4,
                  command=_mac_sil).pack(pady=8)

    tk.Button(
        btn_frame, text="Güvenilir Liste",
        font=("Consolas", 10), fg="#7fb3c8", bg="#1f2937",
        relief="flat", cursor="hand2", padx=10, pady=4,
        command=_goster_liste
    ).pack(side="right", padx=4)

    # İlk yükleme + otomatik yenile
    gecmisi_goster()

    def _oto():
        if win.winfo_exists():
            gecmisi_goster()
            win.after(15_000, _oto)
    win.after(15_000, _oto)


def paneli_guncelle_fn(device_conn_widget, root, aralik_ms=30_000):
    def _ciz():
        try:
            device_conn_widget.config(state="normal"); device_conn_widget.delete("1.0","end")
            for key, cihaz in CIHAZLAR.items():
                durum  = _cihaz_durum.get(key)
                t_ikon = TIP_IKON.get(cihaz["tip"],"?")
                if durum is True:   tag,nokta = "acik","● "
                elif durum is False:tag,nokta = "kapali","● "
                else:               tag,nokta = "bilinmiyor","○ "
                device_conn_widget.insert("end", nokta, tag)
                device_conn_widget.insert("end", f"{t_ikon} {cihaz['isim']}\n","isim_satir")
                device_conn_widget.insert("end", f"   {cihaz['ip']}\n","ip_satir")
            device_conn_widget.config(state="disabled")
        except Exception: pass
        root.after(aralik_ms, _guncelle_ve_ciz)

    def _guncelle_ve_ciz():
        threading.Thread(
            target=lambda: (tum_cihazlari_tara(), root.after(0,_ciz)), daemon=True
        ).start()
    root.after(3000, _guncelle_ve_ciz)

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# =========================
# ANA PENCERE
# =========================
windows = tk.Tk()
windows.title("J.A.R.V.I.S J4(Beta)")
windows.state("zoomed")   # FULL SCREEN
windows.configure(bg="#0d1117")

# =========================
# ANA FRAME
# =========================
main_frame = tk.Frame(windows, bg="#0d1117")
main_frame.pack(fill="both", expand=True)

# =========================
# SOL PANEL
# =========================
left_panel = tk.Frame(main_frame, bg="#111827", width=300)
left_panel.pack(side="left", fill="y")

lbl_features = tk.Label(
    left_panel,
    text="ÖZELLİKLER",
    font=("Consolas", 10, "bold"),
    fg="cyan",
    bg="#111827"
)
lbl_features.pack(pady=(10, 4))

features_box = tk.Text(
    left_panel,
    bg="#111827",
    fg="white",
    font=("Consolas", 9),
    width=30,
    bd=0,
    relief="flat",
    cursor="arrow",
)
features_box.pack(fill="both", expand=True, padx=6, pady=(0, 6))

# Renk tag'leri
features_box.tag_config("cat",  foreground="cyan",    font=("Consolas", 8, "bold"))
features_box.tag_config("sep",  foreground="#1a2a3a")
features_box.tag_config("item", foreground="#7fb3c8",  font=("Consolas", 9))
features_box.tag_config("dot",  foreground="#3a6175")

# Kategorili özellik listesi
features_data = [
    ("MODLAR",        ["Stüdyo Aç/Kapat", "Odak Aç/Kapat"]),
    ("ESP / RÖLE",    ["ESP Web", "Röle 1-4 Aç/Kapat"]),
    ("GÜVENLİK",      ["Turk Hack Team", "RAT Kontrol", "Oracle VM", "Morse (Beta)", "Sezar Şifreleme", "Github"]),
    ("GELİŞTİRME",    ["VS Code", "VS 2022", "Cisco Packet Tracer", "Cursor"]),
    ("AI / ARAÇLAR",  ["ChatGPT", "Copilot", "Gemini AI", "Tinkercad", "Canva", "Pivot Animator"]),
    ("FİNANS",        ["Trading View", "Binance TR", "Shopify"]),
    ("EĞİTİM",        ["Eba", "Duolingo", "Çeviri"]),
    ("WEB / SOSYAL",  ["Google", "YouTube", "Wikipedia", "Instagram", "WhatsApp", "Telegram", "LinkedIn", "Gmail"]),
    ("MEDYA",         ["Müzik Listesi", "Oynat/Durdur", "Sonraki/Önceki", "YT Kanal"]),
    ("İLETİŞİM",      ["WhatsApp Mesaj", "E-posta", "QR Kod", "Şifre Yöneticisi"]),
    ("AĞ",            ["Wi-Fi Aç/Kapat", "Ağ Haritası", "Bant Genişliği", "MAC Arama", "IP Konum", "Domain/Whois"]),
    ("CİHAZ",         ["Samsung TV", "Uzak PC (SSH)", "Telefon Sunucu", "Ağ Güvenlik"]),
    ("SİSTEM",        ["CMD", "Yeniden Başlat", "Kapat", "Ekran Kilitle", "Ses", "Parlaklık"]),
    ("ZAMAN",         ["Saat", "Tarih", "Alarm", "Kronometre"]),
    ("ARAÇLAR",       ["Hesap Makinesi", "Not Defteri", "Kamera/Mikrofon", "Görüntü Analizi", "Ses Transkr."]),
    ("YÖNETİM",       ["Denetim Masası", "Dosya Gezgini", "Ayarlar"]),
]

for cat, items in features_data:
    features_box.insert("end", f"\n  {cat}\n", "cat")
    features_box.insert("end", "  " + "─" * 22 + "\n", "sep")
    for item in items:
        features_box.insert("end", "  ◦ ", "dot")
        features_box.insert("end", f"{item}\n", "item")

features_box.config(state="disabled")

# =========================
# ESP RÖLE KONTROL PANELİ
# =========================
relay_title = tk.Label(
    left_panel,
    text=f"ESP RÖLE  {ESP_IP}",
    font=("Consolas", 9, "bold"),
    fg="cyan",
    bg="#111827"
)
relay_title.pack(pady=(6, 2))

relay_frame = tk.Frame(left_panel, bg="#111827")
relay_frame.pack(fill="x", padx=10, pady=(0, 8))

_relay_dots = {}

def _relay_btn_click(num, state):
    _relay_dots[num].config(fg="#00ff88" if state == "on" else "#ff3355")
    threading.Thread(target=control_relay, args=(num, state), daemon=True).start()

for i in range(1, 5):
    row = tk.Frame(relay_frame, bg="#111827")
    row.pack(fill="x", pady=4)

    # Röle etiketi — sol
    tk.Label(row, text=f"Röle {i}", font=("Consolas", 10),
             fg="#7fb3c8", bg="#111827", width=7,
             anchor="w").pack(side="left")

    # Durum noktası — orta
    dot = tk.Label(row, text="●", font=("Consolas", 10),
                   fg="#3a6175", bg="#111827")
    dot.pack(side="left", padx=(4, 0))
    _relay_dots[i] = dot

    # KAPAT — kırmızı, sağda
    tk.Button(
        row, text="KAPAT",
        font=("Consolas", 9, "bold"),
        fg="#ff3355", bg="#111827",
        activeforeground="white", activebackground="#3a0010",
        relief="flat", bd=0, cursor="hand2", padx=4, pady=1,
        command=lambda n=i: _relay_btn_click(n, "off")
    ).pack(side="right", padx=(2, 0))

    # AÇ — yeşil, sağda (KAPAT'ın solunda)
    tk.Button(
        row, text="AÇ",
        font=("Consolas", 9, "bold"),
        fg="#00ff88", bg="#111827",
        activeforeground="white", activebackground="#003a1a",
        relief="flat", bd=0, cursor="hand2", padx=4, pady=1,
        command=lambda n=i: _relay_btn_click(n, "on")
    ).pack(side="right", padx=(0, 6))

# Tümünü aç / tümünü kapat
all_frame = tk.Frame(left_panel, bg="#111827")
all_frame.pack(fill="x", padx=10, pady=(0, 10))

def _all_on():
    for i in range(1, 5):
        _relay_dots[i].config(fg="#00ff88")
    def _run():
        for i in range(1, 5):
            control_relay(i, "on")
            time.sleep(0.8)
    threading.Thread(target=_run, daemon=True).start()

def _all_off():
    for i in range(1, 5):
        _relay_dots[i].config(fg="#ff3355")
    def _run():
        for i in range(1, 5):
            control_relay(i, "off")
            time.sleep(0.8)
    threading.Thread(target=_run, daemon=True).start()

tk.Button(
    all_frame, text="● Tümünü Aç",
    font=("Consolas", 8, "bold"),
    fg="#00ff88", bg="#0d1117",
    activeforeground="white", activebackground="#003a1a",
    relief="flat", bd=0, cursor="hand2", padx=8, pady=3,
    command=_all_on
).pack(side="left", expand=True, fill="x", padx=(0, 3))

tk.Button(
    all_frame, text="■ Tümünü Kapat",
    font=("Consolas", 8, "bold"),
    fg="#ff3355", bg="#0d1117",
    activeforeground="white", activebackground="#3a0010",
    relief="flat", bd=0, cursor="hand2", padx=8, pady=3,
    command=_all_off
).pack(side="left", expand=True, fill="x", padx=(3, 0))

# =========================
# MODLAR PANELİ
# =========================
tk.Label(
    left_panel,
    text="MODLAR",
    font=("Consolas", 9, "bold"),
    fg="cyan",
    bg="#111827"
).pack(anchor="w", padx=12, pady=(10, 4))

modlar_frame = tk.Frame(left_panel, bg="#111827")
modlar_frame.pack(fill="x", padx=10, pady=(0, 10))

_mod_butonlar = [
    ("○  Stüdyo Aç",    "#7fb3c8", lambda: threading.Thread(target=stüdyo_mod_ac,  daemon=True).start()),
    ("○  Stüdyo Kapat", "#7fb3c8", lambda: threading.Thread(target=stüdyo_mod_kapat, daemon=True).start()),
    ("⊙  Odak Aç",      "#00ff88", lambda: threading.Thread(target=odak_mod_ac,    daemon=True).start()),
    ("⊙  Odak Kapat",   "#ff3355", lambda: threading.Thread(target=odak_mod_kapat, daemon=True).start()),
]

for idx, (metin, renk, cmd) in enumerate(_mod_butonlar):
    r, c = divmod(idx, 2)
    tk.Button(
        modlar_frame,
        text=metin,
        font=("Consolas", 9),
        fg=renk,
        bg="#111827",
        activeforeground="white",
        activebackground="#0d1117",
        relief="flat", bd=0, cursor="hand2",
        padx=4, pady=4,
        command=cmd
    ).grid(row=r, column=c, padx=6, pady=4, sticky="w")

jarvis_dur    = False
_jarvis_thread = None

def restart():
    global _jarvis_thread, jarvis_dur
    # Zaten çalışıyorsa yeni thread açma
    if _jarvis_thread and _jarvis_thread.is_alive():
        speak("Zaten çalışıyorum.")
        return
    jarvis_dur     = False
    _jarvis_thread = threading.Thread(target=jarvis, daemon=True)
    _jarvis_thread.start()
    write_output("Jarvis: Sistem aktif.")
    _durum_guncelle(True)

def stop_jarvis():
    global jarvis_dur
    jarvis_dur = True
    speak("J.A.R.V.I.S durduruldu.")
    _durum_guncelle(False)

def _durum_guncelle(aktif: bool):
    """Log başlığındaki butonları ve durum etiketini senkronize eder."""
    try:
        if aktif:
            basla_btn.config(fg="#3a6175")
            dur_btn.config(fg="#ff3355")
            _durum_lbl.config(text="● AKTİF", fg="#00ff88")
        else:
            basla_btn.config(fg="#00ff88")
            dur_btn.config(fg="#3a6175")
            _durum_lbl.config(text="● HAZIR", fg="#3a6175")
    except Exception:
        pass





# =========================
# ORTA PANEL
# =========================
center_panel = tk.Frame(main_frame, bg="#161b22")
center_panel.pack(side="left", fill="both", expand=True)

title_label = tk.Label(
    center_panel,
    text="J.A.R.V.I.S",
    font=("Orbitron", 36, "bold"),
    fg="cyan",
    bg="#161b22"
)
title_label.pack(pady=15)

# ---- LOG BAŞLIĞI + TEMİZLE BUTONU ----
log_header_frame = tk.Frame(center_panel, bg="#161b22")
log_header_frame.pack(fill="x", padx=20)

tk.Label(
    log_header_frame,
    text="OTURUM GÜNLÜĞÜ",
    font=("Consolas", 9, "bold"),
    fg="#3a6175",
    bg="#161b22"
).pack(side="left")

def clear_log():
    log_box.config(state="normal")
    log_box.delete("1.0", tk.END)
    log_box.config(state="disabled")
    write_output("Jarvis: Günlük temizlendi.")

tk.Button(
    log_header_frame,
    text="TEMİZLE",
    font=("Consolas", 8, "bold"),
    fg="#3a6175",
    bg="#161b22",
    activeforeground="cyan",
    activebackground="#0d1117",
    relief="flat",
    bd=0,
    cursor="hand2",
    command=clear_log
).pack(side="right", padx=(4, 0))

# HAZIR / AKTİF durum etiketi
_durum_lbl = tk.Label(
    log_header_frame,
    text="● HAZIR",
    font=("Consolas", 8, "bold"),
    fg="#3a6175",
    bg="#161b22"
)
_durum_lbl.pack(side="right", padx=(4, 8))

basla_btn = tk.Button(
    log_header_frame,
    text="▶  BAŞLAT",
    font=("Consolas", 8, "bold"),
    fg="#00ff88",
    bg="#161b22",
    activeforeground="white",
    activebackground="#003a1a",
    relief="flat",
    bd=0,
    cursor="hand2",
    command=restart
)
basla_btn.pack(side="right", padx=(4, 0))

dur_btn = tk.Button(
    log_header_frame,
    text="■  DURDUR",
    font=("Consolas", 8, "bold"),
    fg="#ff3355",
    bg="#161b22",
    activeforeground="white",
    activebackground="#3a0010",
    relief="flat",
    bd=0,
    cursor="hand2",
    command=stop_jarvis
)
dur_btn.pack(side="right", padx=(4, 0))

log_box = tk.Text(
    center_panel,
    bg="#0d1117",
    fg="white",
    font=("Consolas", 12)
)

log_box.pack(fill="both", expand=True, padx=20, pady=20)
log_box.tag_config("ts", foreground="#3a6175")   # [HH:MM:SS] soluk gri
log_box.config(state="disabled")

# Konuşma motoru başlatma ve ayarlar
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Konuşma kuyruğu
speak_queue = queue.Queue()

# Konuşma thread'i
def speak_worker():
    while True:
        text = speak_queue.get()
        if text is None:  # Stop sinyali
            break
        engine.say(text)
        engine.runAndWait()
        speak_queue.task_done()

# speak_worker thread'ini başlat
_speak_thread = threading.Thread(target=speak_worker, daemon=True)
_speak_thread.start()

def write_output(text):
    ts = time.strftime("%H:%M:%S")
    log_box.config(state='normal')
    log_box.insert(tk.END, f"[{ts}] ", "ts")
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)
    log_box.config(state='disabled')

def speak(text):
    write_output("Jarvis: " + text)
    speak_queue.put(text)

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        write_output("Dinleniyor...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        try:
            komut = r.recognize_google(audio, language='tr-TR')
            write_output("Sen: " + komut)
            return komut.lower()
        except sr.UnknownValueError:
            speak("Anlayamadım, tekrar eder misin?")
            return ""
        except sr.RequestError:
            speak("İnternet bağlantısı yok veya servis ulaşılamıyor.")
            return ""

# =========================
# SAĞ PANEL
# =========================
right_panel = tk.Frame(main_frame, bg="#111827", width=260)
right_panel.pack(side="right", fill="y")
right_panel.pack_propagate(False)

# === BAŞLIK ===
device_conn_text = tk.Label(
    right_panel,
    text="Cihaz Durumları",
    font=("Arial", 13, "bold"),
    fg="cyan",
    bg="#111827"
)
device_conn_text.pack(pady=(6, 2))

# === TEXT + SCROLLBAR FRAME ===
device_frame = tk.Frame(right_panel, bg="#0d1117")
device_frame.pack(fill="both", expand=True, padx=8, pady=6)

# === CİHAZ LİSTESİ (Dinamik — ping ile izlenir) ===
device_conn = tk.Text(
    device_frame,
    bg="#0d1117", fg="white", font=("Consolas", 10),
    width=30, height=12, bd=0,
)
device_conn.pack(fill="both", expand=True)

device_conn.tag_config("acik",       foreground="#00ff88")
device_conn.tag_config("kapali",     foreground="#ff4444")
device_conn.tag_config("bilinmiyor", foreground="#888888")
device_conn.tag_config("ip_satir",   foreground="#4b5563")
device_conn.tag_config("isim_satir", foreground="white")

device_conn.insert("end", "Cihazlar taranıyor...\n", "bilinmiyor")
device_conn.config(state="disabled")

# === CİHAZ KONTROL BUTONLARI ===
ctrl_label = tk.Label(right_panel, text="Cihaz Kontrol",
                      font=("Arial", 11, "bold"), fg="cyan", bg="#111827")
ctrl_label.pack(pady=(4, 2))

ctrl_frame = tk.Frame(right_panel, bg="#111827")
ctrl_frame.pack(padx=6, pady=4)

tk.Button(ctrl_frame, text="Samsung TV", bg="#1f2937", fg="cyan",
          font=("Consolas", 10), relief="flat", width=13,
          command=tv_gui).grid(row=0, column=0, padx=3, pady=3)

tk.Button(ctrl_frame, text="Uzak PC (SSH)", bg="#1f2937", fg="cyan",
          font=("Consolas", 10), relief="flat", width=13,
          command=uzak_pc_gui).grid(row=0, column=1, padx=3, pady=3)

flask_status_var = tk.StringVar(value="Telefon Sunucu: OFF")

def toggle_flask():
    flask_sunucu_baslat()
    flask_status_var.set(f"Telefon: :{FLASK_PORT}")
    flask_btn_widget.config(fg="lime")

flask_btn_widget = tk.Button(
    ctrl_frame, textvariable=flask_status_var,
    bg="#1f2937", fg="white", font=("Consolas", 9),
    relief="flat", width=28, command=toggle_flask
)
flask_btn_widget.grid(row=1, column=0, columnspan=2, padx=3, pady=3)

def _ciz_cihazlar():
    try:
        device_conn.config(state="normal"); device_conn.delete("1.0","end")
        for key, cihaz in CIHAZLAR.items():
            durum  = _cihaz_durum.get(key)
            t_ikon = TIP_IKON.get(cihaz["tip"],"?")
            if durum is True:   tag,nokta = "acik","● "
            elif durum is False:tag,nokta = "kapali","● "
            else:               tag,nokta = "bilinmiyor","○ "
            device_conn.insert("end", nokta, tag)
            device_conn.insert("end", f"{t_ikon} {cihaz['isim']}\n","isim_satir")
            device_conn.insert("end", f"   {cihaz['ip']}\n","ip_satir")
        device_conn.config(state="disabled")
    except Exception: pass

def manuel_tara():
    tara_btn.config(text="Taranıyor...", state="disabled")
    def _tara():
        tum_cihazlari_tara(); _ciz_cihazlar()
        tara_btn.config(text="Cihazları Tara", state="normal")
    threading.Thread(target=_tara, daemon=True).start()

tara_btn = tk.Button(ctrl_frame, text="Cihazları Tara", bg="#0d1117", fg="cyan",
                     font=("Consolas", 10), relief="flat", width=28, command=manuel_tara)
tara_btn.grid(row=2, column=0, columnspan=2, padx=3, pady=3)

tk.Button(ctrl_frame, text="Gemini AI Sohbet", bg="#1f2937", fg="#a3e635",
          font=("Consolas", 10), relief="flat", width=28, command=gemini_gui
          ).grid(row=3, column=0, columnspan=2, padx=3, pady=3)

tk.Button(ctrl_frame, text="Ag Guvenlik Izleme", bg="#1f2937", fg="#f87171",
          font=("Consolas", 10), relief="flat", width=28, command=yabanci_cihaz_gui
          ).grid(row=4, column=0, columnspan=2, padx=3, pady=3)

# Otomatik cihaz paneli güncellemesi + ping izleme başlat
paneli_guncelle_fn(device_conn, windows, aralik_ms=30_000)
surekli_izle(aralik_sn=30)


net_data = tk.Text(
    right_panel,
    bg="#0d1117",
    fg="white",
    font=("Consolas", 9),
    width=30,
    height=10,
    bd=0,
    relief="flat",
)
net_data.pack(fill="both", expand=True, padx=10, pady=(0, 6))

net_data.tag_config("baslik", foreground="cyan",    font=("Consolas", 8, "bold"))
net_data.tag_config("key",    foreground="#3a6175", font=("Consolas", 9))
net_data.tag_config("val",    foreground="#e8f4f8", font=("Consolas", 9))
net_data.tag_config("sep",    foreground="#0f2a3f")
net_data.tag_config("good",   foreground="#00ff88", font=("Consolas", 9, "bold"))
net_data.tag_config("warn",   foreground="#ff6b35", font=("Consolas", 9, "bold"))
net_data.tag_config("dim",    foreground="#3a6175", font=("Consolas", 8))

net_data.config(state="disabled")

def get_wifi_name():
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("SSID") and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
                if ssid:
                    return ssid
    except:
        pass

    return "-"

def get_network_info():
    output = subprocess.check_output(
        "ipconfig /all",
        shell=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    wifi_name = get_wifi_name()
    adapter = "-"
    ipv4 = "-"
    ipv6 = "-"
    mac = "-"
    gateway = "-"
    subnet = "-"
    dns1 = "-"
    dns2 = "-"
    adapter_name = "-"

    in_adapter = False
    adapter_type = None
    dns_section = False
    lines = output.splitlines()

    for i, line in enumerate(lines):
        line_low = line.lower()
        line_stripped = line.strip()

        if "wireless lan adapter wi-fi" in line_low:
            in_adapter = True
            adapter_type = "Wi-Fi"
            adapter = "Wi-Fi"
            dns_section = False
            # Adapter adını al
            if ":" in line:
                adapter_name = line.split(":")[0].strip()
            continue

        if "ethernet adapter" in line_low:
            in_adapter = True
            adapter_type = "Ethernet"
            adapter = "Ethernet"
            dns_section = False
            # Adapter adını al
            if ":" in line:
                adapter_name = line.split(":")[0].strip()
            continue

        if "adapter" in line_low and not (
            "wi-fi" in line_low or "ethernet" in line_low
        ):
            in_adapter = False
            dns_section = False

        if in_adapter:
            if "physical address" in line_low:
                mac = line.split(":")[-1].strip()

            elif "ipv4" in line_low:
                ipv4 = line.split(":")[-1].split("(")[0].strip()

            elif "ipv6" in line_low:
                ipv6 = line.split(":")[-1].strip()
            
            elif "default gateway" in line_low or "varsayılan ağ geçidi" in line_low:
                gateway = line.split(":")[-1].strip()
            
            elif "subnet mask" in line_low or "alt ağ maskesi" in line_low:
                subnet = line.split(":")[-1].strip()
            
            elif "dns servers" in line_low or "dns sunucuları" in line_low:
                dns_section = True
                dns_line = line.split(":")[-1].strip()
                # IP adresi kontrolü
                if dns_line and re.match(r'^\d+\.\d+\.\d+\.\d+', dns_line):
                    if dns1 == "-":
                        dns1 = dns_line
                    elif dns2 == "-":
                        dns2 = dns_line
            
            elif dns_section and line_stripped:
                # DNS devam satırları (girintili IP'ler)
                if re.match(r'^\d+\.\d+\.\d+\.\d+', line_stripped):
                    if dns1 == "-":
                        dns1 = line_stripped
                    elif dns2 == "-":
                        dns2 = line_stripped
                elif not line_stripped.startswith("."):
                    dns_section = False

    if adapter_type == "Ethernet":
        wifi_name = "Kablolu bağlantı"

    if not adapter_type:
        adapter = "Bağlı değil"

    return wifi_name, adapter, ipv4, ipv6, mac, gateway, subnet, dns1, dns2, adapter_name

def get_network_usage():
    """Ağ kullanım istatistiklerini alır (gönderilen/alınan bytes)"""
    try:
        stats = psutil.net_io_counters()
        sent_mb = stats.bytes_sent / (1024 * 1024)
        recv_mb = stats.bytes_recv / (1024 * 1024)
        return f"{sent_mb:.1f} MB", f"{recv_mb:.1f} MB"
    except:
        return "-", "-"

def get_wifi_signal():
    """Wi-Fi sinyal gücünü alır (Windows)"""
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        for line in output.splitlines():
            line_low = line.lower()
            if "signal" in line_low or "sinyal" in line_low:
                if "%" in line:
                    signal = line.split(":")[-1].strip()
                    return signal
        return "-"
    except:
        return "-"

def get_link_speed():
    """Bağlantı hızını alır (Mbps)"""
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        for line in output.splitlines():
            line_low = line.lower()
            if "receive rate" in line_low or "alma hızı" in line_low:
                speed = line.split(":")[-1].strip()
                return speed
            elif "transmit rate" in line_low or "gönderme hızı" in line_low:
                speed = line.split(":")[-1].strip()
                return speed
        return "-"
    except:
        return "-"

def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=3) as response:
            return response.read().decode("utf-8")
    except:
        return "Alınamadı"

def get_ping():
    try:
        output = subprocess.check_output(
            "ping 8.8.8.8 -n 1",
            shell=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        match = re.search(r"time[=<]\s*(\d+)\s*ms", output)
        if match:
            return f"{match.group(1)} ms"
        else:
            return "Timeout"
    except:
        return "Ping yok"

last_speed = ("-", "-", "-")
last_speed_time = 0
speedtest_running = False


def speedtest_worker():
    global last_speed, last_speed_time, speedtest_running

    speedtest_running = True
    last_speed = ("Ölçülüyor...", "Ölçülüyor...", "Ölçülüyor...")

    try:
        st = speedtest.Speedtest()
        st.get_best_server()

        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping

        last_speed = (
            f"{download:.1f} Mbps",
            f"{upload:.1f} Mbps",
            f"{ping:.0f} ms"
        )
    except:
        last_speed = ("-", "-", "-")

    last_speed_time = time.time()
    speedtest_running = False

def update_network_panel():
    global last_speed_time

    wifi, adapter, ipv4, ipv6, mac, gateway, subnet, dns1, dns2, adapter_name = get_network_info()
    now = time.time()

    if not speedtest_running and now - last_speed_time >= 60:
        threading.Thread(target=speedtest_worker, daemon=True).start()

    down, up, sping   = last_speed
    sent_mb, recv_mb  = get_network_usage()
    wifi_signal       = get_wifi_signal()
    link_speed        = get_link_speed()
    ping_val          = get_ping()

    net_data.config(state="normal")
    net_data.delete("1.0", "end")

    def row(key, val, val_tag="val"):
        net_data.insert("end", f"  {key:<10}", "key")
        net_data.insert("end", f"  {val}\n",   val_tag)

    def sep():
        net_data.insert("end", "  " + "─" * 26 + "\n", "sep")

    # ── BAĞLANTI ──────────────────────────────────────
    net_data.insert("end", "  BAĞLANTI\n", "baslik")
    sep()
    row("Ağ",     adapter)
    row("SSID",   wifi)
    if wifi_signal != "-":
        # Sinyal gücüne göre renk
        try:
            pct = int(wifi_signal.replace("%","").strip())
            sig_tag = "good" if pct >= 60 else "warn"
        except:
            sig_tag = "val"
        row("Sinyal",  wifi_signal, sig_tag)
    if link_speed != "-":
        row("Hız",     link_speed)

    # ── ADRES ─────────────────────────────────────────
    net_data.insert("end", "\n  ADRES\n", "baslik")
    sep()
    row("IPv4",    ipv4)
    row("IPv6",    ipv6[:20] + "…" if len(str(ipv6)) > 20 else ipv6)
    row("MAC",     mac)
    if gateway != "-": row("Gateway", gateway)
    if subnet  != "-": row("Subnet",  subnet)
    if dns1    != "-": row("DNS",     dns1)

    # ── İNTERNET ──────────────────────────────────────
    net_data.insert("end", "\n  İNTERNET\n", "baslik")
    sep()
    row("Dış IP",  get_public_ip())

    # Ping rengi
    try:
        ping_ms  = int(ping_val.replace("ms","").strip())
        ping_tag = "good" if ping_ms < 50 else "warn" if ping_ms < 120 else "warn"
    except:
        ping_tag = "val"
    row("Ping",   ping_val, ping_tag)

    # ── KULLANIM ──────────────────────────────────────
    net_data.insert("end", "\n  KULLANIM\n", "baslik")
    sep()
    row("↑ Gönder",  sent_mb)
    row("↓ Alınan",  recv_mb)

    # ── HIZ TESTİ ─────────────────────────────────────
    net_data.insert("end", "\n  HIZ TESTİ\n", "baslik")
    sep()
    row("Download", down,  "good" if down not in ("-","…") else "dim")
    row("Upload",   up,    "good" if up   not in ("-","…") else "dim")
    row("Gecikme",  sping, "val")

    # Güncelleme zamanı
    net_data.insert("end", f"\n  {time.strftime('%H:%M:%S')} güncellendi\n", "dim")

    net_data.config(state="disabled")
    windows.after(5000, update_network_panel)

update_network_panel()

# ---- SAAT ----
clock_label = tk.Label(
    center_panel,
    font=("Orbitron", 22),
    fg="cyan",
    bg="#161b22"
)
clock_label.pack(pady=10)

def update_clock():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    clock_label.after(1000, update_clock)

update_clock()

# ---- TARİH ----
date_label = tk.Label(
    center_panel,
    font=("Orbitron", 13),
    fg="cyan",
    bg="#161b22"
)
date_label.pack(pady=(0, 6))

# Türkçe gün/ay karşılıkları (locale bağımsız)
_TR_DAYS   = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
_TR_MONTHS = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
              "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

def update_date():
    now = datetime.datetime.now()
    gun  = _TR_DAYS[now.weekday()]
    ay   = _TR_MONTHS[now.month]
    text = f"{gun}  ·  {now.day} {ay} {now.year}"
    date_label.config(text=text)
    date_label.after(60000, update_date)

update_date()

# ---- CPU / RAM / GPU  (canvas bar'lı yeni sistem paneli) ----
sys_outer = tk.Frame(center_panel, bg="#161b22")
sys_outer.pack(pady=(0, 8))

def _make_sys_bar(parent, label_text):
    """Bir satır: etiket + canvas bar + % değeri"""
    row = tk.Frame(parent, bg="#161b22")
    row.pack(anchor="w", padx=20, pady=2)
    tk.Label(row, text=f"{label_text:<5}", font=("Consolas", 9),
             fg="#3a6175", bg="#161b22", width=5).pack(side="left")
    canvas = tk.Canvas(row, height=10, width=180,
                       bg="#0d1117", highlightthickness=0, bd=0)
    canvas.pack(side="left", padx=6)
    val_lbl = tk.Label(row, text="  0%", font=("Consolas", 9),
                       fg="white", bg="#161b22", width=5)
    val_lbl.pack(side="left")
    return canvas, val_lbl

_cpu_bar  = _make_sys_bar(sys_outer, "CPU")
_ram_bar  = _make_sys_bar(sys_outer, "RAM")
_disk_bar = _make_sys_bar(sys_outer, "DISK")
_gpu_row  = tk.Frame(sys_outer, bg="#161b22")
_gpu_row.pack(anchor="w", padx=20, pady=2)
_gpu_lbl  = tk.Label(_gpu_row, text="GPU   N/A",
                     font=("Consolas", 9), fg="#7fb3c8", bg="#161b22")
_gpu_lbl.pack(side="left")

def _draw_bar(canvas_val_lbl, pct):
    canvas, val_lbl = canvas_val_lbl
    w = 180
    canvas.delete("all")
    canvas.create_rectangle(0, 0, w, 10, fill="#0d1117", outline="")
    color = "#00ff88" if pct < 70 else "#ff6b35" if pct < 90 else "#ff3355"
    canvas.create_rectangle(0, 0, int(w * pct / 100), 10, fill=color, outline="")
    val_lbl.config(text=f"{pct:3.0f}%")

def get_gpu_usage():
    """GPU kullanımını alır (NVIDIA için)"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            usage = parts[0].strip()
            temp  = parts[1].strip() if len(parts) > 1 else "?"
            return int(usage), f"GPU   {usage}%  ·  {temp}°C"
        return None, "GPU   N/A"
    except:
        try:
            import wmi
            w = wmi.WMI()
            name = w.Win32_VideoController()[0].Name[:22]
            return None, f"GPU   {name}"
        except:
            return None, "GPU   N/A"

def update_system_info():
    cpu  = psutil.cpu_percent(interval=0)
    ram  = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    _draw_bar(_cpu_bar,  cpu)
    _draw_bar(_ram_bar,  ram)
    _draw_bar(_disk_bar, disk)
    _, gpu_text = get_gpu_usage()
    _gpu_lbl.config(text=gpu_text)
    sys_outer.after(1500, update_system_info)

update_system_info()

WEATHER_API_KEY = "925863c13ed89d69602b4e4c4f53d33c"
WEATHER_DEFAULT_CITY = "Izmir,TR"
_last_weather_ok = None
_last_weather_ok_at = None

def _safe_get(dct, path, default=None):
    cur = dct
    for key in path:
        try:
            cur = cur[key]
        except Exception:
            return default
    return cur

def get_weather(city=WEATHER_DEFAULT_CITY):
    """
    OpenWeatherMap current weather.
    city: "Izmir,TR" gibi (ülke kodu ile) daha doğru eşleşir.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "tr"
    }

    try:
        r = requests.get(url, params=params, timeout=6)
        data = r.json()

        # API hata dönüşleri bazen JSON içinde gelir
        if r.status_code != 200:
            msg = _safe_get(data, ["message"], "Hata")
            return {"ok": False, "error": f"{r.status_code}: {msg}"}

        temp = _safe_get(data, ["main", "temp"])
        feels = _safe_get(data, ["main", "feels_like"])
        humidity = _safe_get(data, ["main", "humidity"])
        wind_ms = _safe_get(data, ["wind", "speed"])
        wind_deg = _safe_get(data, ["wind", "deg"])
        temp_min = _safe_get(data, ["main", "temp_min"])
        temp_max = _safe_get(data, ["main", "temp_max"])
        pressure = _safe_get(data, ["main", "pressure"])
        visibility_m = _safe_get(data, ["visibility"])

        desc = _safe_get(data, ["weather", 0, "description"], "")
        city_name = _safe_get(data, ["name"], city)
        country = _safe_get(data, ["sys", "country"], "")

        # birimler
        wind_kmh = None
        if isinstance(wind_ms, (int, float)):
            wind_kmh = wind_ms * 3.6

        visibility_km = None
        if isinstance(visibility_m, (int, float)):
            visibility_km = visibility_m / 1000.0

        return {
            "ok": True,
            "city": city_name,
            "country": country,
            "temp": round(temp) if isinstance(temp, (int, float)) else None,
            "feels": round(feels) if isinstance(feels, (int, float)) else None,
            "temp_min": round(temp_min) if isinstance(temp_min, (int, float)) else None,
            "temp_max": round(temp_max) if isinstance(temp_max, (int, float)) else None,
            "desc": (str(desc).capitalize() if desc else None),
            "humidity": humidity,
            "pressure": pressure,
            "wind_ms": wind_ms,
            "wind_kmh": round(wind_kmh, 1) if wind_kmh is not None else None,
            "wind_deg": wind_deg,
            "visibility_km": round(visibility_km, 1) if visibility_km is not None else None,
            "raw": data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
weather_frame = tk.Frame(
    right_panel,
    bg="#0d1117",
    highlightbackground="#0f2a3f",
    highlightthickness=1
)
weather_frame.pack(fill="x", padx=8, pady=(4, 0))

# Başlık satırı
weather_header = tk.Frame(weather_frame, bg="#0d1117")
weather_header.pack(fill="x", padx=10, pady=(8, 2))

tk.Label(
    weather_header,
    text="HAVA DURUMU",
    font=("Consolas", 8, "bold"),
    fg="cyan",
    bg="#0d1117"
).pack(side="left")

weather_time_lbl = tk.Label(
    weather_header,
    text="",
    font=("Consolas", 7),
    fg="#3a6175",
    bg="#0d1117"
)
weather_time_lbl.pack(side="right")

# Sıcaklık büyük gösterim
weather_temp_lbl = tk.Label(
    weather_frame,
    text="--°C",
    font=("Consolas", 28, "bold"),
    fg="#00d4ff",
    bg="#0d1117"
)
weather_temp_lbl.pack(anchor="w", padx=12)

# Durum açıklaması
weather_desc_lbl = tk.Label(
    weather_frame,
    text="",
    font=("Consolas", 9),
    fg="#7fb3c8",
    bg="#0d1117"
)
weather_desc_lbl.pack(anchor="w", padx=14, pady=(0, 4))

# Detay alanı — Text widget ile tag'li
weather_detail = tk.Text(
    weather_frame,
    bg="#0d1117",
    bd=0, relief="flat",
    font=("Consolas", 9),
    height=5,
    state="disabled",
    cursor="arrow",
)
weather_detail.pack(fill="x", padx=8, pady=(0, 8))

weather_detail.tag_config("key", foreground="#3a6175")
weather_detail.tag_config("val", foreground="#e8f4f8")
weather_detail.tag_config("sep", foreground="#0f2a3f")

def update_weather():
    global _last_weather_ok, _last_weather_ok_at

    w   = get_weather(WEATHER_DEFAULT_CITY)
    now = datetime.datetime.now()

    if w.get("ok"):
        _last_weather_ok    = w
        _last_weather_ok_at = now
        show        = w
        time_text   = f"↻ {now.strftime('%H:%M')}"
    else:
        show      = _last_weather_ok
        time_text = f"! {_last_weather_ok_at.strftime('%H:%M') if _last_weather_ok_at else 'hata'}"

    weather_time_lbl.config(text=time_text)

    if not show:
        weather_temp_lbl.config(text="--°C")
        weather_desc_lbl.config(text="Veri alınamadı")
        windows.after(600000, update_weather)
        return

    # Büyük sıcaklık
    temp = show.get("temp")
    weather_temp_lbl.config(text=f"{temp}°C" if temp is not None else "--°C")

    # Hissedilen + açıklama
    feels = show.get("feels")
    desc  = show.get("desc") or ""
    city  = show.get("city","") + (f", {show['country']}" if show.get("country") else "")
    weather_desc_lbl.config(text=f"{desc}  ·  {city}")

    # Detay satırları
    weather_detail.config(state="normal")
    weather_detail.delete("1.0", "end")

    def wrow(k, v):
        weather_detail.insert("end", f"  {k:<10}", "key")
        weather_detail.insert("end", f"  {v}\n",   "val")

    wrow("Hissedilen", f"{feels}°C" if feels is not None else "-")
    wrow("Min / Max",  f"{show.get('temp_min','-')} / {show.get('temp_max','-')}°C")
    wrow("Nem",        f"{show.get('humidity','-')} %")
    wrow("Rüzgar",     f"{show.get('wind_kmh','-')} km/h")
    wrow("Görüş",      f"{show.get('visibility_km','-')} km")

    weather_detail.config(state="disabled")
    windows.after(600000, update_weather)

update_weather()

# --- Ses Kontrol Nesnesi ---
devices = AudioUtilities.GetSpeakers()

interface = devices._dev.Activate(   # 🔥 KRİTİK FARK BURASI
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))
volume.SetMasterVolumeLevelScalar(0.5, None)  # %50

# --- Ses Ayarlama Fonksiyonu ---
def set_volume(val):
    volume.SetMasterVolumeLevelScalar(float(val) / 100, None)

# --- UI ---
# ── SES SEVİYESİ ────────────────────────────────────
vol_frame = tk.Frame(
    right_panel,
    bg="#0d1117",
    highlightbackground="#0f2a3f",
    highlightthickness=1
)
vol_frame.pack(fill="x", padx=8, pady=(6, 0))

vol_header = tk.Frame(vol_frame, bg="#0d1117")
vol_header.pack(fill="x", padx=10, pady=(8, 4))

tk.Label(vol_header, text="SES SEVİYESİ",
         font=("Consolas", 8, "bold"), fg="cyan", bg="#0d1117").pack(side="left")

vol_pct_lbl = tk.Label(vol_header, text="50 %",
                        font=("Consolas", 9, "bold"), fg="#00d4ff", bg="#0d1117")
vol_pct_lbl.pack(side="right")

vol_slider_frame = tk.Frame(vol_frame, bg="#0d1117")
vol_slider_frame.pack(fill="x", padx=10, pady=(0, 8))

def set_volume(val):
    v = int(float(val))
    volume.SetMasterVolumeLevelScalar(v / 100, None)
    vol_pct_lbl.config(text=f"{v} %")

volume_slider = tk.Scale(
    vol_slider_frame,
    from_=0, to=100,
    orient="horizontal",
    command=set_volume,
    bg="#0d1117",
    fg="#00d4ff",
    troughcolor="#0f2a3f",
    activebackground="#00d4ff",
    highlightthickness=0,
    bd=0,
    showvalue=False,
    sliderlength=14,
    width=6,
)
volume_slider.set(int(volume.GetMasterVolumeLevelScalar() * 100))
volume_slider.pack(fill="x")

# ── MEDYA KONTROL ────────────────────────────────────

# --- Medya Kontrol Fonksiyonları (YouTube Music için) ---
# Windows medya tuş kodları
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

def send_media_key(key_code):
    """Windows medya tuşunu simüle eder"""
    try:
        # keybd_event kullanarak daha basit yöntem
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)  # Tuş basma
        time.sleep(0.05)  # Kısa bekleme
        ctypes.windll.user32.keybd_event(key_code, 0, 0x0002, 0)  # Tuş bırakma
        return True
    except Exception as e:
        print(f"Medya tuşu hatası: {e}")
        return False

def media_play_pause():
    """Play/Pause tuşu"""
    send_media_key(VK_MEDIA_PLAY_PAUSE)
    speak("Müzik durduruldu veya başlatıldı.")

def media_next():
    """Sonraki şarkı"""
    send_media_key(VK_MEDIA_NEXT_TRACK)
    speak("Sonraki şarkı.")

def media_previous():
    """Önceki şarkı"""
    send_media_key(VK_MEDIA_PREV_TRACK)
    speak("Önceki şarkı.")

# --- Medya Kontrol UI ---
media_frame = tk.Frame(
    right_panel,
    bg="#0d1117",
    highlightbackground="#0f2a3f",
    highlightthickness=1
)
media_frame.pack(fill="x", padx=8, pady=(6, 0))

tk.Label(media_frame, text="MEDYA KONTROL",
         font=("Consolas", 8, "bold"), fg="cyan", bg="#0d1117"
         ).pack(anchor="w", padx=10, pady=(8, 6))

media_buttons_frame = tk.Frame(media_frame, bg="#0d1117")
media_buttons_frame.pack(pady=(0, 10))

for col, (emoji, cmd, tip) in enumerate([
    ("⏮", media_previous, "Önceki"),
    ("⏯", media_play_pause, "Oynat/Duraklat"),
    ("⏭", media_next, "Sonraki"),
]):
    btn = tk.Button(
        media_buttons_frame,
        text=emoji,
        font=("Arial", 18),
        bg="#0d1117",
        fg="#00d4ff",
        width=3,
        command=cmd,
        relief="flat",
        bd=0,
        cursor="hand2",
        activebackground="#0f2a3f",
        activeforeground="white",
    )
    btn.grid(row=0, column=col, padx=10)

#Röle Kontrol Fonksiyonu
def control_relay(relay, state):
    try:
        url = f"http://{ESP_IP}/relay{relay}/{state}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            durum = "açıldı" if state == "on" else "kapatıldı"
            speak(f"Röle {relay} {durum}.")
        else:
            speak(f"ESP32 yanıt kodu: {r.status_code}")
    except Exception as e:
        speak("ESP32'ye bağlanılamadı.")

#Stüdyo Modları
def stüdyo_mod_ac():
    speak("Stüdyo modu açılıyor.")
    webbrowser.open("https://music.youtube.com/playlist?list=LM")
    try:
        subprocess.Popen("C:\\Users\\KODUMUN_ERRORU_\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
    except:
        speak("VS Code açılamadı.")
    webbrowser.open(f"http://{ESP_IP}")
    webbrowser.open("https://www.turkhackteam.org/")
    webbrowser.open("https://www.youtube.com/")
    webbrowser.open("https://web.whatsapp.com/")
    webbrowser.open("https://www.udemy.com/")
    webbrowser.open("https://chatgpt.com/")
    subprocess.Popen("calc.exe")
    subprocess.Popen("notepad.exe")
    # Röleleri bloke etmeden sırayla aç
    def _relay_sequence_on():
        for i in range(1, 5):
            control_relay(i, "on")
            time.sleep(2)
    threading.Thread(target=_relay_sequence_on, daemon=True).start()

def stüdyo_mod_kapat():
    speak("Stüdyo modu kapatılıyor.")
    for prog in ["notepad.exe", "Calc.exe", "chrome.exe", "msedge.exe"]:
        os.system(f"taskkill /f /im {prog} 2>nul")
    def _relay_sequence_off():
        for i in range(1, 5):
            control_relay(i, "off")
            time.sleep(2)
    threading.Thread(target=_relay_sequence_off, daemon=True).start()

#Odak Modları
def odak_mod_ac():
    speak("Odak modu açılıyor.")
    webbrowser.open(f"http://{ESP_IP}")
    webbrowser.open("https://www.udemy.com/")
    webbrowser.open("https://chatgpt.com/")
    webbrowser.open("https://www.youtube.com/")
    webbrowser.open("https://web.whatsapp.com/")
    subprocess.Popen("calc.exe")
    webbrowser.open("https://music.youtube.com/playlist?list=LM")
    def _relay_off():
        for i in range(1, 5):
            control_relay(i, "off")
            time.sleep(1)
    threading.Thread(target=_relay_off, daemon=True).start()

def odak_mod_kapat():
    speak("Odak modu kapatıldı.")
    for prog in ["Calc.exe", "chrome.exe", "msedge.exe"]:
        os.system(f"taskkill /f /im {prog} 2>nul")
    def _relay_off():
        for i in range(1, 5):
            control_relay(i, "off")
            time.sleep(1)
    threading.Thread(target=_relay_off, daemon=True).start()

#ESP_Web
def ESP_Web():
    webbrowser.open(f"http://{ESP_IP}")
    speak("ESP Web açılıyor.")

#Turk Hack Team
def tht():
    webbrowser.open("https://www.turkhackteam.org/")
    speak("Turk Hack Team açılıyor.")

#RAT Kontrol Paneli
def rat():
    subprocess.Popen("C:\\Users\\Emre\\Documents\\PROGRAMLAMA\\RAT\\Rat.py")
    speak("RAT Kontrol Paneli açılıyor.")

#Oracle VM
def vm():
    subprocess.Popen()
    speak("Oraclle VM açılıyor.")

#Morse Haberleşme
try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False

# --- Morse haritaları ---
DOT_MS_DEFAULT = 120

CHAR_TO_MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.',
    # boşluk kelime ayırıcısı olarak '/'
    ' ': '/'
}

# Türkçe karakterleri Latin karşılıklarına eşle (Ç->C, Ş->S, İ->I, Ö->O, Ü->U, Ğ->G, ı->I)
TR_CHAR_MAP = {
    'Ç': 'C', 'ç': 'c', 'Ş': 'S', 'ş': 's', 'İ': 'I', 'ı': 'I',
    'Ö': 'O', 'ö': 'o', 'Ü': 'U', 'ü': 'u', 'Ğ': 'G', 'ğ': 'g'
}

MORSE_TO_CHAR = {v: k for k, v in CHAR_TO_MORSE.items()}

# --- Çeviri fonksiyonları ---
def normalize_turkish(text: str) -> str:
    return ''.join(TR_CHAR_MAP.get(ch, ch) for ch in text)

def text_to_morse(text: str) -> str:
    text = normalize_turkish(text).upper()
    tokens = []
    for ch in text:
        if ch in CHAR_TO_MORSE:
            tokens.append(CHAR_TO_MORSE[ch])
        else:
            tokens.append('?')  # bilinmeyen karakter
    # harfler arası boşluk ; kelimeler '/' ile ayrılıyor zaten çünkü ' ' -> '/'
    # output: her karakter için bir token, örn: 'H E L L O' -> '.... . .-.. .-.. ---'
    return ' '.join(tokens)

def morse_to_text(morse: str) -> str:
    morse = morse.strip()
    # kelime ayırıcı slash (/)
    words = morse.split(' / ')
    decoded_words = []
    for w in words:
        letters = []
        for token in w.split():
            letters.append(MORSE_TO_CHAR.get(token, '?'))
        decoded_words.append(''.join(letters))
    return ' '.join(decoded_words)

# --- Oynatma (ses veya görsel) ---
def play_morse_thread(morse: str, dot_ms: int, ui_feedback_fn=None, stop_event=None):
    """
    Arkaplanda koşacak fonksiyon. ui_feedback_fn(on_off: bool) ile GUI'ye sinyal verebilir.
    stop_event: threading.Event ile oynatma iptali.
    """
    dot = dot_ms / 1000.0
    dash = 3 * dot
    intra_symbol_gap = dot
    between_letters = 3 * dot
    between_words = 7 * dot
    freq = 750  # winsound için frekans

    for ch in morse:
        if stop_event and stop_event.is_set():
            break
        if ch == '.':
            if HAS_WINSOUND:
                winsound.Beep(freq, int(dot_ms))
            else:
                if ui_feedback_fn: ui_feedback_fn(True)
                time.sleep(dot)
                if ui_feedback_fn: ui_feedback_fn(False)
            time.sleep(intra_symbol_gap)
        elif ch == '-':
            if HAS_WINSOUND:
                winsound.Beep(freq, int(3 * dot_ms))
            else:
                if ui_feedback_fn: ui_feedback_fn(True)
                time.sleep(dash)
                if ui_feedback_fn: ui_feedback_fn(False)
            time.sleep(intra_symbol_gap)
        elif ch == ' ':
            time.sleep(between_letters)
        elif ch == '/':
            time.sleep(between_words)
        else:
            # bilinmeyen sembol
            time.sleep(dot)
class JarvisMorseGUI:
    def __init__(self, root):
        self.root = root
        root.title("Morse Haberleşme Arayüzü (Beta)")
        root.geometry("500x400")
        root.resizable(False, False)

        # Stil (ttk)
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Üst: giriş etiketleri ve entry
        frame_top = ttk.Frame(root, padding=(12, 8))
        frame_top.pack(fill='x')

        ttk.Label(frame_top, text="Girdi (metin veya Morse):").pack(anchor='w')
        self.entry = tk.Text(frame_top, height=4, wrap='word')
        self.entry.pack(fill='x')

        # Orta: butonlar
        frame_mid = ttk.Frame(root, padding=(12, 8))
        frame_mid.pack(fill='x')

        btn_encode = ttk.Button(frame_mid, text="Encode (→ Morse)", command=self.on_encode)
        btn_encode.grid(row=0, column=0, padx=6, pady=4)

        btn_decode = ttk.Button(frame_mid, text="Decode (Morse →)", command=self.on_decode)
        btn_decode.grid(row=0, column=1, padx=6, pady=4)

        btn_play = ttk.Button(frame_mid, text="Play Morse", command=self.on_play)
        btn_play.grid(row=0, column=2, padx=6, pady=4)

        btn_stop = ttk.Button(frame_mid, text="Stop", command=self.on_stop)
        btn_stop.grid(row=0, column=3, padx=6, pady=4)

        # Hız slider
        speed_frame = ttk.Frame(frame_mid)
        speed_frame.grid(row=1, column=0, columnspan=4, sticky='we', pady=(6,0))
        ttk.Label(speed_frame, text="Hız (nokta ms):").pack(side='left')
        self.speed_var = tk.IntVar(value=DOT_MS_DEFAULT)
        self.speed_slider = ttk.Scale(speed_frame, from_=40, to=300, variable=self.speed_var, orient='horizontal')
        self.speed_slider.pack(side='left', fill='x', expand=True, padx=8)

        # Alt: çıktı ve gösterge
        frame_bottom = ttk.Frame(root, padding=(12, 8))
        frame_bottom.pack(fill='both', expand=True)

        ttk.Label(frame_bottom, text="Çıktı:").pack(anchor='w')
        self.output = tk.Text(frame_bottom, height=6, wrap='word', state='normal')
        self.output.pack(fill='both', expand=True)

        # Görsel gösterge (sağ alt köşede küçük bir daire)
        self.indicator_canvas = tk.Canvas(root, width=30, height=30, highlightthickness=0)
        self.indicator_canvas.place(x=450, y=350)
        self.indicator_circle = self.indicator_canvas.create_oval(4,4,26,26, fill='gray')

        # Thread kontrol
        self.play_thread = None
        self.stop_event = None

    def set_indicator(self, on: bool):
        color = 'green' if on else 'gray'
        # tkinter çağrıları GUI thread'inde yapılmalı
        try:
            self.indicator_canvas.itemconfig(self.indicator_circle, fill=color)
        except Exception:
            pass

    def on_encode(self):
        text = self.entry.get("1.0", 'end').strip()
        if not text:
            messagebox.showinfo("Bilgi", "Lütfen çevirmek için metin girin.")
            return
        morse = text_to_morse(text)
        self.output.delete("1.0", 'end')
        self.output.insert('end', morse)

    def on_decode(self):
        text = self.entry.get("1.0", 'end').strip()
        if not text:
            messagebox.showinfo("Bilgi", "Lütfen çözmek için Morse girin.")
            return
        decoded = morse_to_text(text)
        self.output.delete("1.0", 'end')
        self.output.insert('end', decoded)

    def on_play(self):
        # Önce mevcut oynatmayı durdur
        self.on_stop()
        # hangi veriyi çalacak? önce output varsa onu kullan, yoksa entry
        payload = self.output.get("1.0", 'end').strip()
        if not payload:
            payload = self.entry.get("1.0", 'end').strip()
        if not payload:
            messagebox.showinfo("Bilgi", "Oynatılacak metin veya Morse yok.")
            return

        # Eğer payload sadece ., -, / ve boşluklardan oluşuyorsa morse kabul et
        if all(ch in '.-/ ' for ch in payload):
            morse = payload
        else:
            morse = text_to_morse(payload)

        dot_ms = int(self.speed_var.get())

        # Stop event ve thread başlat
        self.stop_event = threading.Event()
        def ui_feedback(on):
            # GUI thread'ine güvenli geçiş
            self.root.after(0, self.set_indicator, on)

        self.play_thread = threading.Thread(target=play_morse_thread, args=(morse, dot_ms, ui_feedback, self.stop_event))
        self.play_thread.daemon = True
        self.play_thread.start()

    def on_stop(self):
        if self.stop_event:
            self.stop_event.set()
            self.stop_event = None
        if self.play_thread and self.play_thread.is_alive():
            # thread bitince temizle
            self.play_thread.join(timeout=0.01)
        self.play_thread = None
        # göstergesi kapat
        self.set_indicator(False)

# --- Çalıştırma(Morse) ---
def run_gui():
    root = tk.Tk()
    app = JarvisMorseGUI(root)
    root.mainloop()

#Sezar Şifreleme
def sifrele_us(metin, kaydirma=3):
    alfabe = 'abcdefghijklmnopqrstuvwxyz'
    sonuc = ''
    for harf in metin:
        kucuk_harf = harf.lower()
        if kucuk_harf in alfabe:
            index = alfabe.index(kucuk_harf)
            yeni_index = (index + kaydirma) % len(alfabe)
            yeni_harf = alfabe[yeni_index]
            if harf.isupper():
                yeni_harf = yeni_harf.upper()
            sonuc += yeni_harf
        else:
            sonuc += harf
    return sonuc

def coz_us(metin, kaydirma=3):
    return sifrele_us(metin, -kaydirma)

def sezar_gui():
    theme = THEMES[current_theme]

    windows = tk.Toplevel()
    windows.title("Sezar Şifrreleme Arayüzü - JARVIS J4 (Beta)")
    windows.geometry("500x400")
    windows.configure(bg=theme["bg"])

    # Başlık
    lbl = tk.Label(windows, text="Sezar Şifreleme", font=("Arial", 16, "bold"),bg=theme["bg"], fg=theme["fg"])
    lbl.pack(pady=10)

    # Girdi alanı
    tk.Label(windows, text="Input Text:", font=("Arial", 12),bg=theme["bg"], fg=theme["fg"]).pack()
    entry_input = tk.Text(windows, height=5, width=50,bg=theme["text_bg"], fg=theme["text_fg"])
    entry_input.pack(pady=5)

    # Çıktı alanı
    tk.Label(windows, text="Output:", font=("Arial", 12),bg=theme["bg"], fg=theme["fg"]).pack()
    output_box = tk.Text(windows, height=5, width=50,bg=theme["text_bg"], fg=theme["text_fg"], state="disabled")
    output_box.pack(pady=5)

    # Buton işlevleri
    def encrypt_text():
        girdi = entry_input.get("1.0", tk.END).strip()
        if not girdi:
            messagebox.showwarning("Uyarı", "Lütfen bir metin giriniz!")
            return
        sifreli = sifrele_us(girdi)
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, sifreli)
        output_box.config(state="disabled")

    def decrypt_text():
        girdi = entry_input.get("1.0", tk.END).strip()
        if not girdi:
            messagebox.showwarning("Uyarı", "Lütfen bir metin giriniz!")
            return
        cozulmus = coz_us(girdi)
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, cozulmus)
        output_box.config(state="disabled")

    def copy_output():
        text = output_box.get("1.0", tk.END).strip()
        if text:
            pyperclip.copy(text)

    # Butonlar(sezar)
    btn_frame = tk.Frame(windows, bg=theme["bg"])
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Encrypt", width=12, command=encrypt_text,
              bg=theme["button_bg"], fg=theme["button_fg"]).grid(row=0, column=0, padx=10)

    tk.Button(btn_frame, text="Decrypt", width=12, command=decrypt_text,
              bg=theme["button_bg"], fg=theme["button_fg"]).grid(row=0, column=1, padx=10)

    tk.Button(btn_frame, text="Copy Output", width=12, command=copy_output,
              bg=theme["button_bg"], fg=theme["button_fg"]).grid(row=0, column=2, padx=10)

    windows.mainloop()

# GUI çağırma fonksiyonu(sezar)
def sezar_gui_thread():
    threading.Thread(target=sezar_gui, daemon=True).start()

#Github
def git_hub():
    webbrowser.open("https://github.com/")
    speak("GitHub açılıyor.")

#VS Code
def vs_code():
    speak("VS Code açılıyor.")
    try:
        subprocess.Popen("C:\\Users\\KODUMUN_ERRORU_\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
    
    except:
        speak("VS Code açılamıyor.")

#VS 2022
def vs_2022():
    speak("VS 2022 Açılıyor.")
    try:
        subprocess.Popen("C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\IDE\\devenv.exe")

    except:
        speak("VS 2022 açılamıyor.")
        
#Cisco Packet Tracer
def cisco():
    speak("Cisco Packet Tracer açılıyor.")
    try:
        subprocess.Popen("C:\\Program Files\\Cisco Packet Tracer 8.2.2\\bin\\PacketTracer.exe")
        
    except:
        speak("Cisco Packet Tracer açılamıyor.")

#Cursor AI
def cursor():
    speak("Cursor AI açılıyor.")
    subprocess.Popen("C:\\Users\\Emre\\Downloads\\cursor.exe")

#ChatGPT
def chat_gpt():
    speak("Sohbet GPT açılıyor.")
    webbrowser.open("https://chatgpt.com/")

#Copilot
def copilot():
    speak("Copilot açılıyor.")
    webbrowser.open("https://copilot.microsoft.com/chats/1HryXBrbzcipiL3JyPmu7")

#Tinkercad
def tinkercad():
    speak("Tinkercad açılıyor.")
    webbrowser.open("https://www.tinkercad.com/dashboard")

#Canva
def canva():
    speak("Canva açılıyor.")
    webbrowser.open("https://www.canva.com/?ysclid=mer6ayai5t454426814&continue_in_browser=true")

#Pivot Animator
def pivot_animator():
    speak("Canva açılıyor.")
    webbrowser.open("https://www.canva.com/?ysclid=mer6ayai5t454426814&continue_in_browser=true")

#Trading View
def trading_view():
    speak("Trading View açılıyor.")
    webbrowser.open("https://www.tradingview.com/")

#Binance TR
def binance_tr():
    speak("Binance TR açılıyor.")
    webbrowser.open("https://www.binance.tr/")

#Shopify
def shopify():
        speak("Shopify açılıyor.")
        webbrowser.open("https://admin.shopify.com/store/e1515a-ad/access_account/checkout")

#Eba
def eba():
    speak("Eba açılıyor.")
    webbrowser.open("https://ders.eba.gov.tr/ders/proxy/VCollabPlayer_v0.0.1062/index.html#/main/dashboard/3/9/0")

#Duolingo
def duolingo():
        speak("Duolingo açılıyor.")
        webbrowser.open("https://www.duolingo.com/learn")

#Çeviri
def ceviri():
    speak("Çeviri açılıyor.")
    webbrowser.open("https://www.yandex.com.tr/search/?text=%C3%A7eviri&clid=2411726&lr=104652")

#Google Arama
def google_search():
    ara = komut.replace("google", "").strip()
    webbrowser.open(f"https://www.google.com/search?q={ara}")
    speak(f"{ara} için Google'da arama yapılıyor.")

#URL Arama
def url_search():
    global search_text, search, search_but

#Wikipedia Arama
# Wikipedia Türkçe
wikipedia.set_lang("tr")
def wikipedia_search():
        konu = komut.replace("wikipedia", "").strip()
        bilgi = wiki_bilgi(konu)
        speak(bilgi)

#Youtube Arama
def youtube_search():
        aranacak = komut.replace("youtube", "").strip()
        youtube_ara(aranacak)

#Youtube Music
def youtube_music():
    speak("Beğendiğin müzikler açılıyor.")
    webbrowser.open("https://music.youtube.com/playlist?list=LM")

#Youtube Kanal
def youtube_kanal():
    speak("Youtube kanalın açılıyor.")
    webbrowser.open("https://www.youtube.com/@kodumun_erroru_")

#İnstagram
def instagram():
    speak("İnstagram açılıyor.")
    webbrowser.open("https://www.instagram.com/")

#WhatsApp
def whatsapp():
    speak("WhatsApp açılıyor.")
    webbrowser.open("https://web.whatsapp.com/")

#Telegram
def telegram():
    speak("Telegram açılıyor.")
    webbrowser.open("https://web.telegram.org/k/")

#Linkedln
def linkedln():
    speak("Linledln açılıyor.")
    webbrowser.open("https://www.linkedin.com/feed/")

#Gmail
def gmail():
    speak("Gmail açılıyor.")
    webbrowser.open("https://mail.google.com/mail/u/0/#inbox")

#Wi-Fi Açma Fonksiyonu
def wifi_on():
    os.system('netsh interface set interface "Wi-Fi" admin=enabled')

#Wi-Fi Kapama Fonksiyonu
def wifi_off():
    os.system('netsh interface set interface "Wi-Fi" admin=disabled')

#CMD
def cmd_baslat():

    try:
        subprocess.Popen("cmd.exe",creationflags=subprocess.CREATE_NEW_CONSOLE)
        speak("CMD açılıyor.")

    except Exception as e:
        speak("CMD açılamıyor.")

#Yeniden Başlat
def sistem_yeniden_baslat():
    cevap = messagebox.askyesno("Uyarı", "Bilgisayar yeniden başlatılacak. Emin misiniz?")
    if cevap:
        speak("Bilgisayar yeniden başlatılıyor.")
        subprocess.run("shutdown /r /t 5", shell=True)
    else:
        speak("Yeniden başlatma iptal edildi.")

#Bilgisayarı Kapat
def sistem_kapat():
    cevap = messagebox.askyesno("Warning", "Are you serious?")
    if cevap:
        speak("Turn of the computer.")
        subprocess.run("shutdown /s /t 5", shell=True)
    else:
        speak("Kapatma işlemi iptal edildi.")

#Ekran Kilitleme
def ekrani_kilitle():
    speak("Ekran kilitleniyor.")
    ctypes.windll.user32.LockWorkStation()

#Sistem Ses Ayarı
def sesi_ayarla(seviye):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(seviye, None)
    except Exception as e:
        speak("Ses ayarlanırken hata oluştu.")

#Kronometre
class Kronometre:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.İ.S. J4 Kronometre")
        self.saniye = 0
        self.durum = False
        
        self.zaman_label = tk.Label(self.root, text="00:00:00", font=("Helvetica", 40))
        self.zaman_label.pack(pady=20)
        
        self.baslat_buton = tk.Button(self.root, text="Başlat", command=self.baslat)
        self.baslat_buton.pack(side="left", padx=10)
        self.durdur_buton = tk.Button(self.root, text="Durdur", command=self.durdur)
        self.durdur_buton.pack(side="left", padx=10)
        self.sifirla_buton = tk.Button(self.root, text="Sıfırla", command=self.sifirla)
        self.sifirla_buton.pack(side="left", padx=10)
        
        self.guncelle_zaman()
        self.root.mainloop()

    def guncelle_zaman(self):
        saat = self.saniye // 3600
        dakika = (self.saniye % 3600) // 60
        saniye = self.saniye % 60
        self.zaman_label.config(text=f"{saat:02d}:{dakika:02d}:{saniye:02d}")
        if self.durum:
            self.saniye += 1
        self.root.after(1000, self.guncelle_zaman)
    
    def baslat(self):
        self.durum = True
    
    def durdur(self):
        self.durum = False
    
    def sifirla(self):
        self.durum = False
        self.saniye = 0
        self.zaman_label.config(text="00:00:00")

#Hesap Makinesi
def hesap_makinesi():
    subprocess.Popen("calc.exe")
    speak("Hesap Makinesi açılıyor.")

#Not Defteri
def not_defteri():
    subprocess.Popen("notepad.exe")
    speak("Not Defteri açılıyor.")

#Denetim Masası
def denetim_masası():
    speak("Denetim masası açılıyor.")
    subprocess.Popen("control.exe")

#Dosya Gezgini
def dosya_gezgini():
    speak("Dosya Gezgini açılıyor.")
    subprocess.Popen("explorer")

#Ayarlar
def ayarlar():
    speak("system settings on")
    subprocess.Popen("start ms-settings:", shell=True)

# --- QR Kod Oluşturucu ---
def create_qr_code(text, filename="qr_code.png"):
    """QR kod oluşturur"""
    if not HAS_QR:
        speak("QR kod kütüphanesi yüklü değil. pip install qrcode[pil] komutu ile yükleyin.")
        return None
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="cyan", back_color="black")
        img.save(filename)
        return filename
    except Exception as e:
        speak(f"QR kod oluşturulurken hata: {str(e)}")
        return None

def qr_code_gui():
    """QR kod oluşturma GUI"""
    qr_window = tk.Toplevel(windows)
    qr_window.title("QR Kod Oluşturucu")
    qr_window.geometry("500x400")
    qr_window.configure(bg="#0d1117")
    
    tk.Label(qr_window, text="QR Kod Oluşturucu", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(qr_window, text="Metin veya URL:", bg="#0d1117", fg="white").pack()
    entry = tk.Text(qr_window, height=5, width=50, bg="#161b22", fg="white")
    entry.pack(pady=10)
    
    def generate_qr():
        text = entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Uyarı", "Lütfen metin veya URL girin!")
            return
        
        filename = create_qr_code(text)
        if filename:
            messagebox.showinfo("Başarılı", f"QR kod oluşturuldu: {filename}")
            speak("QR kod oluşturuldu.")
    
    tk.Button(qr_window, text="QR Kod Oluştur", command=generate_qr,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- E-posta Gönderme ---
def send_email_gui():
    """E-posta gönderme GUI"""
    email_window = tk.Toplevel(windows)
    email_window.title("E-posta Gönder")
    email_window.geometry("600x500")
    email_window.configure(bg="#0d1117")
    
    tk.Label(email_window, text="E-posta Gönder", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(email_window, text="Alıcı:", bg="#0d1117", fg="white").pack()
    to_entry = tk.Entry(email_window, width=50, bg="#161b22", fg="white")
    to_entry.pack(pady=5)
    
    tk.Label(email_window, text="Konu:", bg="#0d1117", fg="white").pack()
    subject_entry = tk.Entry(email_window, width=50, bg="#161b22", fg="white")
    subject_entry.pack(pady=5)
    
    tk.Label(email_window, text="Mesaj:", bg="#0d1117", fg="white").pack()
    message_text = tk.Text(email_window, height=10, width=50, bg="#161b22", fg="white")
    message_text.pack(pady=5)
    
    def send_email():
        to_email = to_entry.get().strip()
        subject = subject_entry.get().strip()
        message = message_text.get("1.0", tk.END).strip()
        
        if not to_email or not subject or not message:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = "your_email@gmail.com"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            messagebox.showinfo("Bilgi", "E-posta gönderimi için SMTP ayarlarını yapılandırın.")
            speak("E-posta gönderimi için ayarlar gerekli.")
        except Exception as e:
            messagebox.showerror("Hata", f"E-posta gönderilemedi: {str(e)}")
            speak("E-posta gönderilemedi.")
    
    tk.Button(email_window, text="Gönder", command=send_email,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- WhatsApp Mesajı ---
def send_whatsapp_message(phone, message):
    """WhatsApp Web üzerinden mesaj gönderir"""
    try:
        phone = re.sub(r'\D', '', phone)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"
        webbrowser.open(url)
        speak("WhatsApp mesaj penceresi açılıyor.")
    except Exception as e:
        speak(f"WhatsApp mesajı gönderilemedi: {str(e)}")

def whatsapp_message_gui():
    """WhatsApp mesaj GUI"""
    wa_window = tk.Toplevel(windows)
    wa_window.title("WhatsApp Mesaj")
    wa_window.geometry("500x300")
    wa_window.configure(bg="#0d1117")
    
    tk.Label(wa_window, text="WhatsApp Mesaj Gönder", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(wa_window, text="Telefon Numarası (ülke kodu ile):", bg="#0d1117", fg="white").pack()
    phone_entry = tk.Entry(wa_window, width=40, bg="#161b22", fg="white")
    phone_entry.pack(pady=5)
    
    tk.Label(wa_window, text="Mesaj:", bg="#0d1117", fg="white").pack()
    message_text = tk.Text(wa_window, height=8, width=40, bg="#161b22", fg="white")
    message_text.pack(pady=5)
    
    def send_wa():
        phone = phone_entry.get().strip()
        message = message_text.get("1.0", tk.END).strip()
        if phone and message:
            send_whatsapp_message(phone, message)
        else:
            messagebox.showwarning("Uyarı", "Lütfen telefon ve mesaj girin!")
    
    tk.Button(wa_window, text="Gönder", command=send_wa,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- Şifre Yöneticisi ---
PASSWORD_FILE = "passwords.json"
KEY_FILE = "key.key"

def generate_key():
    """Şifreleme anahtarı oluşturur"""
    if not HAS_CRYPTO:
        return None
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    with open(KEY_FILE, 'rb') as f:
        return f.read()

def save_password(service, username, password):
    """Şifreyi güvenli şekilde kaydeder"""
    if not HAS_CRYPTO:
        speak("Şifre yöneticisi için cryptography kütüphanesi gerekli. pip install cryptography")
        return False
    try:
        key = generate_key()
        if not key:
            return False
        fernet = Fernet(key)
        
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}
        
        encrypted_password = fernet.encrypt(password.encode()).decode()
        data[service] = {
            'username': username,
            'password': encrypted_password
        }
        
        with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Şifre kaydedilemedi: {e}")
        return False

def get_password(service):
    """Şifreyi okur"""
    if not HAS_CRYPTO:
        return None, None
    try:
        key = generate_key()
        if not key:
            return None, None
        fernet = Fernet(key)
        
        if not os.path.exists(PASSWORD_FILE):
            return None, None
        
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if service not in data:
            return None, None
        
        encrypted_password = data[service]['password']
        password = fernet.decrypt(encrypted_password.encode()).decode()
        
        return data[service]['username'], password
    except Exception as e:
        print(f"Şifre okunamadı: {e}")
        return None, None

def password_manager_gui():
    """Şifre yöneticisi GUI"""
    if not HAS_CRYPTO:
        messagebox.showwarning("Uyarı", 
            "Şifre yöneticisi için cryptography kütüphanesi gerekli.\n\n"
            "Kurulum: pip install cryptography")
        speak("Şifre yöneticisi için cryptography kütüphanesi gerekli.")
        return
    
    pm_window = tk.Toplevel(windows)
    pm_window.title("Şifre Yöneticisi")
    pm_window.geometry("600x500")
    pm_window.configure(bg="#0d1117")
    
    tk.Label(pm_window, text="Şifre Yöneticisi", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(pm_window, text="Servis:", bg="#0d1117", fg="white").pack()
    service_entry = tk.Entry(pm_window, width=40, bg="#161b22", fg="white")
    service_entry.pack(pady=5)
    
    tk.Label(pm_window, text="Kullanıcı Adı:", bg="#0d1117", fg="white").pack()
    username_entry = tk.Entry(pm_window, width=40, bg="#161b22", fg="white")
    username_entry.pack(pady=5)
    
    tk.Label(pm_window, text="Şifre:", bg="#0d1117", fg="white").pack()
    password_entry = tk.Entry(pm_window, width=40, show="*", bg="#161b22", fg="white")
    password_entry.pack(pady=5)
    
    def save_pw():
        service = service_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if service and username and password:
            if save_password(service, username, password):
                messagebox.showinfo("Başarılı", "Şifre kaydedildi!")
                speak("Şifre kaydedildi.")
            else:
                messagebox.showerror("Hata", "Şifre kaydedilemedi!")
        else:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
    
    def load_pw():
        service = service_entry.get().strip()
        if service:
            username, password = get_password(service)
            if username and password:
                username_entry.delete(0, tk.END)
                username_entry.insert(0, username)
                password_entry.delete(0, tk.END)
                password_entry.insert(0, password)
                speak("Şifre yüklendi.")
            else:
                messagebox.showinfo("Bilgi", "Bu servis için kayıtlı şifre yok.")
        else:
            messagebox.showwarning("Uyarı", "Lütfen servis adı girin!")
    
    tk.Button(pm_window, text="Kaydet", command=save_pw,
              bg="#0d1117", fg="cyan").pack(side="left", padx=10, pady=10)
    tk.Button(pm_window, text="Yükle", command=load_pw,
              bg="#0d1117", fg="cyan").pack(side="left", padx=10, pady=10)

# --- Kamera/Mikrofon Kontrolü ---
def check_camera():
    """Kamera durumunu kontrol eder"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-PnpDevice | Where-Object {$_.Class -eq 'Camera'} | Select-Object Status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "OK" in result.stdout:
            return "Açık"
        return "Kapalı"
    except:
        return "Bilinmiyor"

def check_microphone():
    """Mikrofon durumunu kontrol eder"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-PnpDevice | Where-Object {$_.Class -eq 'AudioEndpoint'} | Select-Object Status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "OK" in result.stdout:
            return "Açık"
        return "Kapalı"
    except:
        return "Bilinmiyor"

def device_status_gui():
    """Cihaz durumu GUI"""
    ds_window = tk.Toplevel(windows)
    ds_window.title("Cihaz Durumu")
    ds_window.geometry("400x200")
    ds_window.configure(bg="#0d1117")
    
    tk.Label(ds_window, text="Cihaz Durumu", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    camera_status = check_camera()
    mic_status = check_microphone()
    
    tk.Label(ds_window, text=f"📷 Kamera: {camera_status}",
             bg="#0d1117", fg="white", font=("Arial", 12)).pack(pady=5)
    tk.Label(ds_window, text=f"🎤 Mikrofon: {mic_status}",
             bg="#0d1117", fg="white", font=("Arial", 12)).pack(pady=5)
    
    def refresh():
        camera_status = check_camera()
        mic_status = check_microphone()
        speak(f"Kamera {camera_status}, Mikrofon {mic_status}")
    
    tk.Button(ds_window, text="Yenile", command=refresh,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- Görüntü Analizi ---
def analyze_image(image_path):
    """Görüntüyü analiz eder"""
    try:
        if not HAS_QR:
            return "Görüntü analizi için PIL kütüphanesi gerekli."
        
        from PIL import Image
        img = Image.open(image_path)
        
        width, height = img.size
        mode = img.mode
        format_type = img.format
        
        info = f"Boyut: {width}x{height}\nMod: {mode}\nFormat: {format_type}"
        
        colors = img.getcolors(maxcolors=256*256*256)
        if colors:
            dominant_color = max(colors, key=lambda x: x[0])
            info += f"\nBaskın renk: {dominant_color[1]}"
        
        return info
    except Exception as e:
        return f"Hata: {str(e)}"

def image_analysis_gui():
    """Görüntü analizi GUI"""
    ia_window = tk.Toplevel(windows)
    ia_window.title("Görüntü Analizi")
    ia_window.geometry("500x400")
    ia_window.configure(bg="#0d1117")
    
    tk.Label(ia_window, text="Görüntü Analizi", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(ia_window, text="Görüntü Dosya Yolu:", bg="#0d1117", fg="white").pack()
    path_entry = tk.Entry(ia_window, width=50, bg="#161b22", fg="white")
    path_entry.pack(pady=5)
    
    result_text = tk.Text(ia_window, height=15, width=50, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def analyze():
        path = path_entry.get().strip()
        if path and os.path.exists(path):
            result = analyze_image(path)
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
            speak("Görüntü analiz edildi.")
        else:
            messagebox.showwarning("Uyarı", "Geçerli bir dosya yolu girin!")
    
    tk.Button(ia_window, text="Analiz Et", command=analyze,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- Ses Transkripsiyonu ---
def transcribe_audio(audio_file):
    """Ses dosyasını metne çevirir"""
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
        
        text = r.recognize_google(audio, language='tr-TR')
        return text
    except Exception as e:
        return f"Hata: {str(e)}"

def transcription_gui():
    """Ses transkripsiyonu GUI"""
    tr_window = tk.Toplevel(windows)
    tr_window.title("Ses Transkripsiyonu")
    tr_window.geometry("600x400")
    tr_window.configure(bg="#0d1117")
    
    tk.Label(tr_window, text="Ses Transkripsiyonu", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(tr_window, text="Ses Dosya Yolu:", bg="#0d1117", fg="white").pack()
    path_entry = tk.Entry(tr_window, width=50, bg="#161b22", fg="white")
    path_entry.pack(pady=5)
    
    result_text = tk.Text(tr_window, height=15, width=60, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def transcribe():
        path = path_entry.get().strip()
        if path and os.path.exists(path):
            result = transcribe_audio(path)
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", result)
            speak("Transkripsiyon tamamlandı.")
        else:
            messagebox.showwarning("Uyarı", "Geçerli bir ses dosyası yolu girin!")
    
    tk.Button(tr_window, text="Transkripsiyon Yap", command=transcribe,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- Ağ Haritası ---
def scan_network():
    """Yerel ağdaki cihazları tarar"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        
        devices = []
        for ip in list(network.hosts())[:10]:
            try:
                hostname = socket.gethostbyaddr(str(ip))[0]
                devices.append((str(ip), hostname))
            except:
                devices.append((str(ip), "Bilinmiyor"))
        
        return devices
    except Exception as e:
        return [("Hata", str(e))]

def network_map_gui():
    """Ağ haritası GUI"""
    nm_window = tk.Toplevel(windows)
    nm_window.title("Ağ Haritası")
    nm_window.geometry("600x400")
    nm_window.configure(bg="#0d1117")
    
    tk.Label(nm_window, text="Ağ Haritası", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    result_text = tk.Text(nm_window, height=20, width=70, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def scan():
        result_text.delete("1.0", tk.END)
        result_text.insert("1.0", "Taranıyor...\n")
        devices = scan_network()
        
        result_text.delete("1.0", tk.END)
        result_text.insert("1.0", "Yerel Ağ Cihazları:\n" + "="*50 + "\n")
        for ip, hostname in devices:
            result_text.insert(tk.END, f"IP: {ip:20s} Hostname: {hostname}\n")
        
        speak(f"{len(devices)} cihaz bulundu.")
    
    tk.Button(nm_window, text="Tara", command=scan,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- Bant Genişliği İzleme ---
def get_bandwidth_usage():
    """Gerçek zamanlı bant genişliği kullanımını alır"""
    try:
        stats = psutil.net_io_counters()
        return {
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv
        }
    except:
        return None

def bandwidth_monitor_gui():
    """Bant genişliği izleme GUI"""
    bm_window = tk.Toplevel(windows)
    bm_window.title("Bant Genişliği İzleme")
    bm_window.geometry("600x400")
    bm_window.configure(bg="#0d1117")
    
    tk.Label(bm_window, text="Bant Genişliği İzleme", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    result_text = tk.Text(bm_window, height=20, width=70, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def update_bandwidth():
        stats = get_bandwidth_usage()
        if stats:
            sent_mb = stats['bytes_sent'] / (1024 * 1024)
            recv_mb = stats['bytes_recv'] / (1024 * 1024)
            
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", 
                f"Gönderilen: {sent_mb:.2f} MB\n"
                f"Alınan: {recv_mb:.2f} MB\n"
                f"Paket Gönderilen: {stats['packets_sent']}\n"
                f"Paket Alınan: {stats['packets_recv']}\n"
            )
            bm_window.after(1000, update_bandwidth)
    
    update_bandwidth()

# --- MAC Adresi Arama ---
def lookup_mac(mac_address):
    """MAC adresinden üretici bilgisi alır"""
    try:
        mac = mac_address.replace(':', '').replace('-', '').upper()[:6]
        url = f"https://api.macvendors.com/{mac}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Bilinmiyor"
    except:
        return "Hata"

def mac_lookup_gui():
    """MAC adresi arama GUI"""
    ml_window = tk.Toplevel(windows)
    ml_window.title("MAC Adresi Arama")
    ml_window.geometry("500x300")
    ml_window.configure(bg="#0d1117")
    
    tk.Label(ml_window, text="MAC Adresi Arama", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(ml_window, text="MAC Adresi:", bg="#0d1117", fg="white").pack()
    mac_entry = tk.Entry(ml_window, width=40, bg="#161b22", fg="white")
    mac_entry.pack(pady=5)
    
    result_text = tk.Text(ml_window, height=10, width=50, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def lookup():
        mac = mac_entry.get().strip()
        if mac:
            vendor = lookup_mac(mac)
            result_text.delete("1.0", tk.END)
            result_text.insert("1.0", f"MAC: {mac}\nÜretici: {vendor}")
            speak(f"Üretici: {vendor}")
        else:
            messagebox.showwarning("Uyarı", "Lütfen MAC adresi girin!")
    
    tk.Button(ml_window, text="Ara", command=lookup,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- IP Geolocation ---
def ip_geolocation(ip_address):
    """IP adresinden konum bilgisi alır"""
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'country': data.get('country', 'N/A'),
                'region': data.get('regionName', 'N/A'),
                'city': data.get('city', 'N/A'),
                'isp': data.get('isp', 'N/A'),
                'lat': data.get('lat', 'N/A'),
                'lon': data.get('lon', 'N/A')
            }
        return None
    except:
        return None

def ip_geo_gui():
    """IP geolocation GUI"""
    ip_window = tk.Toplevel(windows)
    ip_window.title("IP Geolocation")
    ip_window.geometry("500x400")
    ip_window.configure(bg="#0d1117")
    
    tk.Label(ip_window, text="IP Geolocation", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(ip_window, text="IP Adresi:", bg="#0d1117", fg="white").pack()
    ip_entry = tk.Entry(ip_window, width=40, bg="#161b22", fg="white")
    ip_entry.pack(pady=5)
    
    result_text = tk.Text(ip_window, height=15, width=50, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def lookup_ip():
        ip = ip_entry.get().strip()
        if ip:
            geo = ip_geolocation(ip)
            if geo:
                result_text.delete("1.0", tk.END)
                result_text.insert("1.0",
                    f"Ülke: {geo['country']}\n"
                    f"Bölge: {geo['region']}\n"
                    f"Şehir: {geo['city']}\n"
                    f"ISP: {geo['isp']}\n"
                    f"Enlem: {geo['lat']}\n"
                    f"Boylam: {geo['lon']}\n"
                )
                speak(f"Konum: {geo['city']}, {geo['country']}")
            else:
                messagebox.showerror("Hata", "IP bilgisi alınamadı!")
        else:
            messagebox.showwarning("Uyarı", "Lütfen IP adresi girin!")
    
    tk.Button(ip_window, text="Ara", command=lookup_ip,
              bg="#0d1117", fg="cyan").pack(pady=10)

# --- Domain Bilgisi (Whois) ---
def domain_info(domain):
    """Domain whois bilgisi alır"""
    try:
        if HAS_WHOIS:
            w = whois.whois(domain)
            return {
                'domain': w.domain,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers
            }
        else:
            return {"info": "Whois kütüphanesi yüklü değil. pip install python-whois"}
    except Exception as e:
        return {"error": str(e)}

def domain_info_gui():
    """Domain bilgisi GUI"""
    di_window = tk.Toplevel(windows)
    di_window.title("Domain Bilgisi")
    di_window.geometry("600x400")
    di_window.configure(bg="#0d1117")
    
    tk.Label(di_window, text="Domain Bilgisi", font=("Arial", 16, "bold"),
             bg="#0d1117", fg="cyan").pack(pady=10)
    
    tk.Label(di_window, text="Domain:", bg="#0d1117", fg="white").pack()
    domain_entry = tk.Entry(di_window, width=50, bg="#161b22", fg="white")
    domain_entry.pack(pady=5)
    
    result_text = tk.Text(di_window, height=15, width=60, bg="#161b22", fg="white")
    result_text.pack(pady=10)
    
    def lookup_domain():
        domain = domain_entry.get().strip()
        if domain:
            info = domain_info(domain)
            result_text.delete("1.0", tk.END)
            if 'error' in info:
                result_text.insert("1.0", f"Hata: {info['error']}")
            else:
                for key, value in info.items():
                    result_text.insert(tk.END, f"{key}: {value}\n")
            speak("Domain bilgisi alındı.")
        else:
            messagebox.showwarning("Uyarı", "Lütfen domain adı girin!")
    
    tk.Button(di_window, text="Ara", command=lookup_domain,
              bg="#0d1117", fg="cyan").pack(pady=10)

def jarvis():
    global jarvis_dur
    jarvis_dur = False
    while not jarvis_dur:
        komut = listen()
        if not komut:
            continue

        if "jarvis" in komut:
            speak("Merhaba, sizi dinliyorum.")

        #Modlar 
        elif "stüdyo modu aç" in komut:
            stüdyo_mod_ac()

        elif "stüdyo modu kapat" in komut:
            stüdyo_mod_kapat()

        elif "odak modu aç" in komut:
            odak_mod_ac()

        elif "odak modu kapat" in komut:
            odak_mod_kapat()

        elif "ESP web" in komut:
            ESP_Web()

        # Röle kontrolleri
        elif "röle 1 aç" in komut:
            control_relay(1, "on")

        elif "röle 1 kapat" in komut:
            control_relay(1, "off")

        elif "röle 2 aç" in komut:
            control_relay(2, "on")

        elif "röle 2 kapat" in komut:
            control_relay(2, "off")

        elif "röle 3 aç" in komut:
            control_relay(3, "on")

        elif "röle 3 kapat" in komut:
            control_relay(3, "off")

        elif "röle 4 aç" in komut:
            control_relay(4, "on")

        elif "röle 4 kapat" in komut:
            control_relay(4, "off")
        
        elif "THT" in komut:
            tht()

        elif "RAT" in komut:
            rat()

        elif "VM" in komut:
            vm()

        elif "mors" in komut or "mor" in komut:
            run_gui()

        elif "sezar" in komut:
            sezar_gui_thread()

        elif "GitHub" in komut:
            git_hub()

        elif "code" in komut:
            vs_code()

        elif "VS" in komut:
            vs_2022()

        elif "cisco" in komut:
            cisco()

        elif "sohbet gpt" in komut:
            chat_gpt()

        elif "copilot" in komut:
            copilot()

        elif "tinkercad" in komut:
            tinkercad()

        elif "canva" in komut:
            canva()

        elif "pivot" in komut:
            pivot_animator()

        elif "trading" in komut:
            trading_view()

        elif "binance" in komut:
            binance_tr()

        elif "shopify" in komut:
            shopify()

        elif "eba" in komut:
            eba()

        elif "duo" in komut:
            duolingo()

        elif "çeviri" in komut:
            ceviri()

        elif "google" in komut:
            google_search()

        elif "URL" in komut:
            url_search()

        elif "wikipedia" in komut:
            wikipedia_search()

        elif "youtube" in komut:
            youtube_search()

        elif "müzik" in komut:
            youtube_music()

        elif "müzik durdur" in komut or "müzik dur" in komut or "duraklat" in komut:
            media_play_pause()

        elif "sonraki şarkı" in komut or "sonraki" in komut:
            media_next()

        elif "önceki şarkı" in komut or "önceki" in komut:
            media_previous()

        elif "kanal" in komut:
            youtube_kanal()

        elif "instagram" in komut:
            instagram()

        elif "whatsapp" in komut:
            whatsapp()

        elif "telegram" in komut:
            telegram()

        elif "linkedln" in komut:
            linkedln()

        elif "mail" in komut:
            gmail()

        elif "wifi aç" in komut:
            wifi_on()

        elif "wifi kapat" in komut:
            wifi_off()

        elif "CMD" in komut:
            cmd_baslat()

        elif "yeniden başlat" in komut:
            sistem_yeniden_baslat()

        elif "kapat" in komut:
            sistem_kapat()

        elif "ekran kilitle" in komut:
            ekrani_kilitle()

        elif "ses" in komut:
            sesi_ayarla()

        elif "kronometre" in komut:
            Kronometre()

        elif "hesap" in komut:
            hesap_makinesi()

        elif "not" in komut:
            not_defteri()

        elif "denetim" in komut:
            denetim_masası()

        elif "dosya" in komut:
            dosya_gezgini()

        elif "ayarlar" in komut:
            ayarlar()

        elif "qr kod" in komut or "qr code" in komut:
            qr_code_gui()

        elif "e-posta gönder" in komut or "email gönder" in komut:
            send_email_gui()

        elif "whatsapp mesaj" in komut or "whatsapp gönder" in komut:
            whatsapp_message_gui()

        elif "şifre yöneticisi" in komut or "password manager" in komut:
            password_manager_gui()

        elif "kamera durumu" in komut or "mikrofon durumu" in komut or "cihaz durumu" in komut:
            device_status_gui()

        elif "görüntü analiz" in komut or "image analysis" in komut:
            image_analysis_gui()

        elif "ses transkripsiyon" in komut or "audio transcription" in komut:
            transcription_gui()

        elif "ağ haritası" in komut or "network map" in komut or "ağ tarama" in komut:
            network_map_gui()

        elif "bant genişliği" in komut or "bandwidth" in komut:
            bandwidth_monitor_gui()

        elif "mac adresi" in komut or "mac lookup" in komut:
            mac_lookup_gui()

        elif "ip konum" in komut or "ip geolocation" in komut:
            ip_geo_gui()

        elif "domain bilgisi" in komut or "whois" in komut:
            domain_info_gui()

        elif "tv aç" in komut or "televizyon aç" in komut:
            threading.Thread(target=tv_wake_on_lan, daemon=True).start()
            speak("TV açılıyor, Wake-on-LAN gönderildi.")

        elif "tv kapat" in komut or "televizyon kapat" in komut:
            threading.Thread(target=lambda: samsung_tv_komut("KEY_POWER"), daemon=True).start()
            speak("TV kapatılıyor.")

        elif "tv kumanda" in komut or "samsung tv" in komut:
            tv_gui()

        elif "uzak bilgisayar" in komut or "ssh" in komut:
            uzak_pc_gui()

        elif "telefon sunucu" in komut or "flask" in komut:
            flask_sunucu_baslat()
            speak(f"Telefon kontrol sunucusu başlatıldı. Port {FLASK_PORT}.")

        elif "gemini" in komut or "yapay zeka" in komut or "sohbet" in komut:
            gemini_gui()

        elif "ağ güvenlik" in komut or "yabancı cihaz" in komut or "ag izle" in komut:
            yabanci_cihaz_gui()

        elif komut.startswith("jarvis "):
            soru = komut.replace("jarvis ", "", 1).strip()
            if soru:
                def _sor_ve_soyle(s=soru):
                    yanit = gemini_sor(s)
                    speak(yanit)
                    write_output(f"Gemini: {yanit}")
                threading.Thread(target=_sor_ve_soyle, daemon=True).start()

# BAŞLAT
windows.mainloop()