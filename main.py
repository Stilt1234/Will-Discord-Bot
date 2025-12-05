import discord
from discord.ext import commands
import mcstatus
from mcrcon import MCRcon, MCRconException
from dotenv import load_dotenv, set_key
import os
from typing import Optional
import socket

load_dotenv(override=True)

bot = commands.Bot(command_prefix="/", description="Its Will! Use word WILL for a surprise!", intents=discord.Intents.all())
mc_server_ip = os.getenv("MC_SERVER_IP")
mc_server_rcon_password = os.getenv("MC_SERVER_RCON_PASSWORD")
will_emoji = None
will_cube_emoji = None

# TODO: Add /server_status, /playercount, /feed and /rcon_password (/rcon password will have both get and set options just like /server_ip)
# TODO: Add error handling for admin only commands
# TODO: Use three backtick formatting (``` ```) for server ip and rcon password.
# TODO: Check for invalid rcon password in /say and /command

def save_env_var(env_filepath=".env", key: str=None, value: str=None):
    if(not os.path.exists(env_filepath)):
        print("No .env file found.")
    elif(not key):
        raise ValueError("No key has been provided.")
    elif(not value):
        raise ValueError("No value has been provided.")
    set_key(env_filepath, key, value)

# TODO: Add this to /say, /command, /rcon_password, /server_status and /playercount

# TODO: Use this in /rcon_password, /say and /announce
def valid_server_details(ctx: commands.Context, ip: str, rcon_password: str):
    if(ip == None or len(ip) == 0):
        ctx.send("");
    elif(rcon_password == None or len(rcon_password) == 0):
        pass
    try:
        with MCRcon(ip, rcon_password) as rcon:
            return True
    except socket.gaierror:
        ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Server IP is incorrect.", timestamp=ctx.message.created_at))
    except ConnectionRefusedError:
        ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Server is offline.", timestamp=ctx.message.created_at))
    except MCRconException as e:
        ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="RCON Password is incorrect.", timestamp=ctx.message.created_at))
    except Exception as e:
        ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title=f"Unexpected error has occured : {e}.", timestamp=ctx.message.created_at))
    
    return False

@bot.event
async def on_ready():
    print("Will has spawned!")
    

@bot.event
async def on_message(message: discord.Message):
    if(message.author == bot.user):
        return
    
    # Check for dm.
    if(message.guild != None):
        will_emoji = discord.utils.get(message.guild.emojis, name = "will")
        will_cube_emoji = discord.utils.get(message.guild.emojis, name="willcube")
        if(message.content.find("WILL") != -1 and will_emoji != None):
            await message.add_reaction(will_emoji)
            await message.add_reaction(will_cube_emoji)
        elif(discord.utils.get(message.guild.emojis, name = "will") == None):
            await message.channel.send(embed=discord.Embed(colour=discord.Colour.red(), title="Please upload will emoji.", timestamp=message.created_at))
    await bot.process_commands(message)

@bot.hybrid_command(name="server_ip", description="Sets mc server ip. Only for admins.")
async def server_ip(ctx: commands.Context, server_ip: Optional[str]):
    if(not server_ip):
        await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title=f"Minecraft Server IP is {mc_server_ip}.", timestamp=ctx.message.created_at))
        return
    elif(not ctx.author.guild_permissions.administrator):
        await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="You do not have the permission to set Minecraft Server IP as you are not an administrator.", timestamp=ctx.message.created_at))
        return

    mc_server_ip = server_ip
    save_env_var(key="MC_SERVER_IP", value=mc_server_ip)
    await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title=f"Saved Minecraft Server IP as {mc_server_ip}.", timestamp=ctx.message.created_at))

@bot.hybrid_command(name="rcon_password", description="Sets mc server rcon password. Only for admins.")
async def recon_password(ctx: commands.Context, rcon_password: Optional[str]):
    if(not rcon_password):
        await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title=f"RCON Password is {mc_server_rcon_password}.", timestamp=ctx.message.created_at))
        return

    valid_server_details()

    mc_server_rcon_password = rcon_password
    save_env_var(key="MC_SERVER_RCON_PASSWORD", value=mc_server_rcon_password)
    await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title=f"RCON Password is set to {mc_server_rcon_password}."))

@bot.hybrid_command(name="say", description="Send a server message in the mc server. Only for admins.")
async def say(ctx: commands.Context, msg: str):
    if(not ctx.author.guild_permissions.administrator):
        await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="You do not have the permission to execute this command as you are not an administrator.", timestamp=ctx.message.created_at))
        return
    elif(not mc_server_rcon_password):
        await ctx.send(embed=discord.Embed(color=discord.Colour.red(), title="RCON password has not yet been set. Please use /rcon_password command to set the RCON password.", timestamp=ctx.message.created_at))
        return

    with MCRcon(host=mc_server_ip, password=mc_server_rcon_password) as rcon:
        rcon.command(f"/say {msg}")

    await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title="Message sent to Minecraft Server successfully."))

@bot.hybrid_command(name="command", description="Executes the given command in the minecraft server.")
async def command(ctx: commands.Context, com: str):
    if(not ctx.author.guild_permissions.administrator):
        await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="You do not have the permission to execute this command as you are not an administrator.", timestamp=ctx.message.created_at))
        return
    elif(not mc_server_rcon_password):
        await ctx.send(embed=discord.Embed(color=discord.Colour.red(), title="RCON password has not yet been set. Please use /rcon_password command to set the RCON password.", timestamp=ctx.message.created_at))
        return
    elif(not com.startswith("/")):
        com = "/" + com
    
    with MCRcon(host=mc_server_ip, password=mc_server_rcon_password) as rcon:
        rcon.command(com)

    await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title="Command executed on Minecraft Server successfully."))

@bot.hybrid_command(name="will_say", description="Make's Will say whatever you input as an argument.")
async def will_say(ctx: commands.Context, content: str):
    await ctx.send(content)

@bot.hybrid_command(name="announce")
async def announce(ctx: commands.Context, content: str):
    if(not ctx.author.guild_permissions.administrator):
        await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="You do not have the permission to execute this command as you are not an administrator.", timestamp=ctx.message.created_at))
        return

    await ctx.interaction.response.defer()
    list = []

    for member in ctx.guild.members:
        try:
            if(member.bot):
                continue
            await member.send(f"Announcement from {ctx.guild.name} ->\n{content}")
        except:
            list.append(member.mention)

    if(not list):
        await ctx.interaction.followup.send(embed=discord.Embed(colour=discord.Colour.green(), title="Announcement sent to all members successfully.", timestamp=ctx.message.created_at))
    else:
        string = ""
        for i in list:
            string += f"{i}\n"
        if(len(list) > 1):
            await ctx.interaction.followup.send(embed=discord.Embed(colour=discord.Colour.orange(), title=f"Could not send announcement to the following {len(list)} people as they have disabled DM's from server members who are not their friends in their privacy settings ->\n", description=string, timestamp=ctx.message.created_at))
        else:
            await ctx.interaction.followup.send(embed=discord.Embed(colour=discord.Colour.orange(), title=f"Could not send announcement to the following person as they have disabled DM's from server members who are not their friends in their privacy settings ->\n", description=string, timestamp=ctx.message.created_at))

@bot.hybrid_command(name="sync", description="Used to sync commands.")
async def sync(ctx: commands.Context):
    await bot.tree.sync()
    await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), title="Synced commands.", timestamp=ctx.message.created_at))

bot.run(os.getenv("TOKEN"))