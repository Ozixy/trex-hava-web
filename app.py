from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# LilyGO kartının okuyacağı sunucu tarafındaki aktif konum belleği
aktif_konum = {
    "ulke": "Türkiye",
    "sehir": "Bursa"
}

DunyaVeritabani = {
    "Türkiye": {
        "Adana": {"lat": 37.0000, "lon": 35.3213},
        "Adıyaman": {"lat": 37.7648, "lon": 38.2786},
        "Afyonkarahisar": {"lat": 38.7507, "lon": 30.5567},
        "Ağrı": {"lat": 39.7191, "lon": 43.0503},
        "Aksaray": {"lat": 38.3687, "lon": 34.0370},
        "Amasya": {"lat": 40.6499, "lon": 35.8353},
        "Ankara": {"lat": 39.9334, "lon": 32.8597},
        "Antalya": {"lat": 36.8841, "lon": 30.7056},
        "Ardahan": {"lat": 41.1105, "lon": 42.7022},
        "Artvin": {"lat": 41.1828, "lon": 41.8183},
        "Aydın": {"lat": 37.8444, "lon": 27.8458},
        "Balıkesir": {"lat": 39.6484, "lon": 27.8826},
        "Bartın": {"lat": 41.6344, "lon": 32.3375},
        "Batman": {"lat": 37.8812, "lon": 41.1351},
        "Bayburt": {"lat": 40.2552, "lon": 40.2249},
        "Bilecik": {"lat": 40.1451, "lon": 29.9796},
        "Bingöl": {"lat": 38.8851, "lon": 40.4980},
        "Bitlis": {"lat": 38.4006, "lon": 42.1095},
        "Bolu": {"lat": 40.7350, "lon": 31.6061},
        "Burdur": {"lat": 37.7268, "lon": 30.2885},
        "Bursa": {"lat": 40.1828, "lon": 29.0665},
        "Çanakkale": {"lat": 40.1553, "lon": 26.4142},
        "Çankırı": {"lat": 40.6013, "lon": 33.6134},
        "Çorum": {"lat": 40.5506, "lon": 34.9556},
        "Denizli": {"lat": 37.7765, "lon": 29.0864},
        "Diyarbakır": {"lat": 37.9144, "lon": 40.2306},
        "Düzce": {"lat": 40.8438, "lon": 31.1565},
        "Edirne": {"lat": 41.6771, "lon": 26.5557},
        "Elazığ": {"lat": 38.6810, "lon": 39.2264},
        "Erzincan": {"lat": 39.7500, "lon": 39.5000},
        "Erzurum": {"lat": 39.9000, "lon": 41.2700},
        "Eskişehir": {"lat": 39.7767, "lon": 30.5206},
        "Gaziantep": {"lat": 37.0662, "lon": 37.3833},
        "Giresun": {"lat": 40.9128, "lon": 38.3895},
        "Gümüşhane": {"lat": 40.4386, "lon": 39.4793},
        "Hakkari": {"lat": 37.5833, "lon": 43.7333},
        "Hatay": {"lat": 36.4018, "lon": 36.3498},
        "Iğdır": {"lat": 39.9167, "lon": 44.0333},
        "Isparta": {"lat": 37.7648, "lon": 30.5566},
        "İstanbul": {"lat": 41.0082, "lon": 28.9784},
        "İzmir": {"lat": 38.4192, "lon": 27.1287},
        "Kahramanmaraş": {"lat": 37.5858, "lon": 36.9371},
        "Karabük": {"lat": 41.2061, "lon": 32.6204},
        "Karaman": {"lat": 37.1759, "lon": 33.2287},
        "Kars": {"lat": 40.6014, "lon": 43.0975},
        "Kastamonu": {"lat": 41.3887, "lon": 33.7827},
        "Kayseri": {"lat": 38.7312, "lon": 35.4787},
        "Kilis": {"lat": 36.7184, "lon": 37.1212},
        "Kırıkkale": {"lat": 39.8468, "lon": 33.5153},
        "Kırklareli": {"lat": 41.7333, "lon": 27.2167},
        "Kırşehir": {"lat": 39.1425, "lon": 34.1709},
        "Kocaeli": {"lat": 40.7654, "lon": 29.9408},
        "Konya": {"lat": 37.8667, "lon": 32.4833},
        "Kütahya": {"lat": 39.4167, "lon": 29.9833},
        "Malatya": {"lat": 38.3552, "lon": 38.3095},
        "Manisa": {"lat": 38.6191, "lon": 27.4289},
        "Mardin": {"lat": 37.3212, "lon": 40.7245},
        "Mersin": {"lat": 36.8000, "lon": 34.6333},
        "Muğla": {"lat": 37.2153, "lon": 28.3636},
        "Muş": {"lat": 38.9462, "lon": 41.4910},
        "Nevşehir": {"lat": 38.6939, "lon": 34.7145},
        "Niğde": {"lat": 37.9667, "lon": 34.6833},
        "Ordu": {"lat": 40.9839, "lon": 37.8764},
        "Osmaniye": {"lat": 37.0742, "lon": 36.2478},
        "Rize": {"lat": 41.0201, "lon": 40.5234},
        "Sakarya": {"lat": 40.7569, "lon": 30.3783},
        "Samsun": {"lat": 41.2867, "lon": 36.3300},
        "Siirt": {"lat": 37.9333, "lon": 41.9500},
        "Sinop": {"lat": 42.0231, "lon": 35.1531},
        "Sivas": {"lat": 39.7477, "lon": 37.0179},
        "Şanlıurfa": {"lat": 37.1591, "lon": 38.7969},
        "Şırnak": {"lat": 37.5164, "lon": 42.4611},
        "Tekirdağ": {"lat": 40.9833, "lon": 27.5167},
        "Tokat": {"lat": 40.3167, "lon": 36.5500},
        "Trabzon": {"lat": 41.0015, "lon": 39.7178},
        "Tunceli": {"lat": 39.1079, "lon": 39.5401},
        "Uşak": {"lat": 38.6823, "lon": 29.4082},
        "Van": {"lat": 38.4891, "lon": 43.4089},
        "Yalova": {"lat": 40.6500, "lon": 29.9000},
        "Yozgat": {"lat": 39.8181, "lon": 34.8147},
        "Zonguldak": {"lat": 41.4564, "lon": 31.7987}
    },
    "Almanya": {
        "Berlin": {"lat": 52.5200, "lon": 13.4050},
        "Münih": {"lat": 48.1351, "lon": 11.5820},
        "Frankfurt": {"lat": 50.1109, "lon": 8.6821},
        "Hamburg": {"lat": 53.5511, "lon": 9.9937},
        "Köln": {"lat": 50.9375, "lon": 6.9603}
    },
    "Fransa": {
        "Paris": {"lat": 48.8566, "lon": 2.3522},
        "Marsilya": {"lat": 43.2965, "lon": 5.3698},
        "Lyon": {"lat": 45.7640, "lon": 4.8357},
        "Nice": {"lat": 43.7102, "lon": 7.2620}
    },
    "İngiltere": {
        "Londra": {"lat": 51.5074, "lon": -0.1278},
        "Manchester": {"lat": 53.4808, "lon": -2.2426},
        "Birmingham": {"lat": 52.4862, "lon": -1.8904},
        "Edinburgh": {"lat": 55.9533, "lon": -3.1883}
    },
    "İtalya": {
        "Roma": {"lat": 41.9028, "lon": 12.4964},
        "Milano": {"lat": 45.4642, "lon": 9.1900},
        "Venedik": {"lat": 45.4408, "lon": 12.3155},
        "Napoli": {"lat": 40.8518, "lon": 14.2681}
    },
    "İspanya": {
        "Madrid": {"lat": 40.4168, "lon": -3.7038},
        "Barselona": {"lat": 41.3851, "lon": 2.1734},
        "Valensiya": {"lat": 39.4699, "lon": -0.3763}
    },
    "Hollanda": {
        "Amsterdam": {"lat": 52.3676, "lon": 4.9041},
        "Rotterdam": {"lat": 51.9244, "lon": 4.4777},
        "Lahey": {"lat": 52.0705, "lon": 4.3007}
    },
    "İzlanda": {
        "Reykjavik": {"lat": 64.1466, "lon": -21.9426}
    }
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

@app.route("/")
def index():
    sirali_ulkeler = sorted(DunyaVeritabani.keys())
    return render_template("index.html", ulkeler=sirali_ulkeler, aktif_ulke=aktif_konum["ulke"], aktif_sehir=aktif_konum["sehir"])

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

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data.get("current", {})
        sicaklik = current.get("temperature_2m", 0)
        weathercode = current.get("weathercode", 0)
        durum, ikon = hava_durumu_acikla(weathercode)
        
        return jsonify({
            "sehir": sehir,
            "ulke": ulke,
            "sicaklik": round(sicaklik),
            "durum": durum,
            "ikon": ikon,
            "weathercode": weathercode
        })
    except Exception as e:
        return jsonify({"hata": str(e)}), 500

# WEB SİTESİNDEN ŞEHRİ KAYDETMEK İÇİN ROTAMIZ
@app.route("/api/kaydet", methods=["POST"])
def konumu_kaydet():
    req = request.get_json(silent=True) or {}
    ulke = req.get("ulke")
    sehir = req.get("sehir")

    if ulke in DunyaVeritabani and sehir in DunyaVeritabani[ulke]:
        aktif_konum["ulke"] = ulke
        aktif_konum["sehir"] = sehir
        return jsonify({"durum": "basarili", "ulke": ulke, "sehir": sehir})
    
    return jsonify({"durum": "hata", "mesaj": "Gecersiz konum"}), 400

# LILYGO KARTININ DÜZENLİ SORGULAYACAĞI JSON UÇ NOKTASI
@app.route("/api/cihaz-hava")
def cihaz_hava():
    ulke = aktif_konum["ulke"]
    sehir = aktif_konum["sehir"]
    lat = DunyaVeritabani[ulke][sehir]["lat"]
    lon = DunyaVeritabani[ulke][sehir]["lon"]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data.get("current", {})
        temp = round(current.get("temperature_2m", 0))
        code = current.get("weathercode", 0)
        durum, _ = hava_durumu_acikla(code)

        # ASCII uyumlu temiz Türkçe karakter dönüşümü (ESP32 TFT ekranda bozulmasın diye)
        temiz_sehir = sehir.replace("ı", "i").replace("İ", "I").replace("ş", "s").replace("Ş", "S").replace("ğ", "g").replace("Ğ", "G").replace("ü", "u").replace("Ü", "U").replace("ö", "o").replace("Ö", "O").replace("ç", "c").replace("Ç", "C")
        temiz_ulke = ulke.replace("ü", "u").replace("Ü", "U")

        return jsonify({
            "sehir": temiz_sehir,
            "ulke": temiz_ulke,
            "sicaklik": temp,
            "durum": durum,
            "code": code
        })
    except Exception as e:
        return jsonify({"hata": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)