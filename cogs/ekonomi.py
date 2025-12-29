import config
import discord
from discord.ext import commands
import asyncio
import random
import time



class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #ekonomi    
    @commands.command()
    async def borsa(self, ctx):
        guild_id, user_id = ctx.guild.id, ctx.author.id
        
        #botcoin fiyatını cekiyoruz
        price = await self.bot.db.get_botcoin()
        user_data = await self.bot.db.get_user_data(guild_id, user_id)
        
        user_xp = user_data['xp']
        user_bc = user_data['botcoin']

        embed = discord.Embed(title="📈 BotCoin Borsası", color=config.COLORS.get('Gold', discord.Color.gold()))
        embed.add_field(name="BotCoin Fiyatı", value=f"**{price} XP**")
        embed.add_field(name="Cüzdanınız", value=f"💰 {user_xp} XP\n{config.EMOJIS.get('coin', '🪙')} {user_bc} BC")
        await ctx.send(embed=embed)

    @commands.command(aliases=["coinal"])
    async def buy_coin(self, ctx, n: int):
        if n <= 0: return await ctx.send("Geçersiz miktar.")
        
        guild_id, user_id = ctx.guild.id, ctx.author.id
        
        #botcoin fiyatını cekiyoruz yine
        price = await self.bot.db.get_botcoin()
        cost = price * n
        
        user_data = await self.bot.db.get_user_data(guild_id, user_id)
        
        if user_data['xp'] < cost: 
            return await ctx.send(f"{config.EMOJIS.get('error', '❌')} Yetersiz XP. {cost} XP lazım.")
        
        await self.bot.db.add_xp(guild_id, user_id, -cost) #xp düstü
        await self.bot.db.add_coin(guild_id, user_id, n) #coin alındı
        
        await ctx.send(f"{config.EMOJIS.get('success', '✅')} **{n} BotCoin** alındı. {cost} XP ödendi.")

    @commands.command(aliases=["coinsat"])
    async def sell_coin(self, ctx, n: int):
        if n <= 0: return await ctx.send("Geçersiz miktar.")
        
        guild_id, user_id = ctx.guild.id, ctx.author.id
        
        price = await self.bot.db.get_botcoin()
        earned = price * n
        
        user_data = await self.bot.db.get_user_data(guild_id, user_id)
        
        if user_data['botcoin'] < n: 
            return await ctx.send(f"{config.EMOJIS.get('error', '❌')} Yetersiz Botcoin.")
        
        await self.bot.db.add_coin(guild_id, user_id, -n) # coin düştük
        await self.bot.db.add_xp(guild_id, user_id, earned) # xp ekledik
        
        await ctx.send(f"{config.EMOJIS.get('success', '✅')} **{n} BotCoin** sattın. {earned} XP kazandın.")

    #daily icin fonksiyon
    @commands.command(aliases=["gunluk"])
    async def claim_daily(self, ctx):
        user_id=ctx.author.id  
        server_id=ctx.guild.id

        user_d=await self.bot.db.get_user_data(server_id, user_id)
        if not user_d:
            await self.bot.db.does_user_exists(server_id, user_id) #ne uzun koymusuz bunu ya neyse degistiremem simd
            last=0
        else:
            last=user_d['last_daily'] or 0


        bekleme=24*60*60 #hesaplamaya üsendim kb ayrıca bekleme suresi ingilizcesii hatılamıyrm

        now=int(time.time())
        if now - last < bekleme:
            left = bekleme - (now - last)
            hour = int(left / 3600)
            minute = int((left % 3600) / 60)
            second = int(left % 60)

            left_t=""
            if hour > 0:
                left_t = f"**{hour} saat**"
                if minute > 0:
                    left_t += f" ve **{minute} dakika**"
            elif minute > 0:
                left_t = f"**{minute} dakika**"
            else:
                left_t = f"**{second} saniye**"
            

            embed = discord.Embed(title=f"{config.EMOJIS['Error']} Bekle!", color=config.COLORS['Error'])
            embed.description = f"Günlük ödülünü zaten aldın.\nTekrar alabilmek için **{left_t}** beklemelisin."
            await ctx.send(embed=embed)
            return
        daily_coin=config.DAILY_COIN_REWARD

        daily_xp =config.DAILY_XP_REWARD
        await self.bot.db.claim_daily(server_id, user_id, daily_coin)

        await self.bot.db.add_xp(server_id, user_id, daily_xp)

        embed= discord.Embed(title=f"{config.EMOJIS['success']} Günlük Ödül ALındı!", color=config.COLORS['Success'])
        embed.description=f"Günlük ödülünü aldın!"

        embed.add_field(name="Kazandıkların", value=f"{daily_coin} {config.EMOJIS['coin']} ve {daily_xp} XP")
        #buralara emoji eklenebilir süs amacıyloa ben usendim

        await ctx.send(embed=embed)

    #steal icin fonksiyon
    @commands.command(aliases=["soygun"])
    @commands.cooldown(1, 60, commands.BucketType.user) #1dk
    async def steal(self, ctx):
        guild_id, user_id = ctx.guild.id, ctx.author.id
        
        #önce parayı alıyoruz
        user_data = await self.bot.db.get_user_data(guild_id, user_id)
        current_xp = user_data['xp'] if user_data else 0

        #eğer parası yoksa soygun yapamasın
        if current_xp <= 0:
            await ctx.send(f"{config.EMOJIS['error']} Kaybedecek hiçbir şeyin yokken soygun yapamazsın! Git biraz XP kazan.")
            return

        luck = random.randint(1, 100)
        
        #sansı düsürüyorum cünkü neden olmasın
        if luck <= 10: 
            win_amount = random.randint(200, 600)
            await self.bot.db.add_xp(guild_id, user_id, win_amount)
            
            embed = discord.Embed(title="💰 VURGUN!", description=f"Harika iş çıkardın!\n**+{win_amount} XP** kazandın.", color=config.COLORS.get('Success', discord.Color.green()))
            embed.set_image(url="https://media.tenor.com/images/0e30f323232433765700d367e19c5622/tenor.gif")
            
        
        elif luck <= 50: 
            lost_amount = random.randint(100, 300)
            
            #eksiye düşmemesi için kontrol
            if current_xp < lost_amount:
                lost_amount = current_xp 

            await self.bot.db.add_xp(guild_id, user_id, -lost_amount)
            
            embed = discord.Embed(title="🚔 YAKALANDIN!", description=f"Polisler seni enseledi!\n**-{lost_amount} XP** kaybettin.", color=config.COLORS.get('Error', discord.Color.red()))
            embed.set_image(url="https://media.tenor.com/images/2b7c76d9556035c2e66227b267950223/tenor.gif")
            
        #kaçma ihtimali
        else: 
            embed = discord.Embed(title="🏃‍♂️ KAÇTIN!", description="Polis sirenlerini duyunca boş elle kaçtın.\n**Ne kazandın ne kaybettin.**", color=discord.Color.orange())
            
        await ctx.send(embed=embed)

    #cooldown için 
    @steal.error
    async def steal_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"{config.EMOJIS.get('error', '⏳')} soygun için **{int(error.retry_after)} saniye** daha beklemen lazım.")

    @commands.command()
    async def market(self, ctx):
        #market değişitirldi ve geliştirldi rol eklenebilir
        
        embed = discord.Embed(
            title="🛒 MARKET",
            description=f"XP harcayarak aşağıdaki ürünleri satın alabilirsin.\nSatın almak için: `{ctx.prefix}satinal <numara>`",
            color=config.COLORS.get('Success', discord.Color.green())
        )
        
        #ürünleri otomatik listelemek için
        for id, item in config.SHOP_ITEMS.items():
            role = ctx.guild.get_role(item['role_id'])
            role_name = role.name if role else "Rol Bulunamadı (Admin'e bildir)"
            
            embed.add_field(
                name=f"#{id} - {item['name']} ({item['price']} XP)",
                value=f"📜 {item['desc']}\n🎁 Ödül: **@{role_name}**",
                inline=False
            )
            
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3081/3081559.png") #market ikonu
        embed.set_footer(text=f"Mevcut XP'ni görmek için {ctx.prefix}profil yazabilirsin.")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=["satınal"])
    async def buy(self, ctx, item_id: int):
        #marketten ürün satın alma için
        
        #ürün var mı
        item = config.SHOP_ITEMS.get(item_id)
        if not item:
            await ctx.send(f"{config.EMOJIS.get('error', '❌')} Böyle bir ürün numarası yok! Lütfen marketi kontrol et.")
            return

        guild_id, user_id = ctx.guild.id, ctx.author.id
        
        #bakiyeyi çekiyoruz db ten 
        user_data = await self.bot.db.get_user_data(guild_id, user_id)
        
        if not user_data:
            await ctx.send("Kayıt bulunamadı, lütfen önce bir mesaj yaz.")
            return

        current_xp = user_data['xp']
        cost = item['price']

        #xp kontrolü
        if current_xp < cost:
            await ctx.send(f"{config.EMOJIS.get('error', '❌')} Yetersiz bakiye! Bu ürünü almak için **{cost - current_xp} XP** daha kazanmalısın.")
            return

        #rol kontrolü
        role = ctx.guild.get_role(item['role_id'])
        if not role:
            await ctx.send("⚠️ Bu ürünün rolü sunucuda bulunamadı. Lütfen yetkililere bildir.")
            return
        
        if role in ctx.author.roles:
            await ctx.send(f"⚠️ **{item['name']}** ürününe (rolüne) zaten sahipsin!")
            return

        #satın alma
        try:
           
            await self.bot.db.add_xp(guild_id, user_id, -cost)
            
            
            await ctx.author.add_roles(role)
            
            embed = discord.Embed(
                title="🛍️ SATIN ALMA BAŞARILI!",
                description=f"Tebrikler! **{cost} XP** karşılığında **{item['name']}** satın aldın.\nRolün hesabına tanımlandı: {role.mention}",
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ Botun bu rolü vermeye yetkisi yok! Lütfen botun rolünü satın alınacak rolün üzerine taşıyın.")
        except Exception as e:
            await ctx.send(f"Bir hata oluştu: {e}")
async def setup(bot):
    await bot.add_cog(Economy(bot))
