"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from discord.ext import commands
from config.intents import intents

# PROFILE
name = 'Sentry'
description = ('Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity '
			   'to automatically remove threats to your community\'s safety.')

# CLIENT
sentry = commands.Bot(command_prefix='/', description=description, intents=intents)