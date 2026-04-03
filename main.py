import discord
import os

intents = discord.Intents.default()
intents.message_content = True   # Required to read messages
intents.members = True           # Required to manage roles

client = discord.Client(intents=intents)

# === CONFIGURATION via Environment Variables (set these on Railway) ===
CHANNEL_ID = os.getenv("WL_CHANNEL_ID")          # Must be a string of the channel ID
WHITELIST_ROLE_ID = os.getenv("WL_ROLE_ID")      # Must be a string of the role ID
TRIGGER_WORD = os.getenv("WL_TRIGGER", "wl").lower()  # Default is "wl", you can change it

@client.event
async def on_ready():
    print(f'✅ Bot is online as {client.user}')
    print(f'📍 Watching channel ID: {CHANNEL_ID}')
    print(f'🎖️  Whitelist role ID: {WHITELIST_ROLE_ID}')
    print(f'🔍 Trigger word: "{TRIGGER_WORD}"')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Only respond in the configured channel
    if str(message.channel.id) != CHANNEL_ID:
        return

    # Check for the trigger word (case-insensitive)
    if TRIGGER_WORD in message.content.lower():
        # Get the role using ID (more reliable than name)
        role = message.guild.get_role(int(WHITELIST_ROLE_ID))
        
        if role is None:
            print(f"⚠️ Role with ID {WHITELIST_ROLE_ID} not found!")
            return

        # Add the role if the user doesn't have it
        if role not in message.author.roles:
            try:
                await message.author.add_roles(role)
                print(f"✅ Added {role.name} role to {message.author}")
            except discord.Forbidden:
                print("❌ Bot doesn't have permission to add this role (check role hierarchy)")
            except Exception as e:
                print(f"❌ Error adding role: {e}")

        # Add ✅ reaction to the message
        try:
            await message.add_reaction("✅")
        except Exception as e:
            print(f"❌ Error adding reaction: {e}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN is not set!")
    elif not CHANNEL_ID or not WHITELIST_ROLE_ID:
        print("❌ Missing WL_CHANNEL_ID or WL_ROLE_ID environment variables!")
    else:
        client.run(token)
