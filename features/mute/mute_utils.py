"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
import discord
from discord import Forbidden
import datetime
from PIL import Image
import imagehash
from io import BytesIO
import aiohttp

# Shared session for all modules
_session = None

def get_session():
	global _session
	if _session is None:
		_session = aiohttp.ClientSession()
	return _session

async def image_url_to_phash(url: str) -> str:
	session = get_session()
	async with session.get(url) as resp:
		data = await resp.read()
	image = Image.open(BytesIO(data))
	return str(imagehash.phash(image))

def sync_image_url_to_phash(url: str) -> str:
	import urllib.request
	with urllib.request.urlopen(url) as resp:
		data = resp.read()
	image = Image.open(BytesIO(data))
	return str(imagehash.phash(image))

async def mute_user_for_banned_image(message, db, get_feedback_channel_func):
	reason = 'Uploaded banned image (100% hash match)'

	try:
		await message.author.timeout(
			discord.utils.utcnow() + datetime.timedelta(weeks=1),
			reason=reason
		)

		muted_message_author = message.author

		async for message_history in message.channel.history(limit=10, before=message):
			if message_history.author.id == muted_message_author.id:
				await message_history.delete()
			else:
				break

		await message.delete()

		feedback_channel_id = await get_feedback_channel_func(message.guild.id)
		feedback_channel = message.guild.get_channel(feedback_channel_id) if feedback_channel_id else None

		feedback_msg = (
			f'**User muted**: {message.author.mention}\n'
			f'Reason: banned image detected (100% match)'
		)

		if feedback_channel:
			try:
				await feedback_channel.send(feedback_msg)
			except Forbidden:
				await message.channel.send(f'Could not send feedback to configured channel {feedback_channel.mention}. ' + feedback_msg)
		else:
			await message.channel.send(feedback_msg)

	except Forbidden:
		feedback_channel_id = await get_feedback_channel_func(message.guild.id)
		feedback_channel = message.guild.get_channel(feedback_channel_id) if feedback_channel_id else None

		msg = (
			f'**Action failed**\n'
			f'User: {message.author.mention}\n'
			f'Reason: Bot lacks permission or role hierarchy is insufficient.'
		)

		if feedback_channel:
			await feedback_channel.send(msg)
		else:
			await message.channel.send(msg)