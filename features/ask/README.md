# Ask Feature

The `ask` feature provides Sentry with the ability to answer user questions by processing text through a pre-trained machine learning model.

## Components

- `ask_command.py`: Defines the `/ask` command for manual queries.
- `ask_listener.py`: Listens to message events to provide automated responses when relevant.
- `model.pkl` & `vectorizer.pkl`: The serialized machine learning model and text vectorizer used for inference.

## How it works

The feature uses a vectorizer to transform input text into a numerical format that the model can process. Based on the training data, the model predicts the most appropriate response or category for the user's input.
