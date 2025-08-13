import speech_recognition as sr
import pyttsx3
import tkinter as tk
import threading
import wikipedia
import requests
import webbrowser
import datetime
import re

# Ses kontrol için pycaw
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Sistem sesini ayarlayan fonksiyon
def sesi_ayarla(seviye):  # seviye: 0.0 - 1.0
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(seviye, None)
    except:
        speak("Sistem sesi ayarlanırken bir hata oluştu.")

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

# Arayüz (GUI)
windows = tk.Tk()
windows.title("J.A.R.V.I.S J1")
windows.geometry("500x450")

tk.Label(windows, text="J.A.R.V.I.S", font=("Arial", 30, "bold")).place(x=150, y=0)

# Çıktı kutusu
out = tk.Text(windows, font=("Arial", 12))
out.place(x=50, y=50, width=400, height=230)
out.config(state='disabled')  # Kullanıcı yazamasın

# Çıktı yazma fonksiyonu
def write_output(text):
    out.config(state='normal')
    out.insert(tk.END, text + "\n")
    out.see(tk.END)
    out.config(state='disabled')

# Konuşturma fonksiyonu
def speak(text):
    write_output("Jarvis: " + text)
    engine.say(text)
    engine.runAndWait()

# Dinleme fonksiyonu
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        write_output("Dinleniyor...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio, language='tr-TR')
            write_output("Sen: " + command)
            return command.lower()
        except sr.UnknownValueError:
            speak("Sizi anlayamadım, lütfen tekrar eder misiniz?")
            return ""
        except sr.RequestError:
            speak("İnternet bağlantısı yok veya Google servisine ulaşılamıyor.")
            return ""

# YouTube arama
def youtube(aranacak):
    if not aranacak:
        speak("Ne aramamı istersiniz?")
        return
    url = f"https://www.youtube.com/results?search_query={aranacak.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"{aranacak} için YouTube'da arama yapılıyor.")

# Wikipedia özeti ve sayfa açma
def wiki_bilgi(konu):
    try:
        bilgi = wikipedia.summary(konu, sentences=2)
        sayfa = wikipedia.page(konu).url
        webbrowser.open(sayfa)
        return bilgi
    except:
        return "Bu konuda bilgi bulamadım."

# Hava durumu bilgisi
def hava_durumu_cek(sehir):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={API_KEY}&lang=tr&units=metric"
    response = requests.get(url).json()
    try:
        durum = response["weather"][0]["description"]
        sicaklik = response["main"]["temp"]
        return f"{sehir} için hava durumu: {durum}, sıcaklık: {sicaklik} derece"
    except:
        return "Hava durumu bilgisi alınamadı."

# J.A.R.V.I.S motoru kontrolü
jarvis_dur = False

def jarvis():
    global jarvis_dur
    jarvis_dur = False
    while not jarvis_dur:
        komut = listen()
        if not komut:
            continue

        if "merhaba" in komut:
            speak("Merhaba! Hazırım.")

        elif "hava durumu" in komut:
            sehir = "izmir"  # Varsayılan şehir
            pattern = r'hava durumu (?:için )?(.+)'
            match = re.search(pattern, komut)
            if match:
                sehir = match.group(1).strip()
            bilgi = hava_durumu_cek(sehir)
            speak(bilgi)

        elif "wikipedia" in komut:
            konu = komut.replace("wikipedia", "").strip()
            bilgi = wiki_bilgi(konu)
            speak(bilgi)

        elif "youtube" in komut:
            aranacak = komut.replace("youtube", "").strip()
            youtube(aranacak)

        elif "google" in komut:
            ara = komut.replace("google", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={ara}")
            speak(f"{ara} için Google'da arama yapılıyor.")

        elif "saat" in komut:
            saat = datetime.datetime.now().strftime("%H:%M")
            speak(f"Şu an saat {saat}")

        elif "tarih" in komut:
            bugun = datetime.datetime.now().strftime("%d %B %Y %A")
            speak(f"Bugünün tarihi {bugun}")

        elif "ses" in komut:
            try:
                yuzde = int(re.search(r"%?(\d+)", komut).group(1))
                if 0 <= yuzde <= 100:
                    seviye = yuzde / 100
                    sesi_ayarla(seviye)
                    speak(f"Ses seviyesi yüzde {yuzde} olarak ayarlandı.")
                else:
                    speak("Lütfen 0 ile 100 arasında bir değer söyleyin.")
            except:
                speak("Ses seviyesini anlayamadım. Örnek olarak yüzde 50 diyebilirsiniz.")

        else:
            speak("Bu komutu bilmiyorum.")

# Başlatma fonksiyonu
def restart():
    t = threading.Thread(target=jarvis)
    t.start()

# Durdurma fonksiyonu
def stop_jarvis():
    global jarvis_dur
    jarvis_dur = True
    speak("J.A.R.V.I.S durduruldu.")

# Butonlar
tk.Button(windows, text="Başlat", font=("Arial", 14, "bold"), command=restart).place(x=150, y=300, width=100, height=100)
tk.Button(windows, text="Durdur", font=("Arial", 14, "bold"), command=stop_jarvis).place(x=250, y=300, width=100, height=100)

# Arayüzü çalıştır
windows.mainloop()
