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
        self.db = await aiosqlite.connect('commands/ban/ban_database.db')

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

    async def add_monitored_role(self, guild_id: int, role_id: int):
        await self.db.execute(
            'INSERT OR IGNORE INTO monitored_roles (guild_id, role_id) VALUES (?, ?)',
            (guild_id, role_id)
        )
        await self.db.commit()

    async def remove_monitored_role(self, guild_id: int, role_id: int):
        await self.db.execute(
            'DELETE FROM monitored_roles WHERE guild_id = ? AND role_id = ?',
            (guild_id, role_id)
        )
        await self.db.commit()

    async def get_feedback_channel_id(self, guild_id: int):
        async with self.db.execute(
            'SELECT feedback_channel_id FROM guild_settings WHERE guild_id = ?',
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_feedback_channel_id(self, guild_id: int, channel_id: int):
        await self.db.execute(
            '''
            INSERT INTO guild_settings (guild_id, feedback_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET feedback_channel_id = excluded.feedback_channel_id
            ''',
            (guild_id, channel_id)
        )
        await self.db.commit()

    # ---------- ENFORCEMENT ----------

    async def ban_for_banned_image(self, message):
        reason = 'Uploaded banned image (100% hash match)'

        try:
            await message.guild.ban(
                message.author,
                reason=reason,
                delete_message_days=1
            )

            feedback_channel_id = await self.get_feedback_channel_id(message.guild.id)
            feedback_channel = None
            if feedback_channel_id:
                feedback_channel = message.guild.get_channel(feedback_channel_id)

            feedback_msg = (
                f'**User banned**: {message.author.mention}\n'
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
            await message.channel.send('Missing permission to ban user.')

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
                    await self.ban_for_banned_image(message)
                    return

                await self.store_phash(message, attachment.url, phash)

    # ---------- SLASH COMMAND ----------

    @app_commands.command(
        name='ban-image',
        description='Ban an image by URL (100% pHash match enforcement)'
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban_image(self, interaction, url: str):
        await interaction.response.defer(ephemeral=True)

        phash = await self.image_url_to_phash(url)
        await self.add_banned_image(phash)

        await interaction.followup.send(
            f'Image banned successfully.\n'
            f'pHash: `{phash}`',
            ephemeral=True
        )

    # ---------- ROLE MANAGEMENT ----------

    @app_commands.command(
        name='monitored-roles',
        description='Manage roles that the bot listens to for image banning'
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    @app_commands.choices(action=[
        app_commands.Choice(name='add', value='add'),
        app_commands.Choice(name='remove', value='remove'),
        app_commands.Choice(name='list', value='list')
    ])
    async def monitored_roles(self, interaction, action: str, role: discord.Role = None):
        await interaction.response.defer(ephemeral=True)

        if action == 'add':
            if not role:
                await interaction.followup.send('You must specify a role to add.', ephemeral=True)
                return
            await self.add_monitored_role(interaction.guild.id, role.id)
            await interaction.followup.send(f'Added {role.mention} to monitored roles.', ephemeral=True)

        elif action == 'remove':
            if not role:
                await interaction.followup.send('You must specify a role to remove.', ephemeral=True)
                return
            await self.remove_monitored_role(interaction.guild.id, role.id)
            await interaction.followup.send(f'Removed {role.mention} from monitored roles.', ephemeral=True)

        elif action == 'list':
            roles = await self.get_monitored_roles(interaction.guild.id)
            if not roles:
                await interaction.followup.send('No roles are currently monitored. The bot is currently ignoring all'
												' users (except admins).', ephemeral=True)
            else:
                role_mentions = [f'<@&{r_id}>' for r_id in roles]
                await interaction.followup.send(f'**Monitored Roles:**\n' + '\n'.join(role_mentions), ephemeral=True)

    # ---------- SETTINGS ----------

    @app_commands.command(
        name='set-feedback-channel',
        description='Set the channel where ban feedback messages are sent'
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def set_feedback_channel(self, interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        await self.set_feedback_channel_id(interaction.guild.id, channel.id)

        await interaction.followup.send(
            f'Feedback channel set to {channel.mention}.',
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ImageListener(bot))