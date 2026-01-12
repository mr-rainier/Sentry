"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from config import client, keys, cogs
import os

# MAIN
if __name__ == "__main__":
	client.sentry.run(os.getenv('DISCORD_TOKEN'))