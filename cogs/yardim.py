import discord
from discord.ext import commands
import config

class HelpPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=["yardim", "help", "komutlar"])
    async def helppanel(self, ctx):
        #burası düzenlenccek prefix kımsı

        p = config.DEFAULT_PREFIX
        
        embed = discord.Embed(
            title="📚 Yardım Menüsü",
            description=f"Botun tüm özellikleri aşağıdadır. Komutları kullanırken başına `{p}` koymayı unutma!",
            color=discord.Color.from_rgb(88, 101, 242) #açıklama
        )
        
        #bot avatarı eklenebilir
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        #sosyal fonksiyonları için
        sosyal_desc = (
            f"`{p}askolcer @kisi` - Aşk uyumunuzu ölçer 💘\n"
            f"`{p}evlen @kisi` - Sevdiğin kişiyle evlenirsin 💍\n"
            f"`{p}bosan` - Eşinden boşanırsın 💔\n"
            f"`{p}rep @kisi` - Birine itibar puanı verirsin ⭐\n"
            f"`{p}sirbirak <mesaj>` - Anonim bir sır bırakırsın (Kasa) 🤫\n"
            f"`{p}siroku` - Kasadan rastgele bir sır okursun 🕵️‍♂️\n"
            f"`{p}itiraf <mesaj>` - İtiraf kanalına anonim mesaj atar"
        )
        embed.add_field(name="🎉 Sosyal & Eğlence", value=sosyal_desc, inline=False)
        
        #oyunlar için
        oyun_desc = (
            f"`{p}kelimeoyunu` - Kelime bilmece oyunu başlatır 🎮\n"
            f"`{p}duello @kisi <miktar>` - Bahsine düello atarsın ⚔️\n"
            f"`{p}yazitura <miktar> <yazi/tura>` - Yazı tura atarsın 🪙\n"
            f"`{p}fal` - Falcı bacı sana geleceği söyler 🔮\n"
            f"`{p}cekilis <süre> <ödül>` - Çekiliş başlatır"
        )
        embed.add_field(name="🎲 Oyunlar", value=oyun_desc, inline=False)
        
        #ekonomi komutları için 
        ekonomi_desc = (
            f"`{p}gunluk` - Günlük XP ve Coin ödülünü alırsın 📅\n"
            f"`{p}soygun` - Riskli soygun yaparsın (Kazan yada Kaybet) 💰\n"
            f"`{p}market` - Eşya marketini açar 🛒\n"
            f"`{p}satinal <id>` - Marketten eşya alırsın\n"
            f"`{p}borsa` - BotCoin kurunu görürsün 📈\n"
            f"`{p}coinal <miktar>` / `{p}coinsat` - Coin ticareti"
        )
        embed.add_field(name="💸 Ekonomi", value=ekonomi_desc, inline=False)
        
        #stats komutları için 
        stats_desc = (
            f"`{p}profil` - Kendi profilini ve seviyeni görürsün 👤\n"
            f"`{p}rank` - Sunucudaki XP sıranı görürsün 📊\n"
            f"`{p}stat` - Genel XP liderlik tablosu 🏆\n"
            f"`{p}topses` / `{p}topmesaj` - Ses ve mesaj sıralaması"
        )
        embed.add_field(name="📊 İstatistik", value=stats_desc, inline=False)

        #yönetim sadece yetkililerin izni var
        if ctx.author.guild_permissions.administrator:
            yonetim_desc = (
                f"`{p}kurulum #kanal` - Log kanalını ayarlar\n"
                f"`{p}otorol @rol` - Gelenlere verilecek rol\n"
                f"`{p}ban @kisi` / `{p}kick @kisi` - Yasaklama/Atma\n"
                f"`{p}sil <miktar>` - Mesaj temizler\n"
                f"`{p}otomatik_rol_kur #kanal` - Rol seçme menüsü kurar\n"
                f"`{p}kurulumitiraf #kanal` - İtiraf kanalını ayarlar\n"
                f"`{p}kurulumtrivia #kanal` - Trivia kanalını ayarlar\n"
                f"`{p}buton_ekle <msg_id> <emoji> @rol` - Mesaja rol butonu ekler"
            )
            embed.add_field(name="🛠️ Yönetim (Sadece Yetkililer)", value=yonetim_desc, inline=False)
            
        embed.set_footer(text=f"{ctx.author.name} istedi", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpPanel(bot))