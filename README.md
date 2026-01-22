# Sentry - Advanced Discord Moderation & AI Bot

Sentry is a high-performance Discord bot designed to protect communities from coordinated malicious activity, scams, and spam. It combines traditional moderation tools with machine learning and perceptual hashing to provide a comprehensive security layer for your server.

# Key Features

### Automated Image Enforcement (Mute Feature)
Sentry uses **Perceptual Hashing (pHash)** to detect and block prohibited images, even if they have been slightly modified.
- **Instant Timeout**: Automatically mutes users posting blacklisted content.
- **Proactive Cleanup**: Deletes offending images and recent message history from the offender.
- **Role-Based Monitoring**: Targets specific high-risk roles for content inspection.
- **Persistent Database**: Stores banned hashes and configuration in a local SQLite database.

### Anti-"Ask to Ask" Intelligence (Ask Feature)
Leverages a **Machine Learning model** (XGBoost) to improve communication flow by discouraging meta-questions.
- **Intent Detection**: Automatically identifies when users "ask to ask" instead of posting their question directly.
- **Real-time Reminders**: Provides friendly automated nudges to encourage efficient communication.
- **Human-in-the-Loop**: Supervisors can provide feedback on bot predictions via reactions to improve accuracy.

## Project Structure

```
Sentry/
├── config/             # Bot configuration (Intents, Keys, Client)
├── features/
│   ├── ask/            # AI-powered Q&A module
│   └── mute/           # Image enforcement & moderation module
├── main.py             # Main entry point
├── requirements.txt    # Project dependencies
└── sentry.sh           # Deployment/startup script
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Node.js & NPM (for PM2 process management)

### 1. Clone & Install
```bash
git clone https://github.com/your-repo/sentry.git
cd sentry
pip install -r requirements.txt
```

### 2. Configuration
Create/Update `config/keys.py` with your bot credentials:
```python
DISCORD_TOKEN = 'your-token-here'
```

### 3. Running the Bot
You can use the provided management script for easy deployment:
```bash
chmod +x sentry.sh
./sentry.sh setup    # Initial setup and start
./sentry.sh logs     # View real-time logs
```

## Documentation

- [Mute Feature Documentation](features/mute/README.md)
- [Ask Feature Documentation](features/ask/README.md)

## Community & Safety
Sentry is built with a focus on anti-spam and anti-scam. It is designed to be lightweight, efficient, and easy to deploy for server administrators who need automated protection against visual-based scams.
