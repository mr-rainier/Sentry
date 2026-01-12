"""
Sentry - December 17, 2025
Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
automatically remove threats to your community's safety.
"""

# IMPORTS
import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None

    async def cog_load(self):
        self.db = await aiosqlite.connect('features/mute/mute_database.db')

    async def cog_unload(self):
        await self.db.close()

    # ---------- DATABASE HELPER METHODS ----------

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

    # ---------- SLASH COMMANDS ----------

    @app_commands.command(
        name='monitored-roles',
        description='Manage roles that the bot listens to for image matching'
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

    @app_commands.command(
        name='set-feedback-channel',
        description='Set the channel where enforcement feedback messages are sent'
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
    await bot.add_cog(GeneralCommands(bot))