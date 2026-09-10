from flask import Flask, render_template, jsonify, request
import requests
import json

app = Flask(__name__)

# =====================================================
# ULKE / SEHIR LISTESI (countries.json dosyasindan okunur)
# =====================================================
with open("countries.json", "r", encoding="utf-8") as f:
    UlkeSehirListesi = json.load(f)

# Kartin okuyacagi son secim (bellek ici hafiza)
sonSecim = {
    "ulke": "Turkey",
    "sehir": "Bursa",
    "lat": 40.1826,
    "lon": 29.0665,
    "sicaklik": None,
    "durum": None,
    "ikon": ""
}

# =====================================================
# WMO HAVA DURUMU KODUNU ACIKLAMA + IKONA CEVIR
# =====================================================
def hava_durumu_bilgisi(weathercode):
    kodlar = {
        0: ("Acik", "☀️"),
        1: ("Az Bulutlu", "🌤️"),
        2: ("Parcali Bulutlu", "⛅"),
        3: ("Bulutlu", "☁️"),
        45: ("Sisli", "🌫️"), 48: ("Sisli", "🌫️"),
        51: ("Cisenti", "🌦️"), 53: ("Cisenti", "🌦️"), 55: ("Cisenti", "🌦️"),
        56: ("Donan Cisenti", "🌧️"), 57: ("Donan Cisenti", "🌧️"),
        61: ("Yagmurlu", "🌧️"), 63: ("Yagmurlu", "🌧️"), 65: ("Yagmurlu", "🌧️"),
        66: ("Donan Yagmur", "🌧️"), 67: ("Donan Yagmur", "🌧️"),
        71: ("Kar Yagisli", "🌨️"), 73: ("Kar Yagisli", "🌨️"), 75: ("Kar Yagisli", "🌨️"),
        77: ("Kar Taneli", "🌨️"),
        80: ("Saganak Yagmur", "🌧️"), 81: ("Saganak Yagmur", "🌧️"), 82: ("Saganak Yagmur", "🌧️"),
        85: ("Kar Saganagi", "🌨️"), 86: ("Kar Saganagi", "🌨️"),
        95: ("Gok Gurultulu Firtina", "⛈️"),
        96: ("Dolulu Firtina", "⛈️"), 99: ("Dolulu Firtina", "⛈️")
    }
    return kodlar.get(weathercode, ("Bilinmiyor", "❓"))

# =====================================================
# BIR SEHRIN KOORDINATINI VE HAVA DURUMUNU GETIR (ortak fonksiyon)
# =====================================================
def sehir_hava_verisi(sehir):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={sehir}&count=1"
    geo_res = requests.get(geo_url, timeout=10).json()

    if "results" not in geo_res or len(geo_res["results"]) == 0:
        return None

    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    hava_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    hava_res = requests.get(hava_url, timeout=10).json()

    sicaklik = hava_res["current_weather"]["temperature"]
    weathercode = hava_res["current_weather"]["weathercode"]
    durum, ikon = hava_durumu_bilgisi(weathercode)

    return {
        "lat": lat,
        "lon": lon,
        "sicaklik": round(sicaklik),
        "durum": durum,
        "ikon": ikon
    }

# =====================================================
# ANA SAYFA
# =====================================================
@app.route("/")
def index():
    ulkeler = sorted(list(UlkeSehirListesi.keys()))
    return render_template(
        "index.html",
        ulkeler=ulkeler,
        aktif_ulke=sonSecim["ulke"],
        aktif_sehir=sonSecim["sehir"]
    )

# =====================================================
# SECILEN ULKENIN SEHIRLERINI DONDUR
# =====================================================
@app.route("/api/sehirler")
def sehirleri_getir():
    ulke = request.args.get("ulke")
    if ulke in UlkeSehirListesi:
        return jsonify(sorted(UlkeSehirListesi[ulke]))
    return jsonify([])

# =====================================================
# BIR SEHRIN ANLIK HAVA DURUMUNU GETIR (dashboard onizleme icin)
# =====================================================
@app.route("/api/hava")
def hava_durumu_getir():
    ulke = request.args.get("ulke")
    sehir = request.args.get("sehir")

    if not ulke or not sehir:
        return jsonify({"hata": "ulke ve sehir parametreleri gerekli"}), 400

    try:
        veri = sehir_hava_verisi(sehir)
        if veri is None:
            return jsonify({"hata": "Koordinat bulunamadi"}), 404

        return jsonify({
            "ulke": ulke,
            "sehir": sehir,
            "lat": veri["lat"],
            "lon": veri["lon"],
            "sicaklik": veri["sicaklik"],
            "durum": veri["durum"],
            "ikon": veri["ikon"]
        })

    except Exception as e:
        return jsonify({"hata": str(e)}), 500

# =====================================================
# SEHIR SECIMINI KAYDET / KARTA GONDER
# =====================================================
@app.route("/api/kaydet", methods=["POST"])
def sehir_kaydet():
    veri = request.get_json()
    ulke = veri.get("ulke")
    sehir = veri.get("sehir")

    if not ulke or not sehir:
        return jsonify({"durum": "hata", "mesaj": "ulke ve sehir gerekli"}), 400

    if ulke not in UlkeSehirListesi or sehir not in UlkeSehirListesi[ulke]:
        return jsonify({"durum": "hata", "mesaj": "Gecersiz ulke/sehir"}), 400

    try:
        havaVerisi = sehir_hava_verisi(sehir)
        if havaVerisi is None:
            return jsonify({"durum": "hata", "mesaj": "Koordinat bulunamadi"}), 404

        sonSecim["ulke"] = ulke
        sonSecim["sehir"] = sehir
        sonSecim["lat"] = havaVerisi["lat"]
        sonSecim["lon"] = havaVerisi["lon"]
        sonSecim["sicaklik"] = havaVerisi["sicaklik"]
        sonSecim["durum"] = havaVerisi["durum"]
        sonSecim["ikon"] = havaVerisi["ikon"]

        return jsonify({"durum": "basarili", "ulke": ulke, "sehir": sehir})

    except Exception as e:
        return jsonify({"durum": "hata", "mesaj": str(e)}), 500

# =====================================================
# KARTIN OKUYACAGI SON SECIM
# =====================================================
@app.route("/api/mevcut-secim")
def mevcut_secimi_getir():
    return jsonify(sonSecim)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)