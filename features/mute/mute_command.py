"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from discord.ext import commands
from discord import app_commands
from features.mute.mute_database import MuteDatabase
from features.mute import mute_utils

# COMMAND
class MuteFeature(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._db_manager = MuteDatabase()

	@property
	def db(self):
		return self._db_manager.db

	@app_commands.command(name='mute-image')
	@app_commands.checks.has_permissions(ban_members=True)
	async def ban_image(self, interaction, url: str):
		await interaction.response.defer(ephemeral=True)
		phash = await mute_utils.image_url_to_phash(url)

		await self.db.execute('INSERT OR IGNORE INTO banned_images (phash) VALUES (?)', (phash,))
		await self.db.commit()

		await interaction.followup.send(f'Image registered.\npHash: `{phash}`', ephemeral=True)

async def setup(bot):
	await bot.add_cog(MuteFeature(bot))