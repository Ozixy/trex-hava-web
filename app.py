import os
import json
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# =====================================================
# SEHIR VERITABANI (sehirler.json dosyasindan okunur)
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_yolu = os.path.join(BASE_DIR, "sehirler.json")

try:
    with open(json_yolu, "r", encoding="utf-8") as f:
        DunyaVeritabani = json.load(f)
    print("sehirler.json basariyla yuklendi.")
except Exception as e:
    print(f"JSON okuma hatasi: {e}")
    DunyaVeritabani = {}

# Kart ve web icin aktif secili konum bellegi
aktif_konum = {
    "ulke": "Türkiye",
    "sehir": "Bursa"
}

def turkce_karakter_temizle(metin: str) -> str:
    ceviri = str.maketrans({
        "ı": "i", "İ": "I", "ş": "s", "Ş": "S",
        "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U",
        "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"
    })
    return metin.translate(ceviri)

def hava_durumu_acikla(weathercode):
    if weathercode == 0:
        return "Gunesli", "☀️"
    elif weathercode in [1, 2, 3]:
        return "Bulutlu", "☁️"
    elif weathercode in [45, 48]:
        return "Sisli", "🌫️"
    elif weathercode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Yagmurlu", "🌧️"
    elif weathercode in [71, 73, 75, 77, 85, 86]:
        return "Karli", "❄️"
    elif weathercode in [95, 96, 99]:
        return "Firtina", "⚡"
    else:
        return "Parcali Bulutlu", "⛅"

def acik_meteo_verisi_cek(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
    headers = {
        "User-Agent": "TrexWeatherApp/1.0"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    current = data.get("current", {})
    temp = current.get("temperature_2m")
    code = current.get("weather_code")
    
    if temp is None:
        raise ValueError(f"Sicaklik verisi alinamadi, API yaniti: {data}")
        
    sicaklik = round(float(temp))
    weathercode = int(code) if code is not None else 0
    return sicaklik, weathercode

def koordinat_bul(ulke, sehir):
    try:
        konum = DunyaVeritabani[ulke][sehir]
        return konum["lat"], konum["lon"], ulke, sehir
    except KeyError:
        return 40.1828, 29.0665, "Türkiye", "Bursa"

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
    istenen_ulke = request.args.get("ulke", aktif_konum["ulke"])
    istenen_sehir = request.args.get("sehir", aktif_konum["sehir"])

    lat, lon, ulke, sehir = koordinat_bul(istenen_ulke, istenen_sehir)

    try:
        sicaklik, weathercode = acik_meteo_verisi_cek(lat, lon)
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
        print(f"[HATA /api/hava]: {e}")
        return jsonify({"hata": str(e)}), 500

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
    lat, lon, ulke, sehir = koordinat_bul(aktif_konum["ulke"], aktif_konum["sehir"])

    try:
        temp, code = acik_meteo_verisi_cek(lat, lon)
        durum, _ = hava_durumu_acikla(code)

        temiz_sehir = turkce_karakter_temizle(sehir)
        temiz_ulke = turkce_karakter_temizle(ulke)

        return jsonify({
            "sehir": temiz_sehir,
            "ulke": temiz_ulke,
            "sicaklik": temp,
            "durum": durum,
            "code": code
        })
    except Exception as e:
        print(f"[HATA /api/cihaz-hava]: {e}")
        return jsonify({"hata": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)