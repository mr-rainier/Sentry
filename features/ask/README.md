# Notebook

You can read and access the Deepnote notebook [here](https://deepnote.com/workspace/o-a1bdefa1-d337-4560-aacf-742a0c4f0a4d/project/SandT-SandR-Ask-to-Ask-ML-Model-e4180d97-3f6a-4174-a0f9-3d511a6d6deb/notebook/1-Preliminary-Training-6d638408bb9d4dffb315823266e14a19)

Model is trained almost entirely on the S&T and S&R server's data, with the exception of synthetically generated datasets for finetuning.

# Ask Feature (Anti-"Ask to Ask" System)

The `ask` feature is an intelligent utility designed to improve communication efficiency within the server by discouraging "asking to ask."

## Overview

Many users often post messages like "Can I ask a question?" or "Anyone here an expert in X?". Sentry uses a Machine Learning model to detect these types of meta-questions and automatically reminds the user to post their question directly.

## Key Components

- `ask_listener.py`: The core engine that monitors messages, runs them through the ML model, and sends reminders when meta-questions are detected.
- `ask_command.py`: Provides administrative controls, such as `/ask-toggle` to enable or disable the listener.
- `transformers.py`: Contains `CustomFeatureExtractor`, which prepares message text for the model by extracting relevant linguistic features.
- `model.pkl` & `vectorizer.pkl`: The pre-trained model and feature vectorizer used to classify messages.

## How It Works

1. **Detection**: The bot listens to messages between 4 and 90 characters.
2. **Analysis**: It uses a trained model to calculate the probability that a message is an "ask to ask" meta-question.
3. **Action**: If the confidence score is above 95%, the bot replies with a friendly reminder to ask the question directly.
4. **Feedback Loop**: Authorized supervisors can react to the bot's response with ❤️ (True Positive) or 👎 (False Positive) to help refine future training data.

## Commands

- `/ask-toggle`: (Administrator only) Toggle the automatic detection listener on or off.
