import os
from dotenv import load_dotenv
import discord

#env dosyasını yüklüyoruz
load_dotenv()


#tokeni vs env den alıytoruz
TOKEN = os.getenv("TOKEN") 
OWNER_ID = int(os.getenv("OWNER_ID") or 0)
DB_FILE = "database.db"


DEFAULT_PREFIX = "!" 

# web dashboard ayarlari
SECRET_KEY = os.getenv("SECRET_KEY", "gizli_anahtar_varsayilan")
CLIENT_ID = os.getenv("CLIENT_ID", "1442209715827245169")
CLIENT_SECRET = os.getenv("CLIENT_SECRET") 
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")
PORT = int(os.getenv("PORT", 5000))
DEV_MODE = True 

# cogs listesi
EXTENSIONS = [
    "cogs.stats",
    "cogs.oyun",
    "cogs.yonetim",
    "cogs.ekonomi",
    "cogs.sosyal",
    "cogs.yardim"
]

#savitler

# oyun xp ayarlari
XP_PER_MESSAGE_MIN = 2
XP_PER_MESSAGE_MAX = 5
DAILY_COIN_REWARD = 10
DAILY_XP_REWARD = 30

EMOJIS = {
    "levelup": "⬆️",
    "coin": "🪙",
    "message": "💬",
    "voice": "🎤",
    "error": "❌",
    "success": "✅",
    "info": "ℹ️"
}

COLORS = {
    "Kırmızı": discord.Color.red(), "Turuncu": discord.Color.orange(), "Sarı": discord.Color.gold(),
    "Yeşil": discord.Color.green(), "Mavi": discord.Color.blue(), "Mor": discord.Color.purple(),
    "Siyah": 0x010101, "Beyaz": 0xFFFFFF, "Gold": 0xF1C40F, "Error": 0xE74C3C, "Success": 0x2ECC71,
    "info": 0x3498DB
}

SHOP_ITEMS = {
        1: {"name": "Zengin Rozeti", "price": 1000, "role_id": 123456789012345678, "desc": "Hava atmak için birebir!"},
        2: {"name": "VIP Üye", "price": 5000, "role_id": 987654321098765432, "desc": "Özel kanallara erişim sağlar."},
        3: {"name": "Bot Destekçisi", "price": 10000, "role_id": 112233445566778899, "desc": "Sunucuya katkı sağlayanlara özel."}
    }

BURCLAR = {
    "♈": "Koç", "♉": "Boğa", "♊": "İkizler", "♋": "Yengeç",
    "♌": "Aslan", "♍": "Başak", "♎": "Terazi", "♏": "Akrep",
    "♐": "Yay", "♑": "Oğlak", "♒": "Kova", "♓": "Balık"
}

RENKLER = {
    "🔴": "Kırmızı", "🟠": "Turuncu", "🟡": "Sarı", "🟢": "Yeşil",
    "🔵": "Mavi", "🟣": "Mor", "⚫": "Siyah", "⚪": "Beyaz"
}

OYUNLAR = {
    "🎮": "LoL", "🔫": "Valorant", "⚽": "FIFA", "⛏️": "Minecraft",
    "💣": "CS2", "🏎️": "GTA V", "🕸️": "Among Us", "🚀": "Rocket League"
}

KELIMELER = [
    "elma", "armut", "bilgisayar", "discord", "yazilim", "telefon", "kalem", 
    "kitap", "televizyon", "araba", "okul", "bot", "sunucu", "market", 
    "kripto", "borsa", "klavye", "mouse", "kulaklik", "helikopter", "galaksi",
    "makarna", "kebap", "lahmacun", "pide", "doner", "ayran", "cay", "kahve"
]

TRIVIA_SORULARI = {
    "Türkiye'nin başkenti neresidir?": "ankara",
    "Su kaç derecede kaynar?": "100",
    "İstanbul'un plaka kodu kaçtır?": "34",
    "Fatih Sultan Mehmet İstanbul'u kaç yılında fethetti?": "1453",
    "En hızlı koşan kara hayvanı hangisidir?": "çita",
    "Mustafa Kemal Atatürk kaç yılında doğmuştur?": "1881",
    "Güneş sistemindeki en büyük gezegen hangisidir?": "jüpiter",
    "Hangi elementin sembolü O harfidir?": "oksijen"
}

FAL_SOZLERI = [
    "Üç vakte kadar eline toplu bir para geçecek, ama hemen yeme!",
    "Seni çekemeyen bir yılan var, isminde 'A' harfi geçiyor, dikkat et.",
    "Yakında büyük bir aşk görünüyor, ama eski sevgilin arıza çıkarabilir.",
    "Kariyerinde yükseliş var, patronun sana göz kırpacak (zam anlamında).",
    "Bu aralar şansın çok açık, hemen bir piyango bileti al.",
    "Dikkat et, yakın bir arkadaşın arkandan iş çeviriyor olabilir.",
    "Yolun var, uzun bir yola çıkacaksın ve orada hayatın değişecek.",
    "Bugün mavi giyen birinden güzel bir haber alacaksın."
]

ASK_DURUMLARI = [
    {"limit": 20, "renk": 0x000000, "gif": "https://media.tenor.com/images/d05a6e64160572760a394b7a67e97390/tenor.gif", "yorum": "🤮 **Midem bulandı!** Bu ne uyumsuzluk? Kaç kurtar kendini!"},
    {"limit": 40, "renk": 0xFF0000, "gif": "https://media.tenor.com/images/8a9e27796392bb832b26a8336d4b7f2d/tenor.gif", "yorum": "💔 **Yol yakınken dön.** Sizden cacık olmaz."},
    {"limit": 60, "renk": 0xFFA500, "gif": "https://media.tenor.com/images/6466f27df282eb4b760c7372390409e2/tenor.gif", "yorum": "😐 **Eh işte...** İte kaka gideri var ama çok zorlamayın."},
    {"limit": 85, "renk": 0xFFFF00, "gif": "https://media.tenor.com/images/1c0297360b3823942b5c9cf972b75738/tenor.gif", "yorum": "😏 **Fena değil!** Arada kıvılcımlar çakıyor."},
    {"limit": 101, "renk": 0xFF00FF, "gif": "https://media.tenor.com/images/4596a520e9496cc7a3379863d9a26108/tenor.gif", "yorum": "💍 **RUH EŞİ ALARMI!** Hemen nikah masasına! Şahidin benim."}
]