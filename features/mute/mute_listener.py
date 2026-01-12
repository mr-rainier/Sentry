"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
from discord.ext import commands
from features.mute.mute_database import MuteDatabase
from features.mute import mute_utils

class MuteListener(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._db_manager = MuteDatabase()

	@property
	def db(self):
		return self._db_manager.db

	async def get_feedback_channel_id(self, guild_id):
		async with self.db.execute('SELECT feedback_channel_id FROM guild_settings WHERE guild_id = ?', (guild_id,)) as cursor:
			row = await cursor.fetchone()
			return row[0] if row else None

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot or not message.guild or message.author.guild_permissions.administrator:
			return

		async with self.db.execute('SELECT role_id FROM monitored_roles WHERE guild_id = ?', (message.guild.id,)) as cursor:
			monitored_roles = [row[0] for row in await cursor.fetchall()]

		if not monitored_roles or not any(role.id in monitored_roles for role in message.author.roles):
			return

		for attachment in message.attachments:
			if attachment.content_type and attachment.content_type.startswith('image/'):
				phash = await mute_utils.image_url_to_phash(attachment.url)

				async with self.db.execute('SELECT 1 FROM banned_images WHERE phash = ?', (phash,)) as cursor:
					if await cursor.fetchone():
						await mute_utils.mute_user_for_banned_image(message, self.db, self.get_feedback_channel_id)
						return

				await self.db.execute('INSERT INTO image_hashes (message_id, user_id, channel_id, image_url, phash) VALUES (?, ?, ?, ?, ?)',
									  (message.id, message.author.id, message.channel.id, attachment.url, phash))
				await self.db.commit()

async def setup(bot):
	await bot.add_cog(MuteListener(bot))