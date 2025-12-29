import aiosqlite
import os
import json
import time
from contextlib import asynccontextmanager # EKLEME YAPILDI

class DatabaseManager:
    def __init__(self):
        if not os.path.exists("data"):
            os.makedirs("data")
            print("📁 'data' klasörü oluşturuldu.")
        
        self.db_path = "data/database.db"
    
    # db baglantısı alma fonksiyonu
    #row factory vs kullanılır
    @asynccontextmanager
    async def get_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            yield db

    async def setup(self):
        async with self.get_db() as db:
            # sunucu tablosu, burda sunucu ayarları tutuluyo

            await db.execute(
            """CREATE TABLE IF NOT EXISTS server (
                server_id INTEGER PRIMARY KEY,
                prefix TEXT DEFAULT '!',
                log_channel_id INTEGER,
                itiraf_channel_id INTEGER,
                trivia_channel_id INTEGER,
                level_channel_id INTEGER,
                tag TEXT,
                autorole INTEGER
                )""")
            
            #gecici ses kanalları tablosu
            await db.execute(
            """CREATE TABLE IF NOT EXISTS temp_channels (
                channel_id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                server_id INTEGER NOT NULL,
                create_time INTEGER DEFAULT (strftime('%s', 'now'))
                )""")

            # uyeler tablosu, xp level falan burda
            await db.execute(
                """CREATE TABLE IF NOT EXISTS users (
                server_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                level INTEGER DEFAULT 1 NOT NULL, 
                xp INTEGER DEFAULT 0 NOT NULL,
                message INTEGER DEFAULT 0,
                weekly_message INTEGER DEFAULT 0,
                invites INTEGER DEFAULT 0,
                botcoin INTEGER DEFAULT 0,
                voice_sec REAL DEFAULT 0.0,
                weekly_voice REAL DEFAULT 0.0,
                rep INTEGER DEFAULT 0 NOT NULL,
                partner_id INTEGER DEFAULT NULL,
                afk_reason TEXT DEFAULT NULL,
                afk_timestamp INTEGER DEFAULT NULL,
                last_daily INTEGER DEFAULT 0,
                last_rep INTEGER DEFAULT 0,
                PRIMARY KEY (server_id, user_id)
             )""")

            # tepki rolleri tablosu
            await db.execute(
                """CREATE TABLE IF NOT EXISTS reaction_roles (
                server_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                emoji TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                PRIMARY KEY (server_id, message_id, emoji)
            )""")

            # itiraflar tablosu (gizli sırlar burda)
            await db.execute(
                """CREATE TABLE IF NOT EXISTS secrets (
                server_id INTEGER NOT NULL,
                secret_id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret TEXT NOT NULL,
                create_time INTEGER DEFAULT (strftime('%s', 'now'))
                )""")
            
            # global degiskenler (botcoin fiyati vb)
            await db.execute(
                """CREATE TABLE IF NOT EXISTS bot_globals (
                key TEXT PRIMARY KEY,
                value INTEGER
            )""")

            # eger botcoin fiyati yoksa baslangic degeri verelim
            async with db.execute("SELECT value FROM bot_globals WHERE key = 'botcoin_price'") as cursor:
                if not await cursor.fetchone():
                    await db.execute("INSERT INTO bot_globals (key, value) VALUES ('botcoin_price', '100')") # typo fix: table name was 'globals'
            
            # baska sunuculara izin verme olayi
            await db.execute(
                """CREATE TABLE IF NOT EXISTS allowed_servers (
                server_id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL
                )""")

            # hizli arama icin indexler
            await db.execute("""CREATE INDEX IF NOT EXISTS index_users_xp ON users (server_id, xp DESC)""")
            await db.execute("""CREATE INDEX IF NOT EXISTS index_users_level ON users (server_id, level DESC)""")
            await db.execute("""CREATE INDEX IF NOT EXISTS index_users_message ON users (server_id, message DESC)""")
            await db.execute("""CREATE INDEX IF NOT EXISTS index_users_voice ON users (server_id, voice_sec DESC)""")    

            await db.commit()
            print("DB setup bitti calisiyo")
        
    #sunucu ve kullanıcı kontrol fonksiyonları

    async def get_server_data(self, server_id): 
        async with self.get_db() as db: 
            async with db.execute("SELECT * FROM server WHERE server_id = ?", (server_id,)) as cursor:
                return await cursor.fetchone()
    
    async def does_server_exists(self, server_id): 
        # sunucu yoksa ekle
        async with self.get_db() as db:
            await db.execute("INSERT OR IGNORE INTO server (server_id) VALUES (?)", (server_id,))
            await db.commit()

    async def does_user_exists(self, server_id, user_id): 
        # kullanıcı yoksa ekle
        async with self.get_db() as db:
            await db.execute("INSERT OR IGNORE INTO users (server_id, user_id) VALUES (?, ?)", (server_id, user_id,))
            await db.commit()

    async def get_user_data(self, server_id, user_id):
        #user dataları alıyoruz
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            async with db.execute("SELECT * FROM users WHERE server_id=? AND user_id=?", (server_id, user_id,)) as cursor:
                return await cursor.fetchone()
                
    async def get_botcoin(self):
        async with self.get_db() as db:
            async with db.execute("SELECT value FROM bot_globals WHERE key = 'botcoin_price'") as cursor:
                row = await cursor.fetchone()
                return int(row[0]) if row else 100 

    async def set_botcoin(self, price):
        async with self.get_db() as db:
            await db.execute("UPDATE bot_globals SET value = ? WHERE key = 'botcoin_price'", (price,))
            await db.commit()
    
    async def is_allowed_server(self, server_id):
        #lisanslı sunucu mu kontrolü
        async with self.get_db() as db:
            async with db.execute("SELECT 1 FROM allowed_servers WHERE server_id = ?", (server_id,)) as cursor:
                result = await cursor.fetchone()
                return True if result else False
    #lisanslı sunucu ekleme çıkarma 
    async def add_allowed_server(self, server_id, owner_id):
        async with self.get_db() as db:
            await db.execute("INSERT OR IGNORE INTO allowed_servers(server_id, owner_id) VALUES (?, ?)", (server_id, owner_id))
            await db.commit()
    
    async def no_money_no_bot(self, server_id, owner_id):
        async with self.get_db() as db:
            await db.execute("DELETE FROM allowed_servers WHERE server_id = ? AND owner_id=?", (server_id, owner_id),)
            await db.commit()
    
    #ayarlar için 
    
    async def get_server_settings(self, server_id):
        row = await self.get_server_data(server_id)
        if row: 
            return {
                "prefix": row["prefix"],
                "log_channel_id": row["log_channel_id"],
                "itiraf_channel_id": row["itiraf_channel_id"],
                "trivia_channel_id": row["trivia_channel_id"],
                "level_channel_id": row["level_channel_id"],
                "tag": row["tag"],
                "autorole": row["autorole"]
            }
        return {'prefix': '.', 'log_channel_id': None, 'itiraf_channel_id': None, 'trivia_channel_id': None, 'level_channel_id': None, 'tag': None, 'autorole': None}

    async def set_prefix(self, server_id, new_prefix):
        await self.does_server_exists(server_id)

        async with self.get_db() as db:
            await db.execute("UPDATE server SET prefix = ? WHERE server_id = ?", (new_prefix, server_id))
            await db.commit()

    async def set_log_channel(self, server_id, channel_id):
        await self.does_server_exists(server_id)
        async with self.get_db() as db:

            await db.execute("UPDATE server SET log_channel_id = ? WHERE server_id = ?", (channel_id, server_id))
            await db.commit()

    async def set_itiraf_channel(self, server_id, channel_id):
      
        await self.does_server_exists(server_id)
        async with self.get_db() as db:
            await db.execute("UPDATE server SET itiraf_channel_id = ? WHERE server_id = ?", (channel_id, server_id))
            await db.commit()

    async def set_autorole(self, server_id, role_id):
        await self.does_server_exists(server_id)
        async with self.get_db() as db:
            await db.execute("UPDATE server SET autorole = ? WHERE server_id = ?", (role_id, server_id))
            
            await db.commit()

    async def set_trivia_channel(self, server_id, channel_id):
        await self.does_server_exists(server_id)

        async with self.get_db() as db:
            await db.execute("UPDATE server SET trivia_channel_id = ? WHERE server_id = ?", (channel_id, server_id))
            await db.commit()
    
    async def set_level_channel(self, server_id, channel_id):
        await self.does_server_exists(server_id)
        async with self.get_db() as db:
            await db.execute("UPDATE server SET level_channel_id = ? WHERE server_id = ?", (channel_id, server_id))
            await db.commit()
    
    async def set_tag(self, server_id, tag):
        await self.does_server_exists(server_id)
        async with self.get_db() as db:
            await db.execute("UPDATE server SET tag = ? WHERE server_id = ?", (tag, server_id))
            await db.commit()
    
    async def get_xp_leadership(self, server_id, limit=15):
        async with self.get_db() as db:
            async with db.execute("SELECT user_id, xp, level FROM users WHERE server_id = ? ORDER BY xp DESC LIMIT ?", (server_id, limit)) as cursor:
                
                return await cursor.fetchall()
            
    #veri üzerine ekleme fonksiyonları

    #mesaj ekleme 
    async def add_message(self, server_id, user_id):
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute(
                """UPDATE users SET message=message+1, weekly_message=weekly_message+1
                    WHERE server_id = ? AND user_id =?""", (server_id, user_id))
            await db.commit()


    async def add_voice(self, server_id, user_id, seconds):
        await self.does_user_exists(server_id, user_id)
        add_xp = int(seconds / 60) * 2 
        #dakika basi 2 xp
        async with self.get_db() as db:
            await db.execute("""
                        UPDATE users SET voice_sec = voice_sec + ?, weekly_voice = weekly_voice + ?, xp = xp + ? 
                              WHERE server_id=? AND user_id=? """,
                              (seconds, seconds, add_xp, server_id, user_id))
            await db.commit()

    async def add_coin(self, server_id, user_id, botcoin=0):
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute("""
                             UPDATE users SET botcoin=botcoin+? WHERE server_id=? AND user_id=?""",
                             (botcoin, server_id, user_id))
            await db.commit()

    async def add_xp(self, server_id, user_id, xp=0):
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET xp=xp+? WHERE server_id=? AND user_id=?""",
                             (xp, server_id, user_id))
            await db.commit()

    #sosyal ve ekonomi isleri

    async def set_partner(self, server_id, user1, user2):
        
        await self.does_user_exists(server_id, user1)
        await self.does_user_exists(server_id, user2)
        
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET partner_id = ? WHERE server_id=? AND user_id=? """, (user2, server_id, user1))
            
            await db.execute("""UPDATE users SET partner_id = ? WHERE server_id=? AND user_id=? """, (user1, server_id, user2))
            await db.commit()

    async def divorce_partner(self, server_id, user1, user2):
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET partner_id=NULL WHERE server_id=? AND user_id=? """, (server_id, user1))
            
            await db.execute("""UPDATE users SET partner_id=NULL WHERE server_id=? AND user_id=? """, (server_id, user2))
            await db.commit()

    async def add_rep(self, server_id, giver_user, taker_user):
        current_time = int(time.time())
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET last_rep=? WHERE server_id=? AND user_id=? """, (current_time, server_id, giver_user))
            await db.execute("""UPDATE users SET rep=rep+1 WHERE server_id=? AND user_id=?""", (server_id, taker_user))
            await db.commit()

    async def claim_daily(self, server_id, user_id, amount):
        current_time = int(time.time())
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET last_daily=?, xp=xp+? WHERE server_id=? AND user_id=? """, (current_time, amount, server_id, user_id))
            await db.commit()

    #itiraf ve sır icin vb

    async def add_secret(self, server_id, secret):
        async with self.get_db() as db:
            await db.execute("""INSERT INTO secrets (server_id, secret) VALUES (?, ?)""", (server_id, secret))
            await db.commit()

    async def random_secret(self, server_id):
        async with self.get_db() as db:
            async with db.execute("""SELECT secret FROM secrets WHERE server_id=? ORDER BY RANDOM() LIMIT 1""", (server_id,)) as cursor:
                row = await cursor.fetchone()
                return row["secret"] if row else None

    #buton rolleri icin

    async def add_reaction_role(self, server_id, message_id, emoji, role_id):
        async with self.get_db() as db:
            await db.execute("""INSERT OR IGNORE INTO reaction_roles (server_id, message_id, emoji, role_id) VALUES (?, ?, ?, ?)""", (server_id, message_id, emoji, role_id))
            await db.commit()
            
    async def get_reaction_roles(self, server_id, message_id, emoji):
        async with self.get_db() as db:
            async with db.execute("""
                        SELECT role_id FROM reaction_roles
                        WHERE server_id=? AND message_id=? AND emoji=?""",
                        (server_id, message_id, emoji)) as cursor:
                        row = await cursor.fetchone()
                        return row[0] if row else None
    
    async def remove_reaction_role(self, server_id, message_id, emoji):
        async with self.get_db() as db:
            await db.execute("""DELETE FROM reaction_roles WHERE server_id=? AND message_id=? AND emoji=?""", (server_id, message_id, emoji))
            await db.commit()

    #temp channels (ozel odalar)

    async def make_tempChannel(self, channel_id, owner_id, server_id): 
        async with self.get_db() as db:
            await db.execute("""INSERT OR IGNORE INTO temp_channels (channel_id, server_id, owner_id) VALUES (?, ?, ?)""", (channel_id, server_id, owner_id))
            await db.commit()

    async def get_expired_tc(self):
        limit_time = int(time.time()) - 3600 # 1 saat sonra silinio
        async with self.get_db() as db:
            async with db.execute("SELECT channel_id FROM temp_channels WHERE create_time < ?", (limit_time,)) as cursor:
                return await cursor.fetchall()
    
    async def delete_expired_tc(self, channel_id):
        async with self.get_db() as db:
            await db.execute("DELETE FROM temp_channels WHERE channel_id = ?", (channel_id,))
            await db.commit()

    #haftalık sıfırlama fonksiyonu
    async def reset_weekly(self):
        async with self.get_db() as db:
            await db.execute("UPDATE users SET weekly_message = 0, weekly_voice = 0")
            await db.commit()

    #level xp ayarlama (admin icin demo seyi)

    async def set_user_level(self, server_id, user_id, level): 
        
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET level=? WHERE server_id=? AND user_id=?""", (level, server_id, user_id))
            await db.commit()

    async def set_user_xp(self, server_id, user_id, xp): 

        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET xp=? WHERE server_id=? AND user_id=?""", (xp, server_id, user_id))
            await db.commit()

    async def set_user_coin(self, server_id, user_id, botcoin):
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET botcoin=? WHERE server_id=? AND user_id=?""", (botcoin, server_id, user_id))
            await db.commit()

    # afk

    async def set_afk(self, server_id, user_id, why):
        await self.does_user_exists(server_id, user_id)
        current_time = int(time.time())
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET afk_reason=?, afk_timestamp= ? WHERE server_id=? AND user_id=? """, (why, current_time, server_id, user_id))
            await db.commit()

    async def remove_afk(self, server_id, user_id):
        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:

            await db.execute("""UPDATE users SET afk_reason=NULL, afk_timestamp= NULL WHERE server_id=? AND user_id=? """, (server_id, user_id))
            await db.commit()


#invite sayacı
    async def invite_count(self, server_id, user_id, invites=0):

        await self.does_user_exists(server_id, user_id)
        async with self.get_db() as db:
            await db.execute("""UPDATE users SET invites=invites+? WHERE server_id=? AND user_id=? """, (invites, server_id, user_id))
            await db.commit()