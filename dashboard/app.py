from quart import Quart, render_template, request, session, redirect, url_for, g
import aiosqlite
import os
import aiohttp
from dotenv import load_dotenv
import sys

#configi alıyoruz
import config

app = Quart(__name__)
app.secret_key = config.SECRET_KEY
API_BASE_URL = 'https://discord.com/api/v10'

#mainden bot instance aliyoruz
bot_instance = None

def init_dashboard(bot):
    #global bot instance
    global bot_instance
    bot_instance = bot

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/login')
async def login():
    redirect_uri = config.REDIRECT_URI 
    #configten aldık
    scope = 'identify guilds' 
    #botun guildleri okuyabilmesini istiyoruz
    discord_login_url = (
        f"{API_BASE_URL}/oauth2/authorize"
        f"?client_id={config.CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
    )
    return redirect(discord_login_url)

@app.route('/callback') #callback fonksiyonu
async def callback():
    code = request.args.get('code')
    if not code:
        return "Kod bulunamadı", 400

    data = {
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.REDIRECT_URI
    }
    #token aliyoruz
    async with aiohttp.ClientSession() as http:
        async with http.post(f"{API_BASE_URL}/oauth2/token", data=data) as resp:
            token_resp = await resp.json()
            
    if 'access_token' not in token_resp:
        return f"Giriş başarısız: {token_resp}", 400

    session['access_token'] = token_resp['access_token']
    
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    async with aiohttp.ClientSession() as http:
        async with http.get(f"{API_BASE_URL}/users/@me", headers=headers) as resp:
            user_info = await resp.json()
            session['user'] = user_info

    return redirect(url_for('dashboard'))

@app.route('/logout') #logout fonksiyonu
async def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
 #dashboard fonksiyonu
async def dashboard():
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    token = session['access_token']
    headers = {'Authorization': f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as http:
        async with http.get(f"{API_BASE_URL}/users/@me/guilds", headers=headers) as resp:
            user_guilds = await resp.json()
            
    manageable_guilds = []
    
    #bot instance db
    async with bot_instance.db.get_db() as db: 
        async with db.execute("SELECT server_id FROM allowed_servers") as cursor:
            allowed_ids = [row[0] async for row in cursor]
    
    #user guilds
    for guild in user_guilds:
        permissions = int(guild['permissions'])
        is_manager = (permissions & 0x20) == 0x20
        is_owner = guild['owner']
        is_licensed = int(guild['id']) in allowed_ids
        
        if (is_manager or is_owner) and is_licensed:
             manageable_guilds.append(guild)

    return await render_template('dashboard.html', user=session['user'], guilds=manageable_guilds)

#leaderboard
@app.route('/leaderboard/<int:server_id>')
async def leaderboard(server_id):
    async with bot_instance.db.get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT user_id, xp, level, botcoin FROM users WHERE server_id = ? ORDER BY xp DESC LIMIT 10", (server_id,)) as cursor:
            users = await cursor.fetchall()
            
    return await render_template('leaderboard.html', users=users, server_id=server_id)

#settings
@app.route('/settings/<int:server_id>', methods=['GET', 'POST'])
async def settings(server_id):
    if 'access_token' not in session:
        return redirect(url_for('index'))
        
    #güvenlik kontrolü
    
    if request.method == 'POST':
        form = await request.form
        prefix = form.get('prefix')
        log_channel = form.get('log_channel')
        autorole = form.get('autorole')
        
        if prefix:
            await bot_instance.db.set_prefix(server_id, prefix)
        
        #channel role güncelleme
        async def update_setting(field_name, set_func):
            val_str = form.get(field_name)
            if val_str:
                val = int(val_str) if val_str.isdigit() and int(val_str) > 0 else None
                #set func
                await set_func(server_id, val)

        await update_setting('log_channel', bot_instance.db.set_log_channel)
        await update_setting('itiraf_channel', bot_instance.db.set_itiraf_channel)
        await update_setting('trivia_channel', bot_instance.db.set_trivia_channel)
        await update_setting('level_channel', bot_instance.db.set_level_channel)
        await update_setting('autorole', bot_instance.db.set_autorole)

        tag = form.get('tag')
        if tag is not None: 
             await bot_instance.db.set_tag(server_id, tag)
            
        return redirect(url_for('settings', server_id=server_id))

    #settings get
    server_settings = await bot_instance.db.get_server_settings(server_id)
    
    #channels roles
    guild = bot_instance.get_guild(server_id)
    text_channels = []
    roles = []
    
    if guild:
        text_channels = [c for c in guild.text_channels]
        roles = [r for r in guild.roles if not r.is_default()]
    
    return await render_template(
        'settings.html', 
        server=guild, 
        settings=server_settings, 
        channels=text_channels, 
        roles=roles,
        server_id=server_id
    )
