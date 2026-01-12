# Sentry Discord Bot

Sentry is a specialized Discord bot designed for server management and interactive utility features. It leverages machine learning for natural language interaction and provides robust moderation tools like automated muting.

## Project Structure

- `main.py`: The entry point of the bot.
- `config/`: Contains configuration files for the Discord client, intents, and API keys.
- `features/`: Contains the core functionality of the bot.
  - `ask/`: AI-powered interaction feature.
  - `mute/`: Advanced moderation and muting system.

## Setup

1.  **Clone the repository.**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    Ensure your Discord token and other necessary keys are set up in `config/keys.py`.
4.  **Run the bot**:
    ```bash
    python main.py
    ```

## Features

- **Ask**: A machine learning-based feature that allows the bot to respond to user queries using a trained model.
- **Mute**: A comprehensive muting system with database persistence to handle user mutes across sessions.
