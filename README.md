## Discord Glucose Monitor Bot

# 📌 Description

This Discord bot monitors glucose levels using the Dexcom API and securely stores user credentials and limits in an SQLite database. The bot retrieves real-time glucose readings, updates its status, and sends alerts when glucose levels exceed user-defined thresholds.

## 🚀 Features

✅ Retrieves glucose readings from the Dexcom API.

✅ Updates Discord bot status with the current glucose level and trend.

✅ Securely stores user credentials and glucose limits in an SQLite database.

✅ Allows users to set and update their glucose monitoring preferences.

✅ Sends direct messages when glucose levels exceed set thresholds.

✅ Supports DM commands for setting credentials, limits, and retrieving data.

✅ Admin command to purge messages.

✅ Automated glucose monitoring every minute.

## 🛠 Requirements

* Python 3.8+

* Required Python libraries:
*```sh
  pip install discord.py asyncio pydexcom sqlite3

## 🚀 Installation
Clone this repository or download the script.
Install dependencies:
sh
Copy
Edit
pip install discord.py asyncio pydexcom sqlite3
Set up a bot on the Discord Developer Portal and obtain a bot token.
Replace BOT_TOKEN in the script with your actual bot token.
## 📌 Usage
# ▶️ Run the bot:
sh
Copy
Edit
python script.py
## 💬 Available Commands
DM Commands
setcredentials <username> <password> → Store Dexcom credentials.
setlimits <lower> <upper> → Set glucose limits.
getglucose → Retrieve current glucose reading.
getdata → Display stored user data.
Guild Commands
%getglucose → Retrieve glucose reading (server command).
%removedata <option> → Remove user data (credentials, limits, or all).
%purge <amount> → Delete a specified number of messages (admin-only).
## 📌 Notes
✅ The bot fetches glucose readings every 60 seconds.
✅ Dexcom credentials are securely stored in an SQLite database.
✅ Keep your bot token private to prevent unauthorized access.

## ⚠️ Security Warning
❌ Do not expose your bot token or Dexcom credentials in a public repository.

## ✒️ Author
# Nicholas Munoz
