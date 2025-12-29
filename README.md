# 🤖 Discord Bot & Web Dashboard PRO

> **Advanced Programming Dersi Dönem Projesi**
>
> Bu proje, modern asenkron programlama teknikleri kullanılarak geliştirilmiş, çok sunuculu (multi-server) destekli ve web paneli olan kapsamlı bir Discord botudur.

## 🚀 Teknoloji Yığını (Tech Stack)

Proje, endüstri standardı teknolojilerle ve **%100 Asenkron** mimariyle geliştirilmiştir.

### Backend & Bot
*   **Python 3.10+**: Ana geliştirme dili.
*   **Quart Framework**: Web dashboard için Flask'ın **Asenkron (Async)** versiyonu kullanıldı. Bu sayede bot Discord'daki mesajları yanıtlarken site donmaz. (High Concurrency).
*   **Discord.py (2.0+)**: Discord API ile iletişim için modern kütüphane.
*   **AsyncIO**: Eşzamanlı (concurrent) işlem yönetimi için.

### Veritabanı
*   **SQLite3**: Veri saklama.
*   **aiosqlite**: Veritabanı sorgularının botu kilitlememesi (non-blocking) için kullanılan asenkron sürücü.

### Frontend (Dashboard)
*   **HTML5 & CSS3**: Modern, responsive tasarım.
*   **Glassmorphism UI**: Premium hissiyatlı, bulanık arka planlı (backdrop-filter) modern arayüz tasarımı.
*   **Jinja2**: HTML şablon motoru (Template Engine).

---

## 🔥 Özellikler

### 1. Web Yönetim Paneli (Dashboard)
*   Discord ile Giriş (**OAuth2**)
*   Sunucuya özel ayarlar (Prefix, Log Kanalı vb.)
*   Canlı Liderlik Tabloları (XP, Mesaj, Ses)
*   **Glassmorphism** tasarım dili.

### 2. Gelişmiş Ekonomi (Global)
*   `!buy_coin`, `!sell_coin`: Dinamik borsa sistemi.
*   `!daily`: Günlük ödül sistemi.
*   `!steal`: Riskli soygun mekaniği.
*   `!market`: Rozet ve eşya satın alma.

### 3. Seviye (Level) & İstatistik
*   Her mesaj ve sesli sohbet XP kazandırır.
*   Gelişmiş Profil Kartı (`!profile`).
*   Haftalık ve Genel Sıralamalar (`!stat`, `!top_voice`).

### 4. Eğlence & Sosyal
*   Evlilik Sistemi (`!marry`, `!divorce`).
*   Rep Puanı (`!rep`).
*   Kelime Oyunu, Düello, Yazı Tura.

---

## 🛠️ Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Ortam Değişkenleri (.env)
Proje kök dizinine `.env` dosyası oluşturun:
```env
TOKEN=DISCORD_BOT_TOKEN
OWNER_ID=SIZIN_ID
CLIENT_SECRET=OAUTH2_SECRET
CLIENT_ID=BOT_ID
REDIRECT_URI=http://localhost:5000/callback
SECRET_KEY=rastgele_guvenlik_anahtari
```

### 3. Başlatma
```bash
python main.py
```
*Bu komut hem Botu hem de Web Sitesini tek bir "Event Loop" içinde asenkron olarak başlatır.*

---

## 📂 Proje Yapısı

```
discord-bot/
├── main.py              # Entry Point (Bot + Web Server entegrasyonu)
├── database.py          # Asenkron Veritabanı Katmanı (DAL)
├── cogs/                # Modüler Bot Parçaları
│   ├── ekonomi.py       # Ekonomi Komutları
│   ├── oyun.py          # Oyun Mekanikleri
│   ├── sosyal.py        # Sosyal Etkileşimler
│   ├── stats.py         # İstatistik & Level
│   └── yonetim.py       # Moderasyon
├── dashboard/           # Web Uygulaması (Quart)
│   ├── app.py           # Web Server Logic
│   ├── templates/       # HTML Dosyaları
│   └── static/          # CSS & Assets
└── requirements.txt     # Bağımlılıklar
```

---
## 🧪 Geliştirme ve Test Araçları (Dev Tools)

Proje, geliştirme sürecini hızlandırmak için özel araçlar içerir:

*   **Mock Dashboard Server (`preview.py`)**: Discord API'ye ihtiyaç duymadan arayüzü test etmek için sahte veri (mock data) ile çalışan özel sunucu.
*   **Otomatik Testler (`run_tests.py`)**: Tüm komutların çalıştığını doğrulayan kapsamlı simülasyon testleri.
*   **Mega Simulation**: `tests/test_final_full_system.py` dosyası ile 50+ komutu saniyeler içinde simüle edip raporlar.

---

**Geliştiriciler:** Elif, Nisa, Şeyma
**Lisans:** MIT