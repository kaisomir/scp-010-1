import random
import discord
import json

bot = discord.Bot()

config = json.loads(open('config.json', 'r').read())
token = config['token']
users = config['users']          # UUIDs with perms
s_perms = config['shock_perms']  # role IDs with perms
admins = config['admins']        # UUIDs with pause perms
a_perms = config['admin_roles']  # role IDs with pause perms
channel = config['channel']      # target channel/thread ID - redirects flood
guild = config['guild']          # server (bot is currently single-server only)
target = config['target']        # target user
variants = config['variants']    # fancy text for target
admins.append(target)            # I will not support nonconsensual pinging

calluser = None  # test initialiser
testing = False  # test ongoing
paused = False   # testing halted


@bot.slash_command(guild_ids=[guild])
async def kill(ctx):
    global calluser, testing, paused, variants
    if testing:
        await ctx.respond('Testing is already ongoing.')
        return
    elif ctx.channel.id != channel:
        await ctx.respond(f'This command only works in <#{channel}>.')
        return
    elif paused:
        await ctx.respond('Testing has been temporarily halted. '
                          'Please check back later.')
        return

    perms = False
    if ctx.interaction.user.id in users:
        perms = True
    else:
        for role in s_perms:
            if ctx.interaction.user.get_role(role):
                perms = True
                break

    if perms and not calluser:
        calluser = ctx.interaction.user

        print(f'Starting with user {calluser.name}')

        choice = random.randint(2, 7)
        variants = []
        variant = variants[choice-2]
        await ctx.respond(f'Testing with SCP-010-{choice} on '
                          f'<@{target}> (species {variant[0]}, '
                          f'variant {variant[1]}) will now commence.')
        testing = True
    else:
        await ctx.respond('You are not an authorised SCP-010-1 '
                          'administrator.')
        return

    while testing:
        await ctx.send(f'<@{target}>')


@bot.slash_command(guild_ids=[guild])
async def stop(ctx):
    global testing, admins, a_perms

    if not testing:
        await ctx.respond('There is currently no ongoing testing.')
        return

    perms = False
    if ctx.interaction.user == calluser or ctx.interaction.user.id in admins:
        perms = True
    else:
        for role in a_perms:
            if ctx.guild.get_role(role) in ctx.interaction.user.roles:
                perms = True
                break

    if perms and testing:
        print(f'Testing stopped by user {ctx.interaction.user.name}')
        testing = False
        await ctx.respond('Testing has ceased.')
    else:
        await ctx.respond('You have no power here. Testing must go on.')


@bot.slash_command(guild_ids=[guild])
async def pause(ctx):
    global admins, a_perms, paused, testing

    if paused:
        await ctx.respond('Testing is already halted.')
        return

    perms = False
    if ctx.interaction.user.id in admins:
        perms = True
    else:
        for role in a_perms:
            if ctx.guild.get_role(role) in ctx.interaction.user.roles:
                perms = True
                break

    if perms:
        testing = False
        paused = True
    else:
        await ctx.respond('You may not halt testing.')


@bot.slash_command(guild_ids=[guild])
async def unpause(ctx):
    global admins, a_perms, paused, testing

    if not paused:
        await ctx.respond('Testing is not halted.')
        return

    perms = False
    if ctx.interaction.user.id in admins:
        perms = True
    else:
        for role in a_perms:
            if ctx.guild.get_role(role) in ctx.interaction.user.roles:
                perms = True
                break

    if perms:
        paused = False
    else:
        await ctx.respond('You may not resume testing.')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


bot.run(token)
