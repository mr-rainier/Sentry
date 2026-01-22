# Mute Feature (Image Enforcement System)

The `mute` feature is an advanced automated moderation system designed to detect and penalize the distribution of banned images (e.g., scam graphics, prohibited content) using perceptual hashing (pHash).

## Overview

Unlike traditional text-based moderation, this system focuses on visual content. It calculates a unique hash for every image uploaded by monitored users and compares it against a database of prohibited hashes.

## Key Components

- `mute_command.py`: Provides the `/mute-image` slash command for administrators to register new prohibited images into the database.
- `mute_listener.py`: Monitors message events, extracts image attachments, calculates pHash in a separate thread pool to ensure performance, and triggers enforcement actions upon a match.
- `mute_database.py`: Manages the SQLite database containing image hashes, banned hashes, monitored roles, and guild-specific settings.
- `mute_utils.py`: Contains core utility functions for image processing, hash calculation, and enforcement logic (timeouts and message cleanup).
- `general.py`: Handles administrative configuration commands like `/monitored-roles` and `/set-feedback-channel`.

## Functionality

### 1. Image Perceptual Hashing (pHash)
The system uses the `imagehash` library to generate hashes that are resistant to minor modifications (like resizing or slight color shifts), ensuring that slight variations of a banned image are still detected.

### 2. Automated Enforcement
When a banned image is detected:
- The user is automatically placed in a **1-week timeout**.
- The offending message is deleted.
- Up to 10 previous messages from the same user in that channel are purged to prevent further spam.
- A notification is sent to the configured feedback channel or the current channel.

### 3. Role-Based Monitoring
Administrators can specify which roles should be monitored using the `/monitored-roles` command. This allows the bot to focus on high-risk roles (e.g., new members) while ignoring trusted users or administrators.

### 4. Feedback System
Configurable feedback channels allow moderators to track automated actions in a centralized location via the `/set-feedback-channel` command.

## Setup & Configuration

1. **Set Monitored Roles**: Use `/monitored-roles add <role>` to start tracking users with specific roles.
2. **Configure Feedback**: Use `/set-feedback-channel <channel>` to receive logs of automated mutes.
3. **Ban Images**: Use `/mute-image <url>` to add an image's hash to the blacklist.
