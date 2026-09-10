import json
import os
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# JSON dosyasından dünya veritabanını yükle
json_yolu = os.path.join(os.path.dirname(__file__), "dunya_sehirleri.json")
try:
    with open(json_yolu, "r", encoding="utf-8") as f:
        DunyaVeritabani = json.load(f)
except Exception as e:
    print(f"JSON okuma hatasi: {e}")
    DunyaVeritabani = {}

# Varsayılan başlangıç konumu
aktif_konum = {
    "ulke": "Türkiye",
    "sehir": "Bursa"
}

def hava_durumu_acikla(weathercode):
    try:
        code = int(weathercode)
    except:
        code = 0

    if code == 0:
        return "Gunesli", "☀️"
    elif code in [1, 2, 3]:
        return "Bulutlu", "☁️"
    elif code in [45, 48]:
        return "Sisli", "🌫️"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Yagmurlu", "🌧️"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "Karli", "❄️"
    elif code in [95, 96, 99]:
        return "Firtina", "⚡"
    else:
        return "Parcali Bulutlu", "⛅"

def open_meteo_veri_cek(lat, lon):
    # Hem modern current hem klasik current_weather parametresi gönderiyoruz
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&current_weather=true"
    headers = {
        "User-Agent": "TrexWeatherStation/1.0 (ESP32-Project)"
    }
    
    res = requests.get(url, headers=headers, timeout=6)
    data = res.json()
    
    sicaklik = None
    weathercode = 0

    # 1. Öncelik: Modern current bloğu
    if "current" in data:
        c = data["current"]
        sicaklik = c.get("temperature_2m")
        weathercode = c.get("weather_code", c.get("weathercode", 0))

    # 2. Öncelik: Geleneksel current_weather bloğu (yedek)
    if sicaklik is None and "current_weather" in data:
        cw = data["current_weather"]
        sicaklik = cw.get("temperature")
        weathercode = cw.get("weathercode", 0)

    if sicaklik is None:
        sicaklik = 0

    return round(float(sicaklik)), int(weathercode)

@app.route("/")
def index():
    sirali_ulkeler = sorted(list(DunyaVeritabani.keys()))
    return render_template(
        "index.html",
        ulkeler=sirali_ulkeler,
        aktif_ulke=aktif_konum["ulke"],
        aktif_sehir=aktif_konum["sehir"]
    )

@app.route("/api/sehirler")
def sehirleri_getir():
    ulke = request.args.get("ulke", "Türkiye")
    if ulke in DunyaVeritabani:
        return jsonify(sorted(list(DunyaVeritabani[ulke].keys())))
    return jsonify([])

@app.route("/api/hava")
def hava_durumu_getir():
    ulke = request.args.get("ulke", aktif_konum["ulke"])
    sehir = request.args.get("sehir", aktif_konum["sehir"])
    
    try:
        lat = DunyaVeritabani[ulke][sehir]["lat"]
        lon = DunyaVeritabani[ulke][sehir]["lon"]
    except KeyError:
        lat, lon = 40.1828, 29.0665
        sehir = "Bursa"
        ulke = "Türkiye"

    try:
        sicaklik, weathercode = open_meteo_veri_cek(lat, lon)
        durum, ikon = hava_durumu_acikla(weathercode)
        
        return jsonify({
            "sehir": sehir,
            "ulke": ulke,
            "sicaklik": sicaklik,
            "durum": durum,
            "ikon": ikon,
            "weathercode": weathercode
        })
    except Exception as e:
        print(f"Hava API Hatasi: {e}")
        return jsonify({"hata": str(e), "sicaklik": 0, "durum": "Bilinmiyor", "ikon": "❓"}), 500

@app.route("/api/kaydet", methods=["POST"])
@app.route("/api/sehir-sec", methods=["POST"])
def konumu_kaydet():
    req = request.get_json(silent=True) or {}
    ulke = req.get("ulke")
    sehir = req.get("sehir")

    if ulke in DunyaVeritabani and sehir in DunyaVeritabani[ulke]:
        aktif_konum["ulke"] = ulke
        aktif_konum["sehir"] = sehir
        return jsonify({"durum": "basarili", "ulke": ulke, "sehir": sehir})
    
    return jsonify({"durum": "hata", "mesaj": "Gecersiz konum"}), 400

@app.route("/api/cihaz-hava")
def cihaz_hava():
    ulke = aktif_konum["ulke"]
    sehir = aktif_konum["sehir"]
    
    try:
        lat = DunyaVeritabani[ulke][sehir]["lat"]
        lon = DunyaVeritabani[ulke][sehir]["lon"]
    except KeyError:
        lat, lon = 40.1828, 29.0665
        sehir = "Bursa"
        ulke = "Türkiye"

    try:
        temp, code = open_meteo_veri_cek(lat, lon)
        durum, _ = hava_durumu_acikla(code)

        # LilyGO ekranı için Türkçe karakter temizliği
        temiz_sehir = sehir.replace("ı", "i").replace("İ", "I").replace("ş", "s").replace("Ş", "S").replace("ğ", "g").replace("Ğ", "G").replace("ü", "u").replace("Ü", "U").replace("ö", "o").replace("Ö", "O").replace("ç", "c").replace("Ç", "C")
        temiz_ulke = ulke.replace("ü", "u").replace("Ü", "U").replace("İ", "I").replace("ı", "i")

        return jsonify({
            "sehir": temiz_sehir,
            "ulke": temiz_ulke,
            "sicaklik": temp,
            "durum": durum,
            "code": code
        })
    except Exception as e:
        print(f"Cihaz API Hatasi: {e}")
        return jsonify({"hata": str(e), "sicaklik": 0, "durum": "Hata", "code": 0}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)