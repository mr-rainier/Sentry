# Mute Feature

The `mute` feature is a robust moderation tool designed to temporarily or permanently restrict users from speaking in the server.

## Components

- `mute_command.py`: The command interface for moderators to mute/unmute users.
- `mute_listener.py`: Handles event-based logic, such as ensuring a muted user remains muted if they rejoin the server.
- `mute_database.py` & `mute_database.db`: Manages persistent storage of mute records using SQLite.
- `mute_utils.py`: Helper functions for calculating mute durations and managing role assignments.
- `general.py`: General configuration and logic shared within the mute module.

## Functionality

- **Persistence**: Mutes are stored in a local database, allowing the bot to remember active mutes even after a restart.
- **Automated Management**: The listener tracks member updates to prevent users from bypassing mutes by leaving and re-entering the server.
