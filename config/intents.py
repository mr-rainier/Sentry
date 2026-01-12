"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
import discord
from discord.ext import commands

# INTENT VALUES
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.bans = True
intents.guild_typing = True
intents.guild_messages = True
intents.moderation = True
intents.guild_typing = True
intents.reactions = True