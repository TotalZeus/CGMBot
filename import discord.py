import discord
from discord.ext import commands
import asyncio
from pydexcom import Dexcom

intents = discord.Intents.all()
client = commands.Bot(command_prefix='%', help_command=None, intents=intents)

# Dictionary to store user-defined lower and upper limits
glucose_limits = {}

@client.event
async def on_ready():
    print(f'You have logged in as {client}')
    print('Bot is online!')

async def ch_pr():
    await client.wait_until_ready()

    while not client.is_closed():
        dexcom = Dexcom("nick2003", "2003nickm")
        glucose_reading = dexcom.get_current_glucose_reading()
        arrow = glucose_reading.trend_arrow
        print(glucose_reading)
        print(arrow)

        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Glucose {glucose_reading}mg/dL ({arrow})"))
        
        # Check if glucose reading is outside user-defined limits and send warning
        for user_id, limits in glucose_limits.items():
            if glucose_reading.value < limits['lower']:
                user = client.get_user(user_id)
                await user.send(f"Warning: Glucose level is below {limits['lower']} ({arrow})!")
            elif glucose_reading.value > limits['upper']:
                user = client.get_user(user_id)
                await user.send(f"Warning: Glucose level is above {limits['upper']}({arrow})!")

        await asyncio.sleep(60)

@client.command()
async def setlimits(ctx, lower: int, upper: int):
    # Check if the command invoker has the correct user ID
    if ctx.author.id != 386373553009983491:
        await ctx.send("Sorry, you are not authorized to use this command.")
        return
    
    # Set lower and upper limits for the user
    glucose_limits[ctx.author.id] = {'lower': lower, 'upper': upper}
    await ctx.send(f"Glucose limits set: Lower: {lower}, Upper: {upper}")

@client.command()
async def getlimits(ctx):
    # Check if any limits are set
    if glucose_limits:
        limit_message = "\n".join([f"User {client.get_user(user_id).name}: Lower: {limits['lower']}, Upper: {limits['upper']}" for user_id, limits in glucose_limits.items()])
        await ctx.send("Current glucose limits:\n" + limit_message)
    else:
        await ctx.send("No glucose limits set.")

client.loop.create_task(ch_pr())
BOT_TOKEN = 'MTIzMjIxMzI5Mjg3MzgxNDAzNg.GVDmb3.X9PrNj7nRz711qXm4_4J7AYj-0qKSfMHDYKW0Y'
client.run(BOT_TOKEN)