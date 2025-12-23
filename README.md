# Sentry

Sentry is an anti-spam and anti-scam Discord bot that detects coordinated, script-enabled malicious activity to automatically remove threats to your community's safety. It specifically focuses on image-based threats using perceptual hashing (pHash) to identify and ban malicious content.

## Features

- **Perceptual Image Hashing (pHash):** Detects visually similar images even if they have minor modifications.
- **Automated Banning:** Automatically bans users who post images that match a global database of banned images.
- **Role-Based Monitoring:** Configure specific roles that the bot should monitor (e.g., new members).
- **Feedback Channel:** Dedicated channel for receiving notifications when a user is banned.
- **Slash Commands:** Modern and easy-to-use interface for management.

## Prerequisites

- Python 3.8+
- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- [Pillow](https://python-pillow.org/)
- [ImageHash](https://github.com/JohannesBuchner/imagehash)
- [aiosqlite](https://github.com/omnilib/aiosqlite)
- [aiohttp](https://docs.aiohttp.org/en/stable/)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Sentry.git
   cd Sentry
   ```

2. **Install dependencies:**
   ```bash
   pip install discord.py Pillow ImageHash aiosqlite aiohttp
   ```

3. **Configure Environment Variables:**
   Update `config/keys.py` with your bot's credentials:
   ```python
   os.environ['DISCORD_DEVELOPER_ID'] = 'YOUR_DISCORD_ID'
   os.environ['DISCORD_BOT_ID'] = 'YOUR_DISCORD_BOTS_ID'
   os.environ['DISCORD_TOKEN'] = 'YOUR_DISCORD_BOTS_TOKEN'
   os.environ['DISCORD_SECRET'] = 'YOUR_DISCORD_BOTS_SECRET'
   ```
   *Note: It is recommended to use a `.env` file or actual environment variables in a production environment.*

## Usage

Run the bot using:
```bash
python main.py
```

### Slash Commands

- `/ban-image <url>`: Add an image to the global banned database using its URL. (Requires `Ban Members` permission)
- `/monitored-roles <action> [role]`: Manage roles that the bot listens to. (Requires `Administrator` permission)
    - `action`: `add`, `remove`, or `list`.
- `/set-feedback-channel <channel>`: Set the channel where the bot sends ban notifications. (Requires `Administrator` permission)

## Project Structure

```text
.
├── main.py                  # Entry point of the bot
├── commands/
│   ├── ban/
│   │   ├── ban_command.py   # Core logic for image banning and monitoring
│   │   └── ban_database.db  # SQLite database for hashes and settings
│   └── general.py           # General purpose commands
├── config/
│   ├── client.py            # Bot client initialization
│   ├── intents.py           # Discord intents configuration
│   ├── keys.py              # API keys and environment variables
│   └── profile.py           # Bot profile and description
├── events/
│   └── general.py           # Event handlers (on_ready, etc.)
└── README.md                # Project documentation
```

## How it works

Sentry uses **Perceptual Hashing** via the `imagehash` library. Unlike traditional hashes (like MD5), a perceptual hash changes only slightly if the image is slightly altered (resized, compressed, etc.). This allows Sentry to catch "scam images" that might have been slightly modified to bypass simple detection.

When a user with a **monitored role** sends an image:
1. Sentry calculates the pHash of the image.
2. It checks the pHash against its database of `banned_images`.
3. If a match is found, the user is immediately banned from the server, and a notification is sent to the feedback channel.

---
*Created on December 23, 2025*
