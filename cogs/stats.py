#buna da baslıyorum dosya sistemi düzenlenince direkt cogsun icine koyarız
import discord
import time
import random
import math
import config
import aiosqlite
from discord.ext import commands
from utils import calculate_xp_for_level

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.voice_cache={} #ram de burası sonra değiştilebilir

    @commands.Cog.listener()
    #mesaj attıkça xp artması için 
    async def on_message(self, message):
        if message.author.bot or not message.guild:


            return
        await self.bot.db.add_message(message.guild.id, message.author.id)

        xp_gain=random.randint(config.XP_PER_MESSAGE_MIN, config.XP_PER_MESSAGE_MAX)
        #configten alınır


        await self.bot.db.add_xp(message.guild.id, message.author.id, xp_gain)
        user_data=await self.bot.db.get_user_data(message.guild.id, message.author.id)

        if user_data:
            #xp artınca level atlama kontrülü
        
            current_xp =user_data['xp']
            current_level=user_data['level']

            next_level_xp=calculate_xp_for_level(current_level)
            if current_xp >= next_level_xp:
                new_level=current_level +1

                await self.bot.db.set_user_level(message.guild.id, message.author.id, new_level)

                await self.bot.db.set_user_xp(message.guild.id, message.author.id, 0)
                #reward verilebilir???
                #tabi kide cimriliktenmax 2 coin veriyorum degistilirebilir
                reward=new_level*1
                await self.bot.db.add_coin(message.guild.id, message.author.id, reward)


                #haber verme icin
                setts = await self.bot.db.get_server_settings(message.guild.id)
                channel_id=setts['level_channel_id'] or setts ['log_channel_id']
                #ya level channalına ya da logsa 
                
                if channel_id: #kanalda level atalayanlar gösterlieblir
                    channel =self.bot.get_channel(channel_id)
                    if channel:
                        embed=discord.Embed(title=f"{config.EMOJIS['levelup']} LEVEL ATLADIN!",
                        color=config.COLORS['Gold'])
                        embed.description=f"{message.author.mention}, Tebrikler! {new_level} seviyeye ulaştın"
                        embed.add_field(name="Kazandığın Coin", value=f"{reward} {config.EMOJIS['coin']}")
                        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, enter, leave): 
        #bu fonksiyon isimlerini degistemiyomusuz zor yoldan ögrenildi :(
        if member.bot:return
        user_id=member.id #degiken atadık surekli kullanıyoruz cünkü????
        server_id=member.guild.id

        #kanalagiris
        if enter.channel is None and leave.channel is not None:
            self.voice_cache[user_id]=time.time()
        #kanalcikis
        elif enter.channel is not None and leave.channel is None:
            if user_id in self.voice_cache:
                start=self.voice_cache.pop(user_id)
                end=time.time()
                amount=int(end-start)
                if amount >=60:
                    await self.bot.db.add_voice(server_id, user_id, amount)       

    @commands.command(aliases= ["profil"])
    #profil kartı oluşturmak için komut
    async def profile(self, ctx, member: discord.Member=None):
        member=member or ctx.author
        user_d= await self.bot.db.get_user_data(ctx.guild.id, member.id)
        if not user_d:
            await ctx.send("Kullanıcı yok.")
            return
        
        need_xp=calculate_xp_for_level(user_d['level'])
        #yüzde seyi hesaplama
        if need_xp == 0: need_xp = 100  
        #bölme hatasın önlemek icin
        yuzde =int((user_d['xp'] / need_xp) *10)
        if yuzde >10:
            yuzde =10
        yuzde_bar="█" * yuzde + "░" * (10 - yuzde)  

        embed = discord.Embed(title=f"👤 {member.display_name}", color=member.color)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        #imdat
        embed.add_field(name="Level", value=f"**{user_d['level']}**", inline=True)
        embed.add_field(name="XP", value=f"{user_d['xp']} / {need_xp}\n{yuzde_bar}", inline=True)
        embed.add_field(name="Bakiye", value=f"{user_d['botcoin']} {config.EMOJIS['coin']}", inline=False)
        voice_min = int(user_d['voice_sec'] / 60)
        stats_text = (
            f"📩 Mesaj: **{user_d['message']}**\n"
            f"🎙️ Ses: **{voice_min} dk**\n"
            f"🤝 Davet: **{user_d['invites']}**\n"
            f"⭐ Rep: **{user_d['rep']}**"
        )
        embed.add_field(name="İstatistikler", value=stats_text, inline=False)

        # evliyse ?????? 
        if user_d['partner_id']:
            partner_text = f"💍 <@{user_d['partner_id']}>"
        else:
            partner_text = "Bekar"
            
        embed.add_field(name="Medeni Hali", value=partner_text, inline=False)

        await ctx.send(embed=embed)



    async def create_lb(self, ctx, column, title, unit):
        #leadership tablosu oluşturmak için genel fonks
        server_id = ctx.guild.id
        limit = 10 #kaç kişi gösterilecek
        
        async with self.bot.db.get_db() as db:
            db.row_factory = aiosqlite.Row
            
            query = f"SELECT user_id, {column}, level FROM users WHERE server_id = ? AND {column} > 0 ORDER BY {column} DESC LIMIT ?"
            
            async with db.execute(query, (server_id, limit)) as cursor:
                data = await cursor.fetchall()
        
        if not data:
            await ctx.send(f"{title} için henüz veri yok.")
            return

        embed = discord.Embed(title=title, color=config.COLORS['Gold'])
        desc = ""
        
        for i, row in enumerate(data, 1):
            user_id = row['user_id']
            val = row[column]
            
            #ses icin
            if column == "voice_sec":
                val = int(val / 60)
            
            if i == 1: emoji = "🥇"
            elif i == 2: emoji = "🥈"
            elif i == 3: emoji = "🥉"
            else: emoji = f"**{i}.**"
            
            desc += f"{emoji} <@{user_id}> : **{val} {unit}**\n"
            
        embed.description = desc
        embed.set_footer(text=f"Talep eden: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    #genel xp sıralaması fonksiyonşarı
    @commands.command()
    async def stat(self, ctx):
        await self.create_lb(ctx, "xp", "🏆 Genel XP Liderlik Tablosu", "XP")

    @commands.command(aliases=["statm", "topmesaj", "gevezeler"])
    async def top_message(self, ctx):
        await self.create_lb(ctx, "message", "En Çok Mesaj Atanlar", "Mesaj")
    @commands.command(aliases=["statv", "topses", "radyocular"])
    async def top_voice(self, ctx):

        await self.create_lb(ctx, "voice_sec", "En Çok Seste Duranlar", "Dakika")

    @commands.command(aliases=["statinv", "topdavet", "davetler"])
    async def top_invite(self, ctx):

        await self.create_lb(ctx, "invites", "En Çok Davet Yapanlar", "Davet")

    @commands.command(aliases=["stath", "haftalik"])
    async def top_weekly(self, ctx):
        await self.create_lb(ctx, "weekly_message", "Bu Hafta En Aktifler", "Mesaj")

    @commands.command()
    #sıralama için kullanıcı bazlı
    async def rank(self, ctx):
        user_id = ctx.author.id
        server_id = ctx.guild.id
        
        user_d = await self.bot.db.get_user_data(server_id, user_id)
        if not user_d:
            await ctx.send("Veri yok.")
            return
            
        my_xp = user_d['xp']
        async with self.bot.db.get_db() as db:
            async with db.execute("SELECT COUNT(*) FROM users WHERE server_id = ? AND xp > ?", (server_id, my_xp)) as cursor:
                count = (await cursor.fetchone())[0]
                rank = count + 1 
                #önümüzde kac kisi var+1 cünkü kendimiz dahil                
        embed = discord.Embed(color=config.COLORS['info'])

        embed.description = f"**{ctx.author.mention}**, şu anda **{rank}.** sıradasın! ({my_xp} XP)"
        await ctx.send(embed=embed)

    #profil fotoğrafı gösterme komutu
    @commands.command(aliases=["pp", "profilfoto"])
    async def profile_photo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        embed = discord.Embed(title=f"📸 {member.display_name}", color=member.color)
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await ctx.send(embed=embed)

    #demo icin hile fonksiyonları pek kullanımyacak büyük ihtimalle ama olsun
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give_level(self, ctx, member: discord.Member, level: int):
        await self.bot.db.set_user_level(ctx.guild.id, member.id, level)
        await self.bot.db.set_user_xp(ctx.guild.id, member.id, 0)
        await ctx.send(f"{member.mention} artık **Level {level}**!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def give_xp(self, ctx, member: discord.Member, xp: int):

        await self.bot.db.add_xp(ctx.guild.id, member.id, xp)

        await ctx.send(f"{member.mention} hesabına **+{xp} XP** eklendi.")

async def setup(bot):
    await bot.add_cog(Stats(bot))