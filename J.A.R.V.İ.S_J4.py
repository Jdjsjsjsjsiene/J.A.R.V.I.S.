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

# 3. GUI kütüphaneleri
import tkinter as tk
from tkinter import ttk, messagebox

ESP_IP = "192.168.1.106"

# =========================
# SES MOTORU
# =========================
engine = pyttsx3.init()
engine.setProperty("rate", 150)

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import tkinter as tk

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


def speak(text):
    threading.Thread(target=lambda: engine.say(text) or engine.runAndWait(), daemon=True).start()

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
    font=("Arial", 18, "bold"),
    fg="cyan",
    bg="#111827"
)
lbl_features.pack(pady=10)

features_box = tk.Text(
    left_panel,
    bg="#0d1117",
    fg="white",
    font=("Consolas", 11),
    width=30
)
features_box.pack(fill="both", expand=True, padx=10, pady=10)

features_list = [
    "Stüdyo S2", "Stüdyo Modu Kapat", "Odak O1", "Odak Modu Kapat", "Start_up T1", 
    "----------------------------",
    "ESP Web", "Röleleri Açma-Kapatma", 
    "----------------------------",
    "Turk Hack Team", "RAT Kontrol Programı", "Oracle VM", "Morse Haberleşme(Beta)", "Sezar Şifreleme", "Github", 
    "----------------------------",
    "VS Code", "VS 2022", "Cisco Packet Tracer", 
    "----------------------------",
    "Cursor","Sohbet GPT", "Copilot", 
    "----------------------------",
    "Tinkercad", "Canva", "Pivot Animator", 
    "----------------------------",
    "Trading View", "Binance TR", "Shopify", 
    "----------------------------",
    "Eba", "Duolingo", "Çeviri", 
    "----------------------------",
    "Google Arama", "URL Arama", "Wikipedia Arama", "Youtube Arama", "Beğendiğim Müzikler", "Müzik Durdur/Başlat", "Sonraki Şarkı", "Önceki Şarkı", "YT Kanal", "İnstagram", "WhatsApp", "WhatsApp Mesaj", "Telegram", "Linkedln", "Gmail","QR Kod Oluşturucu", "E-posta Gönderme", "Şifre Yöneticisi", 
    "----------------------------",
    "Wi-Fi Açma", "Wi-Fi Kapatma","Ağ Haritası", "Bant Genişliği İzleme", "MAC Adresi Arama", "IP Geolocation", "Domain Bilgisi", 
    "----------------------------",
    "CMD", "Yeniden Başlat", "Bilgisayarı Kapat", "Ekran Kilitleme", "Sistem Ses Seviyesi Ayarı", "Ekran Parlaklığı Ayarı", "Rahatsız Etme Aç", "Rahatsız Etme Kapat", 
    "----------------------------",
    "Hava Durumu", "Saat", "Alarm", "Kronometre","Tarih", "Hesap Makinesi", "Not Defteri", 
    "----------------------------",
    "Kamera/Mikrofon Kontrolü", "Görüntü Analizi", "Ses Transkripsiyonu",
    "----------------------------",
    "Denetim Masası", "Dosya Gezgini", "Ayarlar", "Durdur"
]

for item in features_list:
    features_box.insert("end", f"• {item}\n")

features_box.config(state="disabled")

def restart():
    t = threading.Thread(target=jarvis, daemon=True)
    t.start()

def stop_jarvis():
    global jarvis_dur
    jarvis_dur = True
    speak("J.A.R.V.I.S durduruldu.")

start_but = tk.Button(
    left_panel,
    text="Başlat",
    bg="#0d1117",
    fg="white",
    font=("Consolas", 21),
    width=2,
    command=restart
)

start_but.pack(fill="both", expand=True, padx=10, pady=10)

stop_but = tk.Button(
    left_panel,
    text="Durdur",
    bg="#0d1117",
    fg="white",
    font=("Consolas", 21),
    width=2,
    command=stop_jarvis
)

stop_but.pack(fill="both", expand=True, padx=10, pady=10)



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

log_box = tk.Text(
    center_panel,
    bg="#0d1117",
    fg="white",
    font=("Consolas", 12)
)

log_box.pack(fill="both", expand=True, padx=20, pady=20)
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

def write_output(text):
    log_box.config(state='normal')
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)
    log_box.config(state='disabled')

def speak(text):
    write_output("Jarvis: " + text)
    speak_queue.put(text) 

# =========================
# SAĞ PANEL
# =========================
right_panel = tk.Frame(main_frame, bg="#111827", width=300)
right_panel.pack(side="right", fill="y")

# === BAŞLIK ===
device_conn_text = tk.Label(
    right_panel,
    text="Cihaz Durumları",
    font=("Arial", 13, "bold"),   # 18 → 13
    fg="cyan",
    bg="#111827"
)
device_conn_text.pack(pady=(6, 2))


# === TEXT + SCROLLBAR FRAME ===
device_frame = tk.Frame(right_panel, bg="#0d1117")
device_frame.pack(fill="both", expand=True, padx=8, pady=6)

# === CİHAZ LİSTESİ ===
device_conn = tk.Text(
    device_frame,
    bg="#0d1117",
    fg="white",
    font=("Consolas", 11),   # 11 → 9
    width=30,              # 30 → 22
    height=1,
    bd=0,
)
device_conn.pack(side="left", fill="both", expand=True)

# === CİHAZLAR ===
device_list = [
    "J.A.R.V.I.S_Watch_W1",
    "J.A.R.V.I.S_F_I (ESP Web)",
    "J.A.R.V.I.S_TV",
    "Xiaomi Redmi Note 13 Pro",
    "Xiaomi Redmi Note 12 Pro",
    "Oppo A3",
    "Ana Sistem",
    "Eray_Laptop",
    "Samsung LED 49",
    "Kali",
    "Deney_Win11"
]

for item in device_list:
    device_conn.insert("end", f"• {item}\n")

device_conn.config(state="disabled")


net_data = tk.Text(
    right_panel,
    bg="#0d1117",
    fg="white",
    font=("Consolas", 11),
    width=30,
    height=10
)
net_data.pack(fill="both", expand=True, padx=10, pady=10)
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

    down, up, sping = last_speed
    sent_mb, recv_mb = get_network_usage()
    wifi_signal = get_wifi_signal()
    link_speed = get_link_speed()

    net_data.config(state="normal")
    net_data.delete("1.0", "end")

    net_data.insert("end", "NETWORK STATUS\n")
    net_data.insert("end", "-" * 30 + "\n")
    net_data.insert("end", f"Ağ     : {adapter}\n")
    if adapter_name != "-":
        net_data.insert("end", f"Kart   : {adapter_name[:20]}\n")
    net_data.insert("end", f"SSID   : {wifi}\n")
    if wifi_signal != "-":
        net_data.insert("end", f"Sinyal : {wifi_signal}\n")
    if link_speed != "-":
        net_data.insert("end", f"Hız   : {link_speed}\n")
    
    net_data.insert("end", "-" * 30 + "\n")
    net_data.insert("end", f"IPv4   : {ipv4}\n")
    net_data.insert("end", f"IPv6   : {ipv6}\n")
    net_data.insert("end", f"MAC    : {mac}\n")
    
    if gateway != "-":
        net_data.insert("end", f"Gateway: {gateway}\n")
    if subnet != "-":
        net_data.insert("end", f"Subnet : {subnet}\n")
    
    if dns1 != "-":
        net_data.insert("end", f"DNS 1  : {dns1}\n")
    if dns2 != "-":
        net_data.insert("end", f"DNS 2  : {dns2}\n")

    net_data.insert("end", "-" * 30 + "\n")
    net_data.insert("end", f"Dış IP : {get_public_ip()}\n")
    net_data.insert("end", f"Ping   : {get_ping()}\n")

    net_data.insert("end", "\nNETWORK USAGE\n")
    net_data.insert("end", "-" * 30 + "\n")
    net_data.insert("end", f"Gönderilen: {sent_mb}\n")
    net_data.insert("end", f"Alınan    : {recv_mb}\n")

    net_data.insert("end", "\nINTERNET SPEED\n")
    net_data.insert("end", "-" * 30 + "\n")
    net_data.insert("end", f"Download : {down}\n")
    net_data.insert("end", f"Upload   : {up}\n")
    net_data.insert("end", f"Lat      : {sping}\n")

    net_data.config(state="disabled")
    windows.after(5000, update_network_panel)

update_network_panel()

# ---- SAAT ----
clock_label = tk.Label(
    center_panel,
    font=("Orbitron", 22),
    fg="cyan",
    bg="#111827"
)
clock_label.pack(pady=10)

def update_clock():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    clock_label.after(1000, update_clock)

update_clock()

# ---- TARİH ----
date_label = tk.Label(
    center_panel,
    font=("Orbitron", 22),
    fg="cyan",
    bg="#111827"
)
date_label.pack(pady=10)

def update_date():
    date_label.config(
        text=datetime.datetime.now().strftime("%d.%m.%Y")
    )
    date_label.after(60000, update_date)

update_date()

# ---- CPU / RAM / GPU ----
sys_label = tk.Label(
    center_panel,
    font=("Consolas", 12),
    fg="white",
    bg="#111827"
)
sys_label.pack(pady=10)

def get_gpu_usage():
    """GPU kullanımını alır (NVIDIA için)"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            gpu_usage = result.stdout.strip()
            return f"GPU: {gpu_usage}%"
        return "GPU: N/A"
    except:
        # NVIDIA GPU yoksa veya hata varsa
        try:
            # Alternatif: WMI ile GPU bilgisi
            import wmi
            w = wmi.WMI()
            gpu_info = w.Win32_VideoController()[0]
            if gpu_info:
                return f"GPU: {gpu_info.Name[:20]}"
        except:
            pass
        return "GPU: N/A"

def update_system_info():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    gpu_info = get_gpu_usage()
    sys_label.config(text=f"CPU: {cpu}%\nRAM: {ram}%\n{gpu_info}")
    sys_label.after(1000, update_system_info)

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
    bg="#111827",
    width=280,
    height=180,
    highlightbackground="cyan",
    highlightthickness=1
)
weather_frame.pack(padx=10)
weather_frame.pack_propagate(False)

weather_title = tk.Label(
    weather_frame,
    text="🌦️ HAVA DURUMU",
    font=("Orbitron", 16, "bold"),
    fg="cyan",
    bg="#111827"
)
weather_title.pack(pady=8)

weather_label = tk.Label(
    weather_frame,
    font=("Consolas", 11),
    fg="white",
    bg="#111827",
    justify="left",
    anchor="w"
)
weather_label.pack(pady=10)

def update_weather():
    global _last_weather_ok, _last_weather_ok_at

    w = get_weather(WEATHER_DEFAULT_CITY)
    now = datetime.datetime.now()

    if w.get("ok"):
        _last_weather_ok = w
        _last_weather_ok_at = now
        show = w
        status_line = f"Güncel  : {now.strftime('%H:%M')}"
    else:
        # son başarılı veri varsa onu göster, hata mesajını alta ekle
        show = _last_weather_ok
        if _last_weather_ok_at:
            status_line = f"Son OK  : {_last_weather_ok_at.strftime('%H:%M')}  | Hata: {w.get('error','-')}"
        else:
            status_line = f"Hata    : {w.get('error','Hava durumu alınamadı')}"

    if not show:
        weather_label.config(text=status_line)
    else:
        def fmt(label, value, unit=""):
            v = "-" if value is None or value == "" else str(value)
            if unit and v != "-":
                v = f"{v} {unit}"
            return f"{label:<9}: {v}"

        city_txt = f"{show.get('city','-')}"
        if show.get("country"):
            city_txt += f", {show.get('country')}"

        lines = [
            f"{'Konum':<9}: {city_txt}",
            fmt("Durum", show.get("desc") or "-", ""),
            fmt("Sıcaklık", show.get("temp"), "°C"),
            fmt("Hissed.", show.get("feels"), "°C"),
            fmt("Min/Max", f"{show.get('temp_min','-')}/{show.get('temp_max','-')}", "°C"),
            fmt("Nem", show.get("humidity"), "%"),
            fmt("Basınç", show.get("pressure"), "hPa"),
            fmt("Rüzgar", show.get("wind_kmh"), "km/h"),
            fmt("Görüş", show.get("visibility_km"), "km"),
            status_line
        ]
        weather_label.config(text="\n".join(lines))

    windows.after(600000, update_weather)  # 10 dk

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
volume_frame = tk.Frame(right_panel, bg="#111827", bd=2, relief="solid")
volume_frame.pack(pady=5)

volume_label = tk.Label(
    volume_frame,
    text="🔊 Ses Seviyesi",
    font=("Orbitron", 14),
    fg="cyan",
    bg="#111827"
)
volume_label.pack(pady=5)

volume_slider = tk.Scale(
    volume_frame,
    from_=0,
    to=100,
    orient="horizontal",
    command=set_volume,
    length=200,
    bg="#111827",
    fg="cyan",
    troughcolor="#1f2933",
    highlightthickness=0
)
volume_slider.set(int(volume.GetMasterVolumeLevelScalar() * 100))
volume_slider.pack(padx=10, pady=10)

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
media_frame = tk.Frame(right_panel, bg="#111827", bd=2, relief="solid")
media_frame.pack(pady=5)

media_label = tk.Label(
    media_frame,
    text="🎵 Medya Kontrol",
    font=("Orbitron", 14),
    fg="cyan",
    bg="#111827"
)
media_label.pack(pady=5)

# Butonlar için frame
media_buttons_frame = tk.Frame(media_frame, bg="#111827")
media_buttons_frame.pack(pady=5)

# Önceki buton
prev_button = tk.Button(
    media_buttons_frame,
    text="⏮️",
    font=("Arial", 16),
    bg="#0d1117",
    fg="cyan",
    width=3,
    command=media_previous,
    relief="flat",
    activebackground="#161b22",
    activeforeground="white"
)
prev_button.grid(row=0, column=0, padx=3)

# Play/Pause buton
play_pause_button = tk.Button(
    media_buttons_frame,
    text="⏯️",
    font=("Arial", 16),
    bg="#0d1117",
    fg="cyan",
    width=3,
    command=media_play_pause,
    relief="flat",
    activebackground="#161b22",
    activeforeground="white"
)
play_pause_button.grid(row=0, column=1, padx=3)

# Sonraki buton
next_button = tk.Button(
    media_buttons_frame,
    text="⏭️",
    font=("Arial", 16),
    bg="#0d1117",
    fg="cyan",
    width=3,
    command=media_next,
    relief="flat",
    activebackground="#161b22",
    activeforeground="white"
)
next_button.grid(row=0, column=2, padx=3)

#Röle Kontrol Fonksiyonu
def control_relay(relay, state):
    try:
        url = f"{ESP_IP}/relay{relay}/{state}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            speak(f"Röle {relay} { 'açıldı' if state=='on' else 'kapatıldı' }")
        else:
            speak("Bağlantı hatası oluştu.")
    except Exception as e:
        speak("ESP32'ye bağlanılamadı.")

#Stüdyo Modları
def stüdyo_mod_ac():
    speak("Studio Mode opens.")
    webbrowser.open("https://music.youtube.com/playlist?list=LM")
    try:
        subprocess.Popen("C:\\Users\\KODUMUN_ERRORU_\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
    except:
        speak("VS Code not opens.")
    webbrowser.open(ESP_IP)
    webbrowser.open("https://www.turkhackteam.org/")
    webbrowser.open("https://www.youtube.com/")
    webbrowser.open("https://web.whatsapp.com/")
    webbrowser.open("https://www.udemy.com/")
    webbrowser.open("https://chatgpt.com/")
    subprocess.Popen("calc.exe")
    subprocess.Popen("notepad.exe")
    control_relay(1, "on")
    time.sleep(2)
    control_relay(2, "on")
    time.sleep(2)
    control_relay(3, "on")
    time.sleep(2)
    control_relay(4, "on")

def stüdyo_mod_kapat():
    speak("Stüdyo modu off")
    for prog in ["notepad.exe", "Calc.exe", "chrome.exe", "msedge.exe"]:
        os.system(f"taskkill /f /im {prog}")
    control_relay(1, "off")
    time.sleep(2)
    control_relay(2, "off")
    time.sleep(2)
    control_relay(3, "off")
    time.sleep(2)
    control_relay(4, "off")   

#Odak Modları
def odak_mod_ac():
    speak("Odak modu on")
    webbrowser.open(ESP_IP)
    webbrowser.open("https://www.udemy.com/")
    webbrowser.open("https://chatgpt.com/")
    webbrowser.open("https://www.youtube.com/")
    webbrowser.open("https://web.whatsapp.com/")
    subprocess.Popen("calc.exe")
    webbrowser.open("https://music.youtube.com/playlist?list=LM")
    control_relay(1, "off")
    time.sleep(2)
    control_relay(2, "off")
    time.sleep(2)
    control_relay(3, "off")
    time.sleep(2)
    control_relay(4, "off")

def odak_mod_kapat():
    speak("Odak modu off")
    for prog in ["Calc.exe", "chrome.exe", "msedge.exe"]:
        os.system(f"taskkill /f /im {prog}")
    control_relay(1, "off")
    time.sleep(2)
    control_relay(2, "off")
    time.sleep(2)
    control_relay(3, "off")
    time.sleep(2)
    control_relay(4, "off")      

#ESP_Web
def ESP_Web():
    webbrowser.open(ESP_IP)
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

# BAŞLAT
windows.mainloop()