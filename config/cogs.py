"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from config import client
from features.ask.ask_command import AskFeature
from features.mute.general import GeneralCommands
from features.mute.mute_command import MuteFeature
from features.mute.mute_database import MuteStorage
from features.mute.mute_listener import MuteListener
from features.ask.ask_listener import AskListener

# LOAD COGS
@client.sentry.event
async def on_ready():
    assert client.sentry.user is not None

    print(f'Logged in as {client.sentry.user} (ID: {client.sentry.user.id})')

    if not client.sentry.get_cog("GeneralCommands"):
        print("Adding GeneralCommands cog...")
        await client.sentry.add_cog(GeneralCommands(client.sentry))
        print("GeneralCommands cog added.")

    if not client.sentry.get_cog("MuteStorage"):
        print("Adding MuteDatabase cog...")
        await client.sentry.add_cog(MuteStorage(client.sentry))
        print("MuteDatabase cog added.")
    else:
        print("MuteDatabase cog already loaded.")

    if not client.sentry.get_cog("MuteFeature"):
        print("Adding MuteFeature cog...")
        await client.sentry.add_cog(MuteFeature(client.sentry))
        print("MuteFeature cog added.")
    else:
        print("MuteFeature cog already loaded.")

    if not client.sentry.get_cog("MuteListener"):
        print("Adding MuteListener cog...")
        await client.sentry.add_cog(MuteListener(client.sentry))
        print("MuteListener cog added.")
    else:
        print("MuteListener cog already loaded.")

    if not client.sentry.get_cog("AskFeature"):
        print("Adding AskFeature cog...")
        await client.sentry.add_cog(AskFeature(client.sentry))
        print("AskFeature cog added.")

    if not client.sentry.get_cog("AskListener"):
        print("Adding AskListener cog...")
        await client.sentry.add_cog(AskListener(client.sentry))
        print("AskListener cog added.")

    try:
        synced = await client.sentry.tree.sync()
        print(f"Synced {len(synced)} global command(s): {', '.join([cmd.name for cmd in synced])}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
