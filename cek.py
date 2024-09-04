import requests
import json
import time
from datetime import datetime, timedelta, timezone

# Configuration
config = {
    "url": "https://growtopiagame.com/detail/",
    "retries": 5,
    "retry_delay": 2,
    "timeout": 10,
    "player_thresholds": {
        "major_increase": 15000,
        "major_decrease": -20000,
        "minor_decrease": -4500,
    },
    "discord_webhooks": {
        "main": "https://discord.com/api/webhooks/1279845223702335498/-3Rauo8l5cT1tz5r84Soe6ka2-Zgn0fCIGFa7aqvfsSQ2ygOf1fp6BtNhY7H_tgYGb8t",
        "major_decrease": "https://discord.com/api/webhooks/1279845035533271052/R7ugvCw2eis2nW7QQ76vJALMvrBEDunBfmVwew0ucnlgbKtb-E8JmfSfU5eLl0pmIQS4",
        "minor_decrease": "https://discord.com/api/webhooks/1279843288483889253/uSFTnn9SE9rp8I8iToInjCeomXLqOeKoi-shfirorI4lkAObm0-JZcwTH1tkOt4mfElD",
    },
    "roles": {
        "banwave_or_hardwarp": "@BW/HW",
        "maintenance_or_crash": "@MAINTE/CRASH",
    },
    "emojis": {
        "megaphone": "<:megagt:1279846195098812563>",
        "up": "<:upg:1279846196566818960>",
        "down": "<:downg:1279846192838082651>",
        "boom": "<:boomgt:1279846190506184734>",
    },
    "check_interval": 10
}

# Global variable to store previous player count
previous_player_count = None

# Function to get the player count from the website
def get_player_count():
    url = config["url"]
    retries = config["retries"]
    for i in range(retries):
        try:
            response = requests.get(url, timeout=config["timeout"])
            if response.status_code == 200:
                try:
                    data = response.json()
                    player_count = data.get("online_user")
                    if player_count is not None:
                        return int(player_count)
                    else:
                        print("Could not find the player count in the JSON response.")
                        return None
                except json.JSONDecodeError:
                    print("Failed to decode JSON response.")
                    return None
            else:
                print(f"Failed to retrieve page: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {i + 1} failed: {e}")
            if i < retries - 1:
                time.sleep(config["retry_delay"])
            else:
                print("Max retries exceeded. Could not retrieve player count.")
                return None

# Function to send an embedded message to the Discord webhook
def send_to_discord(title, description, color, webhook_url):
    embed = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {
                "text": f"Made By Yuri :v       {get_current_time_pht()}"
            }
        }]
    }
    try:
        response = requests.post(webhook_url, json=embed, timeout=config["timeout"])
        if response.status_code == 204:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")

# Function to get current time in PHT (UTC+8) in 12-hour format
def get_current_time_pht():
    pht = timezone(timedelta(hours=8))
    return datetime.now(pht).strftime('%I:%M:%S %p')

# Function to get current Unix timestamp
def get_current_unix_timestamp():
    return int(time.time())

# Main loop to periodically check the player count and send to Discord
while True:
    player_count = get_player_count()
    if player_count is not None:
        current_time = get_current_time_pht()
        current_unix_timestamp = get_current_unix_timestamp()
        if previous_player_count is not None:
            difference = player_count - previous_player_count
            print(f"> Player count: {player_count}, Previous count: {previous_player_count}, Difference: {difference}")  # Debug print
            
            if difference > 0:
                if difference > config["player_thresholds"]["major_increase"]:
                    title = f"{config['emojis']['megaphone']} **Server is Back Online!** {config['emojis']['megaphone']}"
                    description = (
                        f"There are currently **{player_count}** online players!\n"
                        f"**+{difference}** {config['emojis']['megaphone']} ||@UP||"
                    )
                    color = 3066993
                    send_to_discord(title, description, color, config["discord_webhooks"]["main"])
                else:
                    title = f"{config['emojis']['megaphone']} **Player Count Update**"
                    description = (
                        f"There are currently **{player_count}** online players!\n"
                        f"**+{difference}** {config['emojis']['up']}"
                    )
                    color = 3066993
                    send_to_discord(title, description, color, config["discord_webhooks"]["main"])
            elif difference < 0:
                if difference < config["player_thresholds"]["major_decrease"]:
                    title = f"{config['emojis']['megaphone']} **Server Maintenance/Crash**"
                    description = (
                        f"The server had a {config['roles']['maintenance_or_crash']}!\n"
                        f"**{difference}** {config['emojis']['boom']}"
                    )
                    color = 15158332
                    send_to_discord(title, description, color, config["discord_webhooks"]["major_decrease"])
                    
                    title = f"{config['emojis']['megaphone']} **Player Count Update** {config['emojis']['megaphone']}"
                    description = (
                        f"There are currently **{player_count}** online players!\n"
                        f"**{difference}** {config['emojis']['down']}"
                    )
                    color = 15158332
                    send_to_discord(title, description, color, config["discord_webhooks"]["main"])
                    
                elif difference < config["player_thresholds"]["minor_decrease"]:
                    title = f"{config['emojis']['megaphone']} **Banwave/Hardwarp** {config['emojis']['megaphone']}"
                    description = (
                        f"The server had a {config['roles']['banwave_or_hardwarp']}!\n"
                        f"**{difference}** {config['emojis']['boom']}"
                    )
                    color = 15158332
                    send_to_discord(title, description, color, config["discord_webhooks"]["minor_decrease"])
                    
                    title = f"{config['emojis']['megaphone']} **Player Count Update** {config['emojis']['megaphone']}"
                    description = (
                        f"There are currently **{player_count}** online players!\n"
                        f"**{difference}** {config['emojis']['down']}"
                    )
                    color = 15158332
                    send_to_discord(title, description, color, config["discord_webhooks"]["main"])
                    
                else:
                    title = f"{config['emojis']['megaphone']} **Player Count Update** {config['emojis']['megaphone']}"
                    description = (
                        f"There are currently **{player_count}** online players!\n"
                        f"**{difference}** {config['emojis']['down']}"
                    )
                    color = 15158332
                    send_to_discord(title, description, color, config["discord_webhooks"]["main"])
            else:
                print(f"No change in player count: {player_count}")

            if difference != 0:
                print(f"Title: {title}\nDescription: {description}")
        
        previous_player_count = player_count
    else:
        print("Failed to retrieve player count.")
    
    time.sleep(config["check_interval"])
