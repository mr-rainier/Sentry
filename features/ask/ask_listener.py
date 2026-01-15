"""
Sentry - January 11, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
import joblib
import xgboost
import sklearn
from discord.ext import commands
from features.ask.ask_command import AskFeature

# LOAD MODEL
model = joblib.load('features/ask/model.pkl')
vectorizer = joblib.load('features/ask/vectorizer.pkl')

# SUPERVISORS
SUPERVISORS = {
	395419912845393923, # Thomas
	228331610444005377, # Kiftz
	496918293509308419 # Ry
}

# LISTENER
class AskListener(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.message_map = {}

	def _predict(self, content):
		# VECTORIZE
		message_vec = vectorizer.transform([content])
		prediction = model.predict(message_vec)[0]
		probability = model.predict_proba(message_vec)[0][1]
		return prediction, probability

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return

		if AskFeature.ask_listener_on:
			if len(message.content) > 0:
				channel = self.bot.get_channel(1129475112744275988)
				# channel = message.channel # Uncomment when ready to deploy in any channel

				# Run CPU-bound prediction in a thread pool to avoid blocking the event loop
				prediction, probability = await self.bot.loop.run_in_executor(None, self._predict, message.content)

				if probability > 0.90:
					bot_message = await channel.send(f'{message.author.mention}. Please ask your question directly, there\'s no '
													 f'need to ask to ask! :) {prediction}, {probability:.2f}')
					# Store the mapping
					self.message_map[bot_message.id] = message.content
					return
				elif probability > 0.10:
					bot_message = await channel.send(f'{prediction}, {probability:.2f}')
					# Store the mapping
					self.message_map[bot_message.id] = message.content
					return
				else:
					return
		else:
			return

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if user.bot:
			return

		if user.id not in SUPERVISORS:
			return

		if reaction.message.id not in self.message_map:
			return

		original_message = self.message_map[reaction.message.id]

		if str(reaction.emoji) == '❤️':
			target_user = await self.bot.fetch_user(496918293509308419)
			await target_user.send(f'{original_message} "TRUE"') # TODO: replace with a database logging system

		elif str(reaction.emoji) == '👎':
			target_user = await self.bot.fetch_user(496918293509308419)
			await target_user.send(f'{original_message} "FALSE"') # TODO: replace with a database logging system