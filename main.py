import discord
import odoo_config
import xmlrpc.client

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(odoo_config.hostname))
uid = common.authenticate(odoo_config.database, odoo_config.username, odoo_config.password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(odoo_config.hostname))

config = models.execute_kw(odoo_config.database, uid, odoo_config.password,
    'res.config.settings', 'search_read',
    [[['company_id', '=', 1]]],
    {'fields': ['gc_discord_bot_token', 'gc_discord_server_id'], 'limit': 1})

bot = discord.Client()

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    for guild in bot.guilds:
        if guild.id == int(config[0]["gc_discord_server_id"]):
            register_user(guild.owner_id)
            for member in guild.members:
                register_user(member.id)
            break

@bot.event
async def on_message(message):
    if message.guild.id == int(config[0]["gc_discord_server_id"]):
        if message.author == bot.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

def check_if_user_exists(user_id):
    return bool(models.execute_kw(odoo_config.database, uid, odoo_config.password,
        'gc.user', 'search_count',
        [[['discord_uuid', '=', str(user_id)]]]
    ))

def register_user(user_id):
    if not check_if_user_exists(user_id):
        models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.user', 'create', [{
            "discord_uuid": str(user_id)
        }])


bot.run(config[0]["gc_discord_bot_token"])