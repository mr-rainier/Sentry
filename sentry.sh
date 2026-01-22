#!/bin/bash


# Sentry - January 21, 2025
# Sentry is an anti-spam and anti-scam bot that detects coordinated, script-enabled malicious activity to
# automatically remove threats to your community's safety.

# HELP
show_help() {
    echo "Usage: ./sentry.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup    Initialize virtual environment, install requirements, and start bot"
    echo "  start    Start the bot using PM2"
    echo "  stop     Stop the bot using PM2"
    echo "  restart  Restart the bot"
    echo "  logs     Show real-time bot logs"
}

# SETUP
setup_bot() {
    echo "--- Starting Sentry Setup ---"
    
    # Update system packages
    sudo apt-get update && sudo apt-get install -y python3-venv python3-pip nodejs npm

    # Install PM2 globally if not present
    if ! command -v pm2 &> /dev/null; then
        echo "Installing PM2..."
        sudo npm install pm2 -g
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Install/Update requirements
    echo "Installing requirements..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    # Start with PM2
    start_bot
}

# START
start_bot() {
    echo "Starting Sentry Bot with PM2..."
    pm2 start main.py --name "sentry-bot" --interpreter ./venv/bin/python3
    pm2 save
}

# LOGIC
case "$1" in
    setup)
        setup_bot
        ;;
    start)
        start_bot
        ;;
    stop)
        pm2 stop sentry-bot
        ;;
    restart)
        pm2 restart sentry-bot
        ;;
    logs)
        pm2 logs sentry-bot
        ;;
    *)
        show_help
        ;;
esac