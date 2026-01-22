"""
Sentry - January 11, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from discord import app_commands
from discord.ext import commands

class AskFeature(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	ask_listener_on: bool = True

	@app_commands.command(name='ask-toggle')
	@app_commands.checks.has_permissions(administrator=True)
	async def ask_toggle(self, interaction):
		self.ask_listener_on = not self.ask_listener_on
		await interaction.response.send_message(f'Ask listener is now {self.ask_listener_on}')