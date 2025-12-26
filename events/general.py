"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from config import client
from commands.mute.mute_command import ImageListener
from commands.general import GeneralCommands

# GENERAL EVENTS
@client.sentry.event
async def on_ready():
    assert client.sentry.user is not None

    print(f'Logged in as {client.sentry.user} (ID: {client.sentry.user.id})')
    print("""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@%+%@@@@@@@@@@@@@@@@@@@@@@@@@%+%@@@
@@@@%-..=#@@@@@@@@@@@@@@@@@#=..-%@@@@
@@@@@*:=+=..:#@@@@@@@@@%:..=+=:*@@@@@
@@@@@@*+*+:.+.#@@@@@@@%.=.:+*+*@@@@@@
@@@@@@@%**+=*.=.-+*+-.=.*=+*#%@@@@@@@
@@@@@@@@@#**-:=:-...-:=:-**#@@@@@@@@@
@@@@@@@@@@@%@*%-.:.:.-%*%%@@@@@@@@@@@
@@@@@@@@@@@@@@@@@*-*@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    """)

    if not client.sentry.get_cog("GeneralCommands"):
        print("Adding GeneralCommands cog...")
        await client.sentry.add_cog(GeneralCommands(client.sentry))
        print("GeneralCommands cog added.")

    if not client.sentry.get_cog("ImageListener"):
        print("Adding ImageListener cog...")
        await client.sentry.add_cog(ImageListener(client.sentry))
        print("ImageListener cog added.")
    else:
        print("ImageListener cog already loaded.")

    try:
        synced = await client.sentry.tree.sync()
        print(f"Synced {len(synced)} global command(s): {', '.join([cmd.name for cmd in synced])}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
