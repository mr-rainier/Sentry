"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
# noinspection PyUnusedImports
from config import client
import discord
from discord.ext import commands
from discord import app_commands, Forbidden
import aiohttp
import datetime
from PIL import Image
import imagehash
import aiosqlite
from io import BytesIO

class ImageListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.db = None

    # ---------- LIFECYCLE ----------

    async def cog_load(self):
        self.db = await aiosqlite.connect('commands/mute/mute_database.db')

        await self.db.execute('''
                              CREATE TABLE IF NOT EXISTS image_hashes (
                                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                          message_id INTEGER,
                                                                          user_id INTEGER,
                                                                          channel_id INTEGER,
                                                                          image_url TEXT,
                                                                          phash TEXT,
                                                                          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                              )
                              ''')

        await self.db.execute('''
                              CREATE TABLE IF NOT EXISTS banned_images (
                                                                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                           phash TEXT NOT NULL UNIQUE
                              )
                              ''')

        await self.db.execute('''
                              CREATE TABLE IF NOT EXISTS monitored_roles (
                                                                              guild_id INTEGER,
                                                                              role_id INTEGER,
                                                                              PRIMARY KEY (guild_id, role_id)
                              )
                              ''')

        await self.db.execute('''
                              CREATE TABLE IF NOT EXISTS guild_settings (
                                                                            guild_id INTEGER PRIMARY KEY,
                                                                            feedback_channel_id INTEGER
                              )
                              ''')

        await self.db.execute('CREATE INDEX IF NOT EXISTS idx_phash ON image_hashes(phash)')
        await self.db.execute('CREATE INDEX IF NOT EXISTS idx_banned_phash ON banned_images(phash)')
        await self.db.commit()

    async def cog_unload(self):
        await self.session.close()
        await self.db.close()

    # ---------- IMAGE HASHING ----------

    async def image_url_to_phash(self, url: str) -> str:
        async with self.session.get(url) as resp:
            data = await resp.read()

        image = Image.open(BytesIO(data))
        return str(imagehash.phash(image))

    # ---------- DATABASE ----------

    async def store_phash(self, message, image_url, phash):
        await self.db.execute(
            '''
            INSERT INTO image_hashes (
                message_id, user_id, channel_id, image_url, phash
            ) VALUES (?, ?, ?, ?, ?)
            ''',
            (
                message.id,
                message.author.id,
                message.channel.id,
                image_url,
                phash,
            ),
        )
        await self.db.commit()

    async def is_banned_image(self, phash: str) -> bool:
        async with self.db.execute(
                'SELECT 1 FROM banned_images WHERE phash = ?',
                (phash,)
        ) as cursor:
            return await cursor.fetchone() is not None

    async def add_banned_image(self, phash: str):
        await self.db.execute(
            'INSERT OR IGNORE INTO banned_images (phash) VALUES (?)',
            (phash,)
        )
        await self.db.commit()

    async def get_monitored_roles(self, guild_id: int):
        async with self.db.execute('SELECT role_id FROM monitored_roles WHERE guild_id = ?', (guild_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_feedback_channel_id(self, guild_id: int):
        async with self.db.execute(
            'SELECT feedback_channel_id FROM guild_settings WHERE guild_id = ?',
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    # ---------- ENFORCEMENT ----------

    async def mute_for_banned_image(self, message):
        reason = 'Uploaded banned image (100% hash match)'

        try:
            # Mute (timeout) for 1 week
            await message.author.timeout(
                discord.utils.utcnow() + datetime.timedelta(weeks=1),
                reason=reason
            )

            # Get muted message author
            muted_message_author = message.author

            # Delete adjacent messages from the same user
            async for message_history in message.channel.history(limit=10, before=message):
                if message_history.author.id == muted_message_author.id:
                    await message_history.delete()
                else:
                    break

            # Delete the offending message
            await message.delete()

            feedback_channel_id = await self.get_feedback_channel_id(message.guild.id)
            feedback_channel = None
            if feedback_channel_id:
                feedback_channel = message.guild.get_channel(feedback_channel_id)

            feedback_msg = (
                f'**User muted**: {message.author.mention}\n'
                f'Reason: banned image detected (100% match)'
            )

            if feedback_channel:
                try:
                    await feedback_channel.send(feedback_msg)
                except Forbidden:
                    await message.channel.send(f'Could not send feedback to configured'
                                               f' channel {feedback_channel.mention}. ' + feedback_msg)
            else:
                await message.channel.send(feedback_msg)

        except Forbidden:
            feedback_channel_id = await self.get_feedback_channel_id(message.guild.id)
            feedback_channel = (
                message.guild.get_channel(feedback_channel_id)
                if feedback_channel_id else None
            )

            msg = (
                f'**Action failed**\n'
                f'User: {message.author.mention}\n'
                f'Reason: Bot lacks permission or role hierarchy is insufficient.'
            )

            if feedback_channel:
                await feedback_channel.send(msg)
            else:
                await message.channel.send(msg)


    # ---------- BACKGROUND LISTENER ----------

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
                message.author.bot
                or not message.guild
                or message.author.guild_permissions.administrator
        ):
            return

        monitored_roles = await self.get_monitored_roles(message.guild.id)
        if not monitored_roles:
            return

        user_roles = [role.id for role in message.author.roles]
        if not any(role_id in monitored_roles for role_id in user_roles):
            return

        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                phash = await self.image_url_to_phash(attachment.url)

                if await self.is_banned_image(phash):
                    await self.mute_for_banned_image(message)
                    return

                await self.store_phash(message, attachment.url, phash)

    # ---------- SLASH COMMAND ----------

    @app_commands.command(
        name='mute-image',
        description='Register an image to trigger enforcement (100% pHash match)'
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban_image(self, interaction, url: str):
        await interaction.response.defer(ephemeral=True)

        phash = await self.image_url_to_phash(url)
        await self.add_banned_image(phash)

        await interaction.followup.send(
            f'Image registered successfully.\n'
            f'pHash: `{phash}`',
            ephemeral=True
        )

    @app_commands.command(name='test-timeout')
    async def test_timeout(self, interaction, member: discord.Member):
        await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=1))
        await interaction.response.send_message("Done")

async def setup(bot):
    await bot.add_cog(ImageListener(bot))