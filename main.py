import discord
from discord.ext import commands, tasks
import asyncio
import os
import config
from database import DatabaseManager
from utils import log 

#intentler
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

#prefix fonksiyonu
async def get_prefix(bot, message):
    if not message.guild:
        return config.DEFAULT_PREFIX
    
    # db den sunucu ayarlarini cek
    settings = await bot.db.get_server_settings(message.guild.id)
    return settings.get("prefix", config.DEFAULT_PREFIX)

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help") 

#databasei bota ekliyoruz ki her yerden eriselim
bot.db = DatabaseManager()

@bot.event
async def on_ready():
    #bot acilinca calisir
    log.info(f"Giris yapildi: {bot.user.name}")
    log.info("------")
    
    # database kurulumu
    await bot.db.setup()
    
    #database ve lisans kontrolü
    for guild in bot.guilds:
        #dbte var mı yok mu
        await bot.db.does_server_exists(guild.id)
        
        #lisans kontrolü
        if not await bot.db.is_allowed_server(guild.id):
            log.warning(f"Lisanssiz sunucu bulundu: {guild.name} ({guild.id})")
            await guild.leave() 
        
        #uyeleri ekleme
        for member in guild.members:
            if not member.bot:
                await bot.db.does_user_exists(guild.id, member.id)

    #status ayarlama
    await bot.change_presence(activity=discord.Game(name=f"{config.DEFAULT_PREFIX}help | Version 1.0"))
    
    #looplari baslat
    if not reset_weekly_stats.is_running():
        reset_weekly_stats.start()

#cogs yukleme
async def load_extensions():
    # config.EXTENTIONS listesini kullancaz
    for ext in config.EXTENTIONS:
        try:
            await bot.load_extension(ext)
            log.info(f"Yuklendi: {ext}")
        except Exception as e:
            log.error(f"Hata olustu {ext}: {e}")

@bot.event
async def on_guild_join(guild):
    #bot bir sunucuya eklenince
    
    #lisans kontrolü
    if not await bot.db.is_allowed_server(guild.id):
        #eğer izinli listesinde yoksa
        owner = guild.owner
        if owner:
            try:
                await owner.send(f"❌ **{bot.user.name}** botunu kullanmak için lisansınız yok. Lütfen geliştirici ile iletişime geçin.")
            except:
                pass
        
        log.warning(f"Lisanssiz giris denemesi: {guild.name}")
        # await guild.leave() # burasi da demo icin kapali
        return

    await bot.db.does_server_exists(guild.id)
    log.info(f"Yeni sunucuya katildi: {guild.name}")

@bot.event
async def on_member_join(member):
    #gelenleri veritabanina kaydetme
    if not member.bot:
        await bot.db.does_user_exists(member.guild.id, member.id)
    
    #otorol varsa ver
    settings = await bot.db.get_server_settings(member.guild.id)
    autorole_id = settings['autorole']
    if autorole_id:
        role = member.guild.get_role(autorole_id)
        if role:
            await member.add_roles(role)

@bot.event
async def on_raw_reaction_add(payload):
    #reaction role ekleme
    if payload.user_id == bot.user.id: return

    rr = await bot.db.get_reaction_roles(payload.guild_id, payload.message_id, str(payload.emoji))
    if rr:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(rr)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    #reaction role silme
    rr = await bot.db.get_reaction_roles(payload.guild_id, payload.message_id, str(payload.emoji))
    if rr:
        guild = bot.get_guild(payload.guild_id)
        role = guild.get_role(rr)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)

@tasks.loop(hours=168) #1 hafta
async def reset_weekly_stats():
    #haftalik statlari sifirla
    await bot.db.reset_weekly()
    log.info("Haftalik istatistikler sifirlandi.")


#dashboard import
from dashboard.app import app, init_dashboard

async def main():
    async with bot:
        await load_extensions()
        if not config.TOKEN:
            log.critical("HATA: Token bulunamadi! .env dosyasini kontrol et.")
            return

        #dashboard baslatma (bot ile birlikte)
        init_dashboard(bot)
        
        #web sunucusunu arka planda baslat

        #app run task asenktron calısır
        bot.loop.create_task(app.run_task(port=int(config.PORT or 5000), host='0.0.0.0'))
        log.info(f"Dashboard başlatılıyor... Port: {config.PORT}")

        await bot.start(config.TOKEN)

    @bot.event
    async def on_command_error(ctx, error):
    #eğer komut bulunamazsa vs
     if isinstance(error, commands.CommandNotFound):
        return

    #hatayı chate gönder
    if isinstance(error, commands.CommandInvokeError):

        await ctx.send(f"🔥 **HATA OLUŞTU:** `{error.original}`", delete_after=20)
        print(f"KRİTİK HATA: {error.original}") #terminale de yazsın
    else:
        await ctx.send(f"⚠️ **BİLGİ:** {error}", delete_after=20)
        
if __name__ == "__main__":
    asyncio.run(main())