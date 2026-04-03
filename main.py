import discord
import os

# ====================== INTENTS ======================
intents = discord.Intents.default()
intents.message_content = True   # Needed to read message content
intents.members = True           # Needed to manage roles
intents.guilds = True            # Critical for on_message + guild access

client = discord.Client(intents=intents)

# ====================== CONFIG ======================
CHANNEL_ID = os.getenv("WL_CHANNEL_ID")          # Channel where users type the trigger
WHITELIST_ROLE_ID = os.getenv("WL_ROLE_ID")      # Role to give
TRIGGER_WORD = os.getenv("WL_TRIGGER", "wl").lower().strip()

@client.event
async def on_ready():
    print(f'✅ Bot is online as {client.user}')
    print(f'📍 Watching channel: {CHANNEL_ID}')
    print(f'🎖️  Whitelist role ID: {WHITELIST_ROLE_ID}')
    print(f'🔍 Trigger word: "{TRIGGER_WORD}"')


@client.event
async def on_message(message):
    # Skip bots and DMs
    if message.author.bot or message.guild is None:
        return

    # Only work in the specified channel
    if str(message.channel.id) != CHANNEL_ID:
        return

    # Check trigger word (exact match - safest for whitelist)
    if message.content.lower().strip() != TRIGGER_WORD:
        return

    # Get role safely
    try:
        role_id = int(WHITELIST_ROLE_ID)
        role = message.guild.get_role(role_id)
    except (TypeError, ValueError):
        print("❌ WL_ROLE_ID environment variable is not a valid number!")
        return

    if role is None:
        print(f"⚠️ Role with ID {WHITELIST_ROLE_ID} was not found in the server!")
        return

    # Add role if user doesn't have it already
    if role not in message.author.roles:
        try:
            await message.author.add_roles(role)
            print(f"✅ Added '{role.name}' role to {message.author} ({message.author.id})")
        except discord.Forbidden:
            print("❌ Cannot add role: Bot is below the role in hierarchy or missing 'Manage Roles' permission")
        except discord.HTTPException as e:
            print(f"❌ HTTP error while adding role: {e}")
        except Exception as e:
            print(f"❌ Unexpected error adding role: {e}")
    else:
        print(f"ℹ️  {message.author} already has the '{role.name}' role")

    # Add reaction to confirm
    try:
        await message.add_reaction("✅")
    except Exception as e:
        print(f"❌ Could not add ✅ reaction: {e}")


# ====================== START BOT ======================
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("❌ DISCORD_TOKEN environment variable is missing!")
    elif not CHANNEL_ID:
        print("❌ WL_CHANNEL_ID environment variable is missing!")
    elif not WHITELIST_ROLE_ID:
        print("❌ WL_ROLE_ID environment variable is missing!")
    else:
        print("🚀 Starting whitelist bot...")
        client.run(token)
