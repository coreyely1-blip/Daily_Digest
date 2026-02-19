#!/usr/bin/env bash
# setup_cron.sh - Set up the daily digest cron job for 7:00 AM ET
#
# Prerequisites:
#   1. Python 3.8+ installed
#   2. pip install -r requirements.txt
#   3. Copy .env.example to .env and fill in your Gmail App Password:
#        cp .env.example .env
#        # Edit .env with your credentials
#   4. Test the setup:
#        python daily_digest.py --test     (sends a test email)
#        python daily_digest.py --dry-run  (previews without sending)
#   5. Run this script:
#        chmod +x setup_cron.sh
#        ./setup_cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(which python3 || which python)"

if [ -z "$PYTHON" ]; then
    echo "Error: Python 3 not found. Please install Python 3.8+."
    exit 1
fi

echo "Using Python: $PYTHON"
echo "Project directory: $SCRIPT_DIR"

# Check that .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ""
    echo "Error: .env file not found."
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your Gmail App Password."
    exit 1
fi

# Build the cron command
# 7:00 AM ET - uses the system timezone; adjust the cron time if your server
# is in a different timezone. For UTC servers, 7 AM ET = 12:00 PM UTC (EST)
# or 11:00 AM UTC (EDT). Using a wrapper that handles timezone.
CRON_CMD="0 7 * * * cd $SCRIPT_DIR && $PYTHON daily_digest.py >> $SCRIPT_DIR/logs/digest.log 2>&1"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Check if cron job already exists
EXISTING=$(crontab -l 2>/dev/null | grep -F "daily_digest.py" || true)

if [ -n "$EXISTING" ]; then
    echo "A daily digest cron job already exists:"
    echo "  $EXISTING"
    read -p "Replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
    # Remove existing entry
    crontab -l 2>/dev/null | grep -v -F "daily_digest.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo ""
echo "Cron job installed successfully!"
echo "Schedule: Every day at 7:00 AM (server local time)"
echo "Command:  $CRON_CMD"
echo ""
echo "To verify: crontab -l"
echo "To remove: crontab -l | grep -v daily_digest | crontab -"
echo "Logs at:   $SCRIPT_DIR/logs/digest.log"
echo ""
echo "NOTE: The cron time (7:00 AM) uses your server's local timezone."
echo "If your server is in UTC, edit the cron entry to adjust:"
echo "  - 7 AM ET (EST) = 12 PM UTC  -> change '0 7' to '0 12'"
echo "  - 7 AM ET (EDT) = 11 AM UTC  -> change '0 7' to '0 11'"
