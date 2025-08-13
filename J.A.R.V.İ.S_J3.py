import speech_recognition as sr
import pyttsx3
import tkinter as tk
import threading
import wikipedia
import requests
import webbrowser
import datetime
import re
import subprocess
from tkinter import messagebox
import ctypes
import os
import time
import winsound
from tkinter import ttk

# Ses kontrol için pycaw
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Sistem sesi ayarlayan fonksiyon
def sesi_ayarla(seviye):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(seviye, None)
    except Exception as e:
        speak("Ses ayarlanırken hata oluştu.")

# Konuşma motoru başlatma ve ayarlar
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Wikipedia Türkçe
wikipedia.set_lang("tr")

# Hava durumu API
API_KEY = "925863c13ed89d69602b4e4c4f53d33c"

# Temalar
THEMES = {
    "Açık": {
        "bg": "white",
        "fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "button_bg": "lightgrey",
        "button_fg": "black"
    },
    "Koyu": {
        "bg": "#2e2e2e",
        "fg": "white",
        "text_bg": "#3c3f41",
        "text_fg": "white",
        "button_bg": "#555555",
        "button_fg": "white"
    }
}

current_theme = "Açık"

# Ana pencere
windows = tk.Tk()
windows.title("J.A.R.V.I.S J3 (Beta)")
windows.geometry("1920x1080")

def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    theme = THEMES[theme_name]
    
    windows.config(bg=theme["bg"])
    label_title.config(bg=theme["bg"], fg=theme["fg"])
    label_features.config(bg=theme["bg"], fg=theme["fg"])
    features.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["fg"])
    out.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["fg"])
    buton_frame.config(bg=theme["bg"])
    btn_start.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
    btn_stop.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
    btn_settings.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])

# Başlık
label_title = tk.Label(windows, text="J.A.R.V.I.S", font=("Arial", 30, "bold"))
label_title.place(x=750, y=0)

# Özellikler başlığı ve kutusu
label_features = tk.Label(windows, text="Özellikler", font=("Arial", 20, "bold"))
label_features.place(x=70, y=0)

features = tk.Text(windows, font=("Arial", 12))
features.place(x=20, y=40, width=250, height=600)
features_list = [
    "Stüdyo S1", "Stüdyo Modu kapat", "VS code", "Turk Hack Team", "Oracle VM",
    "Google Arama", "Youtube Arama", "WhatsApp", "Gmail", "Udemy", "Wikipedia Arama",
    "Yeniden Başlatma", "Rahatsız Etme aç", "Rahatsız Etme kapat", "Bilgisayarı kapatma",
    "Ekran Kilitleme", "Hava Durumu", "Saat", "Alarm", "Tarih", "Hesap makinesi",
    "Not defteri", "Sistem Ses seviyesi ayarı", "Çeviri", "Beğendiğim müzikler",
    "Youtube kanal", "Sohbet GPT", "Denetim Masası", "Ayarlar", "J2 Ayarları(Ses Desteği Yok!)","Durdur"
]
for item in features_list:
    features.insert(tk.END, item + "\n")
features.config(state='disabled')

# Çıktı kutusu
out = tk.Text(windows, font=("Arial", 12))
out.place(x=300, y=40, width=1200, height=600)
out.config(state='disabled')

def write_output(text):
    out.config(state='normal')
    out.insert(tk.END, text + "\n")
    out.see(tk.END)
    out.config(state='disabled')

def speak(text):
    write_output("Jarvis: " + text)
    engine.say(text)
    engine.runAndWait()

def ekrani_kilitle():
    speak("Ekran kilitleniyor.")
    ctypes.windll.user32.LockWorkStation()

def stüdyo_mod_ac():
    speak("Studio Mode opens.")
    webbrowser.open("https://music.youtube.com/playlist?list=LM")
    # VSCode yolu kendine göre değiştir
    try:
        subprocess.Popen("C:\\Users\\KODUMUN_ERRORU_\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
    except:
        speak("VS Code not opens.")
    webbrowser.open("https://www.turkhackteam.org/")
    webbrowser.open("https://www.youtube.com/")
    webbrowser.open("https://web.whatsapp.com/")
    webbrowser.open("https://www.udemy.com/")
    webbrowser.open("https://chatgpt.com/")
    subprocess.Popen("calc.exe")
    subprocess.Popen("notepad.exe")

def stüdyo_mod_kapat():
    speak("Stüdyo modu off")
    for prog in ["Code.exe", "notepad.exe", "Calc.exe", "chrome.exe", "msedge.exe"]:
        os.system(f"taskkill /f /im {prog}")

def sistem_kapat():
    cevap = messagebox.askyesno("Warning", "Are you serious?")
    if cevap:
        speak("Turn of the computer.")
        subprocess.run("shutdown /s /t 5", shell=True)
    else:
        speak("Kapatma işlemi iptal edildi.")

def sistem_yeniden_baslat():
    cevap = messagebox.askyesno("Uyarı", "Bilgisayar yeniden başlatılacak. Emin misiniz?")
    if cevap:
        speak("Bilgisayar yeniden başlatılıyor.")
        subprocess.run("shutdown /r /t 5", shell=True)
    else:
        speak("Yeniden başlatma iptal edildi.")

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

def youtube_ara(aranacak):
    if not aranacak:
        speak("Ne aramamı istersin?")
        return
    url = f"https://www.youtube.com/results?search_query={aranacak.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"Youtube'da {aranacak} aranıyor.")

def wiki_bilgi(konu):
    try:
        bilgi = wikipedia.summary(konu, sentences=2)
        sayfa = wikipedia.page(konu).url
        webbrowser.open(sayfa)
        return bilgi
    except:
        return "Bilgi bulunamadı."

def hava_durumu_cek(sehir):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={API_KEY}&lang=tr&units=metric"
    response = requests.get(url).json()
    try:
        durum = response["weather"][0]["description"]
        sicaklik = response["main"]["temp"]
        return f"{sehir} için hava durumu: {durum}, sıcaklık: {sicaklik}°C"
    except:
        return "Hava durumu alınamadı."

jarvis_dur = False

def jarvis():
    global jarvis_dur
    jarvis_dur = False
    while not jarvis_dur:
        komut = listen()
        if not komut:
            continue

        if "jarvis" in komut:
            speak("Merhaba, sizi dinliyorum.")

        elif "stüdyo modu aç" in komut:
            stüdyo_mod_ac()

        elif "stüdyo modu kapat" in komut:
            stüdyo_mod_kapat()

        elif "vs code" in komut:
            speak("VS Code açılıyor.")
            try:
                subprocess.Popen("C:\\Users\\KODUMUN_ERRORU_\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
            except:
                speak("VS Code açılamadı.")

        elif "tht" in komut:
            speak("Turk Hack Team açılıyor.")
            webbrowser.open("https://www.turkhackteam.org/")

        elif "not defteri" in komut:
            speak("Not defteri açılıyor.")
            subprocess.Popen("notepad.exe")

        elif "kilitle" in komut:
            ekrani_kilitle()

        elif "bilgisayarı kapat" in komut:
            sistem_kapat()

        elif "yeniden başlat" in komut:
            sistem_yeniden_baslat()

        elif "rahatsız etme aç" in komut:
            speak("Rahatsız etme modu açılıyor.")
            subprocess.run(["powershell", "-Command",
                "New-ItemProperty -Path HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value 0 -PropertyType DWORD -Force"])

        elif "rahatsız etme kapat" in komut:
            speak("Rahatsız etme modu kapatılıyor.")
            subprocess.run(["powershell", "-Command",
                "New-ItemProperty -Path HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings -Name NOC_GLOBAL_SETTING_TOASTS_ENABLED -Value 1 -PropertyType DWORD -Force"])

        elif "hava durumu" in komut:
            sehir = "izmir"
            match = re.search(r'hava durumu (?:için )?(.+)', komut)
            if match:
                sehir = match.group(1).strip()
            bilgi = hava_durumu_cek(sehir)
            speak(bilgi)

        elif "whatsapp" in komut:
            speak("WhatsApp açılıyor.")
            webbrowser.open("https://web.whatsapp.com/")

        elif "mail" in komut:
            speak("Gmail açılıyor.")
            webbrowser.open("https://mail.google.com/mail/u/0/#inbox")

        elif "wikipedia" in komut:
            konu = komut.replace("wikipedia", "").strip()
            bilgi = wiki_bilgi(konu)
            speak(bilgi)

        elif "udemy" in komut:
            speak("Udemy açılıyor.")
            webbrowser.open("https://www.udemy.com/")

        elif "youtube" in komut:
            aranacak = komut.replace("youtube", "").strip()
            youtube_ara(aranacak)

        elif "beğendiğim müzikler" in komut:
            speak("Beğendiğin müzikler açılıyor.")
            webbrowser.open("https://music.youtube.com/playlist?list=LM")

        elif "yt kanal" in komut:
            speak("Youtube kanalın açılıyor.")
            webbrowser.open("https://www.youtube.com/@kodumun_erroru_")

        elif "sohbet gpt" in komut:
            speak("Sohbet GPT açılıyor.")
            webbrowser.open("https://chatgpt.com/")

        elif "çeviri" in komut:
            speak("Çeviri açılıyor.")
            webbrowser.open("https://translate.google.com/")

        elif "google" in komut:
            ara = komut.replace("google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={ara}")
            speak(f"{ara} için Google'da arama yapılıyor.")

        elif "saat" in komut:
            saat = datetime.datetime.now().strftime("%H:%M")
            speak(f"Saat şu anda {saat}")

        elif "alarm kur" in komut:
            speak("Alarm saatini söyle. Örnek: 07:30")
            alarm_cevap = listen()
            try:
                alarm_kur(alarm_cevap)
            except:
                speak("Saat formatı hatalı, lütfen tekrar deneyin.")

        elif "tarih" in komut:
            bugun = datetime.datetime.now().strftime("%d %B %Y %A")
            speak(f"Bugünün tarihi: {bugun}")

        elif "hesap makinesi" in komut:
            speak("Hesap makinesi açılıyor.")
            subprocess.Popen("calc.exe")

        elif "ses seviyesi" in komut or "volume" in komut:
            try:
                yuzde = int(re.search(r"%?(\d+)", komut).group(1))
                if 0 <= yuzde <= 100:
                    seviye = yuzde / 100
                    sesi_ayarla(seviye)
                    speak(f"Ses seviyesi %{yuzde} olarak ayarlandı.")
                else:
                    speak("Lütfen 0 ile 100 arasında bir değer verin.")
            except:
                speak("Ses seviyesi anlaşılamadı. Örnek: 50 yüzde")

        elif "ayarlar" in komut:
            speak("system settings on")
            subprocess.Popen("start ms-settings:", shell=True)


        elif "denetim masası" in komut:
            speak("Denetim masası açılıyor.")
            subprocess.Popen("control.exe")

        elif "durdur" in komut or "stop" in komut:
            stop_jarvis()

        else:
            speak("Bu komutu bilmiyorum.")

def alarm_kur(alarm_saati):
    def alarm_bekle():
        speak(f"Alarm {alarm_saati} için kuruldu.")
        hedef = datetime.datetime.strptime(alarm_saati, "%H:%M").time()
        while True:
            simdi = datetime.datetime.now().time()
            if simdi.hour == hedef.hour and simdi.minute == hedef.minute:
                speak("Alarm! Kalkma zamanı!")
                # istersen buraya alarm sesi koyabilirsin
                break
            time.sleep(10)

    threading.Thread(target=alarm_bekle, daemon=True).start()

def restart():
    t = threading.Thread(target=jarvis, daemon=True)
    t.start()

def stop_jarvis():
    global jarvis_dur
    jarvis_dur = True
    speak("J.A.R.V.I.S durduruldu.")

buton_frame = tk.Frame(windows)
buton_frame.place(x=20, y=650, width=400, height=60)

btn_start = tk.Button(buton_frame, text="Başlat", font=("Arial", 12, "bold"), command=restart)
btn_start.grid(row=0, column=0, padx=25, pady=25)

btn_stop = tk.Button(buton_frame, text="Durdur", font=("Arial", 12, "bold"), command=stop_jarvis)
btn_stop.grid(row=0, column=1, padx=25, pady=25)

btn_settings = tk.Button(windows, text="Ayarlar", font=("Arial", 12, "bold"), command=lambda: settings_window())
btn_settings.place(x=1430, y=5)

def settings_window():
    settings_win = tk.Toplevel(windows)
    settings_win.title("Ayarlar")
    settings_win.geometry("300x250")
    settings_win.config(bg=THEMES[current_theme]["bg"])

    tk.Label(settings_win, text="Tema:", font=("Arial", 12), bg=THEMES[current_theme]["bg"], fg=THEMES[current_theme]["fg"]).pack(pady=10)
    tema_var = tk.StringVar(value=current_theme)
    tema_combo = ttk.Combobox(settings_win, textvariable=tema_var, values=list(THEMES.keys()), state="readonly")
    tema_combo.pack(pady=5)

    def kaydet():
        apply_theme(tema_var.get())
        settings_win.destroy()

    tk.Button(settings_win, text="Kaydet", command=kaydet).pack(pady=15)

    def surum_bilgisi():
        versiyon_pencere = tk.Toplevel(settings_win)
        versiyon_pencere.title("Uygulama Sürümü")
        versiyon_pencere.geometry("250x100")
        versiyon_pencere.config(bg=THEMES[current_theme]["bg"])
        tk.Label(
            versiyon_pencere,
            text="J.A.R.V.I.S J3 (Beta)\n STÜDYO S2",
            font=("Arial", 14),
            bg=THEMES[current_theme]["bg"],
            fg=THEMES[current_theme]["fg"]
        ).pack(expand=True, pady=20)

    btn_versiyon = tk.Button(settings_win, text="Uygulama Sürümü", font=("Arial", 12), bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], command=surum_bilgisi)
    btn_versiyon.pack()

apply_theme(current_theme)

windows.mainloop()
