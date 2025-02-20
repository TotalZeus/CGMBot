Discord Glucose Monitor Bot

Description

This is a Discord bot that monitors glucose levels using the Dexcom API. The bot retrieves real-time glucose readings and updates its status accordingly. 
Additionally, users can set upper and lower glucose limits, receiving alerts when their glucose levels exceed these thresholds.

Features
1. Retrieves glucose readings from the Dexcom API.
2. Updates Discord bot status with current glucose level and trend.
3. Allows authorized users to set glucose level limits.
4. Sends direct messages to users when glucose levels exceed the set thresholds.

Requirements

Python 3.8+
Required Python libraries:
1. discord.py
2. asyncio
3. pydexcom

Installation

1. Clone this repository or download the script.
2. Install dependencies:
   pip install discord.py asyncio pydexcom

3. Set up a bot on the Discord Developer Portal and obtain a bot token.
4. Replace BOT_TOKEN in the script with your actual bot token.

Usage

1. Run the bot:
   python script.py
2. Commands:
   %setlimits <lower> <upper>: Set glucose limits (authorized users only).
   %getlimits: Retrieve currently set glucose limits.

Notes

1. The bot continuously fetches glucose readings every 60 seconds.
2. The Dexcom username and password are hardcoded in the script. Consider using environment variables or a configuration file for security.
3. The bot token should be kept private to prevent unauthorized access.

Security Warning

Do not expose your bot token or Dexcom credentials in a public repository.

Author
Nicholas Munoz

