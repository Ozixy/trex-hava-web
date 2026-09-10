import json
import os
from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# =====================================================
# SEHIR VERITABANI (sehirler.json dosyasindan okunur)
# =====================================================
JSON_DOSYA_ADI = "sehirler.json"
json_yolu = os.path.join(os.path.dirname(__file__), JSON_DOSYA_ADI)

try:
    with open(json_yolu, "r", encoding="utf-8") as f:
        DunyaVeritabani = json.load(f)
except Exception as e:
    print(f"JSON okuma hatasi: {e}")
    DunyaVeritabani = {}

# Kart ve web icin aktif secili konum bellegi
aktif_konum = {
    "ulke": "Türkiye",
    "sehir": "Bursa"
}

def hava_durumu_acikla(weathercode):
    if weathercode == 0:
        return "Gunesli", "☀️"
    elif weathercode in [1, 2, 3]:
        return "Bulutlu", "☁️"
    elif weathercode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Yagmurlu", "🌧️"
    elif weathercode in [71, 73, 75, 77, 85, 86]:
        return "Karli", "❄️"
    elif weathercode in [95, 96, 99]:
        return "Firtina", "⚡"
    else:
        return "Parcali Bulutlu", "⛅"

def acik_meteo_verisi_cek(lat, lon):
    # Sadece standart 'current' parametresi kullanıyoruz (400 hatası almaz)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
    
    headers = {
        "User-Agent": "TrexWeatherApp/1.0"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    
    # API cevabını konsola yazdır (Render Logs'ta görebilmek için)
    print(f"Meteo API Yaniti ({lat}, {lon}): {data}")
    
    current = data.get("current", {})
    temp = current.get("temperature_2m")
    code = current.get("weather_code")
    
    if temp is None:
        raise ValueError(f"Sicaklik alinamadi, donen veri: {data}")
        
    sicaklik = round(float(temp))
    weathercode = int(code) if code is not None else 0
    
    return sicaklik, weathercode
    except Exception as e:
        print(f"Open-Meteo Baglanti Hatasi: {e}")
        # Hata durumunda 0 dondurup ekrani dondurmesin
        return 20, 1

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
        temp, code = acik_meteo_verisi_cek(lat, lon)
        durum, _ = hava_durumu_acikla(code)

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
        print(f"[HATA] Hava verisi islenirken sorun cikti: {e}")
        return jsonify({"hata": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)