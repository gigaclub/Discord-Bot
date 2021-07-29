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
            for channel in guild.channels:
                if isinstance(channel, discord.channel.CategoryChannel):
                    register_category(channel)
                else:
                    register_channel(channel)
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

def check_if_category_exists(category_id):
    return bool(models.execute_kw(odoo_config.database, uid, odoo_config.password,
          'gc.discord.category', 'search_count',
          [[['discord_channel_uuid', '=', str(category_id)]]]))

def register_category(category):
    if not check_if_category_exists(category.id):
        models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.category', 'create', [{
            "discord_channel_uuid": str(category.id),
            "name": str(category.name),
        }])
    else:
        id = models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.category', 'search',
                          [[["discord_channel_uuid", '=', str(category.id)]]], {'limit': 1})
        category_id = id and id[0]
        if category_id:
            models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.category', 'write', [[category_id], {
                "name": str(category.name)
            }])

def check_if_channel_exists(channel_id):
    return bool(models.execute_kw(odoo_config.database, uid, odoo_config.password,
          'gc.discord.channel', 'search_count',
          [[['discord_channel_uuid', '=', str(channel_id)]]]))

def register_channel(channel):
    if not check_if_channel_exists(channel.id):
        type = False
        if isinstance(channel, discord.channel.TextChannel):
            type = "text"
            if channel.is_news():
                type = "announcement"
        elif isinstance(channel, discord.channel.VoiceChannel):
            type = "voice"
        elif isinstance(channel, discord.channel.StageChannel):
            type = "stage"
        if type:
            create_dict = {
                "discord_channel_uuid": str(channel.id),
                "name": str(channel.name),
                "type": type,
            }
            if channel.category:
                register_category(channel.category)
                id = models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.category', 'search',
                                  [[["discord_channel_uuid", '=', str(channel.category_id)]]], {'limit': 1})
                if id:
                    create_dict["category_id"] = id[0]
            models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.channel', 'create', [create_dict])
    else:
        id = models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.channel', 'search',
                          [[["discord_channel_uuid", '=', str(channel.id)]]], {'limit': 1})
        channel_id = id and id[0]
        if channel_id:
            write_dict = {
                "name": str(channel.name)
            }
            if channel.category:
                register_category(channel.category)
                id = models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.category', 'search',
                                       [[["discord_channel_uuid", '=', str(channel.category_id)]]], {'limit': 1})
                if id:
                    write_dict["category_id"] = id[0]
            models.execute_kw(odoo_config.database, uid, odoo_config.password, 'gc.discord.channel', 'write', [[channel_id], write_dict])

bot.run(config[0]["gc_discord_bot_token"])