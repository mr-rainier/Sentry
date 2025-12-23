"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
import os
from config import client
from config import keys
from events import general

# MAIN
client.sentry.run(os.getenv('DISCORD_TOKEN'))
