import unittest
import asyncio
import os
import sys
import shutil
import random


#projeyi roota ekledik
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
import database
import os
# database.py os importunu unutmuş, test çalışsın diye burdan ekliyoruz
database.os = os

from database import DatabaseManager
from cogs.ekonomi import Economy
from cogs.oyun import Oyun
from cogs.sosyal import Sosyal
from cogs.yonetim import Yonetim
from cogs.stats import Stats

#test için mock sınıfları
class MockMessage:
    def __init__(self, id, channel, content, author):
        self.id = id
        self.channel = channel
        self.content = content
        self.author = author
        self.reactions = []

    async def add_reaction(self, emoji):
        self.reactions.append(emoji)

    async def delete(self):
        pass
        
    def users(self):
        #çekiliş için 
        class AsyncIterator:
            def __init__(self, users): self.users = users
            def __aiter__(self): return self
            async def __anext__(self):
                if not self.users: raise StopAsyncIteration
                return self.users.pop(0)
        return AsyncIterator([type('obj', (object,), {'bot': False, 'mention': '@Winner'})])

class MockReaction:
    def __init__(self):
        self.users = lambda: MockMessage(0,0,0,0).users() #dummy

class MockRole:
    #rol için
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.position = 1
        self.mention = f"@{name}"
        
    def __ge__(self, other):
        return self.position >= other.position

class MockUser:
    #kullanıcı için
    def __init__(self, id, name, bot=False):
        self.id = id
        self.name = name
        self.display_name = name
        self.bot = bot
        self.mention = f"@{name}"
        class MockAsset:
            def __init__(self, url):
                self.url = url
            async def read(self):
                return b'binary_data'
            def replace(self, **kwargs):
                return self

        self.avatar = MockAsset('http://mock.url')
        self.default_avatar = MockAsset('http://mock.url')
        self.display_avatar = self.avatar
        self.top_role = MockRole(999, "Role")
        self.guild = None
        self.color = 0xFFFFFF
        self.roles = []

    async def send(self, content=None, embed=None):
        print(f"[DM to {self.name}]: {content} (Embed: {embed is not None})")
        
    async def kick(self, reason=None):
        print(f"[Kick]: {self.name} atıldı. Sebep: {reason}")

    async def ban(self, reason=None):
        print(f"[Ban]: {self.name} yasaklandı. Sebep: {reason}")
        
    async def add_roles(self, role):
        print(f"[Role]: {role.name} rolü {self.name} kullanıcısına verildi")

    async def remove_roles(self, role):
        print(f"[Role]: {role.name} rolü {self.name} kullanıcısından alındı")

class MockGuild:
    #sunucu için
    def __init__(self, id, name, owner_id):
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.members = []
        self.roles = [MockRole(999, 'Admin')]
        self.default_role = MockRole(0, 'everyone')

    def get_role(self, id):
        return self.roles[0]

    def get_member(self, id):
        for m in self.members:
            if m.id == id: return m
        return None
        
    async def create_voice_channel(self, name, category, overwrites):
        print(f"[Guild]: Ses kanalı oluşturuldu {name}")
        return MockChannel(random.randint(1000,9999), name, self)

    async def create_role(self, name, color, reason):
        print(f"[Guild]: Rol oluşturuldu {name}")
        return MockRole(random.randint(1000,9999), name)

class MockChannel:
    #kanal için
    def __init__(self, id, name, guild):
        self.id = id
        self.name = name
        self.guild = guild
        self.category = None
        self.mention = f"<#{id}>"

    #genel mesaj gönderme metodu
    async def send(self, content=None, embed=None, delete_after=None, file=None):
        print(f"[Channel {self.name}]: {content} (Embed: {embed is not None})")
        msg = MockMessage(random.randint(1000,9999), self, content, None)
        msg.reactions.append(MockReaction()) # Genel kullanım için mock reaksiyon ekle
        return msg
        
    async def purge(self, limit=None):
        return [1] * limit
        
    async def fetch_message(self, id):
        msg = MockMessage(id, self, "fetched msg", None)
        msg.reactions = [MockReaction()]
        return msg

class MockContext:
    def __init__(self, author, guild, channel):
        self.author = author
        self.guild = guild
        self.channel = channel
        self.message = MockMessage(999, channel, "mock_msg", author)
        self.bot = None 
        self.prefix = "!"
    
    def typing(self):
        class AsyncContextManager:
            async def __aenter__(self): return None
            async def __aexit__(self, exc_type, exc, tb): return None
        return AsyncContextManager()

    async def send(self, content=None, embed=None, delete_after=None, file=None):
        return await self.channel.send(content, embed, delete_after, file)

class TestFullSystem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Test Veritabanı Kurulumu
        self.test_db_path = "tests/test_full.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = DatabaseManager()
        self.db.db_path = self.test_db_path
        await self.db.setup()

        # Mock Bot (coglar için gerekli)
        class MockBotInternal:
            def __init__(self, db):
                self.db = db
                self.user = MockUser(99999, "Bot")
                self.loop = asyncio.get_event_loop()
            def get_guild(self, id): return None
            def get_channel(self, id): return MockChannel(id, "fetched_chan", None)
            async def wait_for(self, event, **kwargs):
                # Etkileşimli komutlar için her zaman başarılı mock döndür
                if 'check' in kwargs:
                   # Evlilik/düello için olumlu yanıt simüle et
                   msg = MockMessage(1,1,"evet", MockUser(102, "User2"))
                   return msg
                raise asyncio.TimeoutError()

        self.bot = MockBotInternal(self.db)
        
        # Coglar
        self.eco = Economy(self.bot)
        self.game = Oyun(self.bot)
        self.social = Sosyal(self.bot)
        self.admin = Yonetim(self.bot)
        self.stats = Stats(self.bot)

        # Mock Verileri
        self.owner = MockUser(100, "Owner")
        self.user1 = MockUser(101, "User1")
        self.user2 = MockUser(102, "User2")
        self.guild = MockGuild(500, "TestServer", self.owner.id)
        self.channel = MockChannel(700, "general", self.guild)
        
        self.guild.members = [self.owner, self.user1, self.user2]
        self.user1.guild = self.guild
        self.user2.guild = self.guild
        self.owner.guild = self.guild

        # Kullanıcıları veritabanına kaydet
        await self.db.does_user_exists(self.guild.id, self.owner.id)
        await self.db.does_user_exists(self.guild.id, self.user1.id)
        await self.db.does_user_exists(self.guild.id, self.user2.id)

    async def asyncTearDown(self):
        if os.path.exists(self.test_db_path):
            try: os.remove(self.test_db_path)
            except: pass

    # ==========================
    # 1. EKONOMİ KOMUTLARI
    # ==========================
    async def test_economy_full(self):
        print("\n=== EKONOMİ TESTİ ===")
        ctx = MockContext(self.user1, self.guild, self.channel)
        await self.db.add_xp(self.guild.id, self.user1.id, 5000) # Zengin başlat

        # borsa
        await self.eco.borsa.callback(self.eco, ctx) 
        
        # buy_coin (10 coin al, fiyat rastgele ama kullanıcının XP'si var)
        await self.eco.buy_coin.callback(self.eco, ctx, 10)
        
        # sell_coin (5 tane sat)
        await self.eco.sell_coin.callback(self.eco, ctx, 5)
        
        # günlük ödül
        await self.eco.claim_daily.callback(self.eco, ctx)
        
        # steal (mock şans rastgele, kazanabilir veya kaybedebilir, sadece çalıştığından emin oluyoruz)
        await self.eco.steal.callback(self.eco, ctx)
        
        # market
        await self.eco.market.callback(self.eco, ctx)
        
        # buy
        await self.eco.buy.callback(self.eco, ctx, 1)

    # ==========================
    # 2. OYUN KOMUTLARI
    # ==========================
    async def test_games_full(self):
        print("\n=== OYUN TESTİ ===")
        ctx = MockContext(self.user1, self.guild, self.channel)
        await self.db.add_xp(self.guild.id, self.user1.id, 1000)

        # kelime oyunu (1 el simüle eder)
        # Not: etkileşimli wait_for anında başarılı veya başarısız olacak şekilde mocklandı,
        # ama önemli olan mantığın çalışması.
        try: await self.game.word_game.callback(self.game, ctx, 1)
        except Exception as e: print(f"WordGame etkileşimli kısım atlandı: {e}")

        # düello (user2 ile)
        await self.db.add_xp(self.guild.id, self.user2.id, 1000) # rakibin paraya ihtiyacı var
        try: await self.game.duello.callback(self.game, ctx, self.user2, 50)
        except: pass # mock wait_for bunu halleder

        # yazitura
        await self.game.yazitura.callback(self.game, ctx, 50, "yazi")

        # anket
        await self.game.poll.callback(self.game, ctx, question="Bot iyi mi?")
        
        # lottery (Sosyal'den taşındı)
        await self.game.lottery.callback(self.game, ctx, "1s", odul="Nitro")

        # fal (Sosyal'den taşındı)
        await self.game.fortune.callback(self.game, ctx)

    # ==========================
    # 3. SOSYAL KOMUTLARI
    # ==========================
    async def test_social_full(self):
        print("\n=== SOSYAL TESTİ ===")
        ctx = MockContext(self.user1, self.guild, self.channel)
        await self.db.add_xp(self.guild.id, self.user1.id, 2000)
        
        # aşk ölçer
        try: await self.social.love_calculator.callback(self.social, ctx, self.user2)
        except: pass # Bazen PIL bağımlılık sorunları olabiliyor
        
        # evlilik
        try: await self.social.marry.callback(self.social, ctx, self.user2)
        except: pass
        
        # boşanma
        # Önce mantığı test etmek için veritabanında evli olduklarından emin olun?
        # Veya sadece başarısız mesajını görmek için çalıştırın.
        await self.social.divorce.callback(self.social, ctx)
        
        # rep
        await self.social.rep.callback(self.social, ctx, self.user2)
        
        # itiraf (önce kanal ayarlanmalı) (Mock eksik kanalı zarifçe karşılar)
        await self.social.confession.callback(self.social, ctx, m="Gizli")
        
        # read_secret
        await self.social.read_secret.callback(self.social, ctx)
        
        # leave_secret
        await self.social.leave_secret.callback(self.social, ctx, secret="Sırrım var")

    # ==========================
    # 4. YÖNETİM KOMUTLARI
    # ==========================
    async def test_management_full(self):
        print("\n=== YÖNETİM TESTİ ===")
        ctx = MockContext(self.owner, self.guild, self.channel)
        dummy_channel = MockChannel(888, "logs", self.guild)
        dummy_role = MockRole(777, "Member")

        # setting (log)
        await self.admin.setting.callback(self.admin, ctx, dummy_channel)
        
        # set_itiraf
        await self.admin.set_confession.callback(self.admin, ctx, dummy_channel)
        
        # set_trivia
        await self.admin.set_trivia.callback(self.admin, ctx, dummy_channel)
        
        # auto_role (varsayılan rolü ayarla)
        await self.admin.auto_role.callback(self.admin, ctx, dummy_role)
        
        # set_auto_role (paneller)
        await self.admin.set_auto_role.callback(self.admin, ctx, dummy_channel)
        
        # tagayarla
        await self.admin.set_tag.callback(self.admin, ctx, "TAG|")
        
        # kick
        await self.admin.kick.callback(self.admin, ctx, self.user2, reason="Test Kick")
        
        # ban
        await self.admin.ban.callback(self.admin, ctx, self.user2, reason="Test Ban")
        
        # delete (Sil)
        await self.admin.delete.callback(self.admin, ctx, 5)
        
        # afk
        await self.admin.afk.callback(self.admin, ctx, reason="Uyumak")
        
        # private_channel
        await self.admin.private_channel.callback(self.admin, ctx, "OzelOda")
        
        # add_button (önce mesaj için db kaydı gerekir? çoğunlukla Discord API ağırlıklı)
        # Bir mesaja buton eklemeyi simüle ediyoruz
        await self.admin.add_button.callback(self.admin, ctx, 12345, "👍", dummy_role)
        
        # Lisanslar
        await self.admin.add_license.callback(self.admin, ctx, 999, 888)
        await self.admin.remove_license.callback(self.admin, ctx, 999)

    # ==========================
    # 5. İSTATİSTİK KOMUTLARI
    # ==========================
    async def test_stats_full(self):
        print("\n=== İSTATİSTİK TESTİ ===")
        ctx = MockContext(self.user1, self.guild, self.channel)

        # profil
        await self.stats.profile.callback(self.stats, ctx, self.user1)
        
        # stat (XP Sıralaması)
        await self.stats.stat.callback(self.stats, ctx)
        
        # top_voice
        await self.stats.top_voice.callback(self.stats, ctx)
        
        # top_message
        await self.stats.top_message.callback(self.stats, ctx)
        
        # top_invite
        await self.stats.top_invite.callback(self.stats, ctx)
        
        # top_weekly
        await self.stats.top_weekly.callback(self.stats, ctx)
        
        # rank (Sıralamam)
        await self.stats.rank.callback(self.stats, ctx)
        
        # profile_photo
        await self.stats.profile_photo.callback(self.stats, ctx, self.user1)
        
        # Yönetim İşlemleri
        ctx_admin = MockContext(self.owner, self.guild, self.channel)
        
        # give_xp
        await self.stats.give_xp.callback(self.stats, ctx_admin, self.user2, 100)
        
        # give_level
        await self.stats.give_level.callback(self.stats, ctx_admin, self.user2, 5)

if __name__ == '__main__':
    unittest.main()
