import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3
from pydexcom import Dexcom 

intents = discord.Intents.all()
client = commands.Bot(command_prefix='%', help_command=None, intents=intents)

# Set up SQLite database
conn = sqlite3.connect('glucose_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, 
                username TEXT, 
                password TEXT, 
                lower INTEGER DEFAULT 70, 
                upper INTEGER DEFAULT 180)''')
conn.commit()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    check_glucose_levels.start()
    
    dexcom = Dexcom("Dexcom Username", "Dexcom Password")
    glucose_reading = dexcom.get_current_glucose_reading()
    arrow = glucose_reading.trend_arrow
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Glucose {glucose_reading}mg/dL ({arrow})"))

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        if message.content.lower().startswith("setcredentials"):
            parts = message.content.split()
            if len(parts) == 3:
                await setcredentials_dm(message, parts[1], parts[2])
            else:
                await message.channel.send("Usage: setcredentials <username> <password>")
        elif message.content.lower().startswith("setlimits"):
            parts = message.content.split()
            if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
                await setlimits_dm(message, int(parts[1]), int(parts[2]))
            else:
                await message.channel.send("Usage: setlimits <lower> <upper>")
        elif message.content.lower().startswith("getglucose"):
            await getglucose_dm(message)
        elif message.content.lower().startswith("getdata"):
            await getdata_dm(message)
        else:
            await message.channel.send("Invalid command. Available: setcredentials, setlimits, getglucose, getdata.")
    await client.process_commands(message)

async def setcredentials_dm(message, username, password):
    c.execute("INSERT OR REPLACE INTO users (user_id, username, password) VALUES (?, ?, ?)",
              (message.author.id, username, password))
    conn.commit()
    await message.channel.send("Dexcom credentials saved! Use setlimits to configure glucose alerts.")

async def setlimits_dm(message, lower, upper):
    c.execute("UPDATE users SET lower = ?, upper = ? WHERE user_id = ?", (lower, upper, message.author.id))
    conn.commit()
    await message.channel.send(f"Glucose limits set: Lower: {lower}, Upper: {upper}")

async def getglucose_dm(message):
    c.execute("SELECT username, password FROM users WHERE user_id = ?", (message.author.id,))
    user = c.fetchone()
    
    if not user:
        await message.channel.send("You need to set your Dexcom credentials first using setcredentials.")
        return
    
    username, password = user
    response = await message.channel.send("Fetching your glucose levels... ⏳")
    
    try:
        dexcom = Dexcom(username, password)
        glucose_reading = dexcom.get_current_glucose_reading()
        arrow = glucose_reading.trend_arrow
        await response.edit(content=f"Your current glucose level is {glucose_reading.value} mg/dL ({arrow}).")
    except Exception as e:
        await response.edit(content=f"Error retrieving glucose data: {e}")

async def getdata_dm(message):
    c.execute("SELECT username, lower, upper FROM users WHERE user_id = ?", (message.author.id,))
    user_data = c.fetchone()
    
    if not user_data:
        await message.channel.send("No data found. Please set your credentials and limits first.")
        return
    
    username, lower, upper = user_data
    await message.channel.send(f"Stored Data:\nUsername: {username}\nLower Limit: {lower}\nUpper Limit: {upper}")


@client.command()
async def getglucose(ctx):
    c.execute("SELECT username, password FROM users WHERE user_id = ?", (ctx.author.id,))
    user = c.fetchone()
    
    if not user:
        await ctx.send("You need to set your Dexcom credentials first using %setcredentials.")
        return
    
    username, password = user
    message = await ctx.send("Fetching your glucose levels... ⏳")
    
    try:
        dexcom = Dexcom(username, password)
        glucose_reading = dexcom.get_current_glucose_reading()
        arrow = glucose_reading.trend_arrow
        await message.edit(content=f"Your current glucose level is {glucose_reading.value} mg/dL ({arrow}).")
    except Exception as e:
        await message.edit(content=f"Error retrieving glucose data: {e}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑 Deleted {amount} messages.", delete_after=3)

@client.command()
async def removedata(ctx, option: str = "all"):
    if option == "credentials":
        c.execute("UPDATE users SET username = NULL, password = NULL WHERE user_id = ?", (ctx.author.id,))
        conn.commit()
        await ctx.send("Your Dexcom credentials have been removed.")
    elif option == "limits":
        c.execute("UPDATE users SET lower = 70, upper = 180 WHERE user_id = ?", (ctx.author.id,))
        conn.commit()
        await ctx.send("Your glucose limits have been reset to default (70-180 mg/dL).")
    elif option == "all":
        c.execute("DELETE FROM users WHERE user_id = ?", (ctx.author.id,))
        conn.commit()
        await ctx.send("All your stored data has been removed.")
    else:
        await ctx.send("Invalid option. Use 'credentials', 'limits', or 'all'.")
    

@client.command()
async def getdata(ctx):
    c.execute("SELECT username, lower, upper FROM users WHERE user_id = ?", (ctx.author.id,))
    user_data = c.fetchone()
    
    if not user_data:
        await ctx.send("No data found. Please set your credentials and limits first.")
        return
    
    username, lower, upper = user_data
    await ctx.send(f"Stored Data:\nUsername: {username}\nLower Limit: {lower}\nUpper Limit: {upper}")

@client.command()
async def setlimits(ctx, lower: int, upper: int):
    c.execute("UPDATE users SET lower = ?, upper = ? WHERE user_id = ?", (lower, upper, ctx.author.id))
    conn.commit()
    await ctx.send(f"Glucose limits set: Lower: {lower}, Upper: {upper}")

@tasks.loop(minutes=1)
async def check_glucose_levels():
    c.execute("SELECT user_id, username, password, lower, upper FROM users")
    users = c.fetchall()
    
    for user_id, username, password, lower, upper in users:
        try:
            dexcom = Dexcom(username, password)
            glucose_reading = dexcom.get_current_glucose_reading()
            arrow = glucose_reading.trend_arrow
            
            # Check limits
            if glucose_reading.value < lower:
                user = await client.fetch_user(user_id)
                await user.send(f"⚠️ Warning: Glucose level is below {lower} mg/dL ({arrow})!")
            elif glucose_reading.value > upper:
                user = await client.fetch_user(user_id)
                await user.send(f"⚠️ Warning: Glucose level is above {upper} mg/dL ({arrow})!")
        except Exception as e:
            print(f"Error checking glucose for {user_id}: {e}")

BOT_TOKEN = 'Insert Discord Bot Token'
client.run(BOT_TOKEN)
