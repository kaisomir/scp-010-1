import random
import discord
import json

bot = discord.Bot()

config = json.loads(open('config.json', 'r').read())
token = config['token']

users, p_perms = config['users'], config['ping_perms']
admins, a_perms = config['admins'], config['admin_roles']
b_users, b_roles = config['blacklist'], config['blacklist_roles']
guild, channel = config['guild'], config['channel']
target, variants = config['target'], config['variants']
admins.append(target)
users.append(target)

calluser = None  # test initialiser
testing = False  # test ongoing
paused = False   # testing halted


def p_check_perms(ctx):
    global users, p_perms, b_users, b_roles

    if ctx.interaction.user.id in b_users:
        return False
    for role in b_roles:
        if ctx.interaction.user.get_role(role):
            return False
    if ctx.interaction.user.id in users:
        return True
    for role in p_perms:
        if ctx.interaction.user.get_role(role):
            return True


def a_check_perms(ctx):
    global admins, a_perms
    if ctx.interaction.user.id in admins:
        return True
    for role in a_perms:
        if ctx.guild.get_role(role) in ctx.interaction.user.roles:
            return True
    return False


@bot.slash_command(guild_ids=[guild],
                   description='Begin test.'
                   )
async def test(ctx):
    print(f'Command test called by {ctx.interaction.user}')
    global calluser, testing, paused, variants, channel

    if ctx.channel.id != channel:
        await ctx.respond(f'This command only works in <#{channel}>.')
        return
    elif testing:
        await ctx.respond('Testing is already ongoing.')
        return
    elif paused:
        await ctx.respond('Testing has been temporarily halted. '
                          'Please check back later.')
        return

    perms = p_check_perms(ctx)

    if perms and calluser is None:
        calluser = ctx.interaction.user

        print(f'User {calluser.name} started testing.')

        choice = random.randint(2, 7)
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


@bot.slash_command(guild_ids=[guild],
                   description='Stop ongoing test.'
                   )
async def stop(ctx):
    print(f'Command stop called by {ctx.interaction.user}')
    global testing, channel, calluser

    if ctx.channel.id != channel:
        await ctx.respond(f'This command only works in <#{channel}>.')
        return
    elif not testing:
        await ctx.respond('There is currently no ongoing testing.')
        return

    perms = p_check_perms(ctx)

    if perms and testing:
        print(f'Testing stopped by user {ctx.interaction.user.name}')
        testing = False
        await ctx.respond('Testing has ceased.')
        calluser = None
    else:
        await ctx.respond('You have no power here. Testing must go on.')


@bot.slash_command(guild_ids=[guild],
                   description='Temporarily halt testing.'
                   )
async def pause(ctx):
    print(f'Command pause called by {ctx.interaction.user}')
    global paused, testing, channel

    if ctx.channel.id != channel:
        await ctx.respond(f'This command only works in <#{channel}>.')
        return
    elif paused:
        await ctx.respond('Testing is already halted.')
        return

    perms = a_check_perms(ctx)

    if perms:
        testing = False
        paused = True
        print(f'Testing paused by {ctx.interaction.user}')
        await ctx.respond('Testing halted.')
    else:
        await ctx.respond('You may not halt testing.')


@bot.slash_command(guild_ids=[guild],
                   description='Resume testing.'
                   )
async def unpause(ctx):
    print(f'Command unpause called by {ctx.interaction.user}')
    global paused, testing, channel

    if ctx.channel.id != channel:
        await ctx.respond(f'This command only works in <#{channel}>.')
        return
    elif not paused:
        await ctx.respond('Testing is not halted.')
        return

    perms = a_check_perms(ctx)

    if perms:
        paused = False
        print(f'Testing unpaused by {ctx.interaction.user}')
        await ctx.respond('Testing resumed.')
    else:
        await ctx.respond('You may not resume testing.')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


bot.run(token)
