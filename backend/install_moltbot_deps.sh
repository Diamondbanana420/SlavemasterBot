#!/bin/bash
# Moltbot Dependencies Installation Script
# This script ensures Node.js 22+ and Moltbot (clawdbot) are installed

set -e

LOGFILE="/tmp/moltbot_deps.log"
LOCKFILE="/tmp/moltbot_deps.lock"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
}

# Check if already running
if [ -f "$LOCKFILE" ]; then
    log "Another installation is already in progress"
    exit 0
fi

trap "rm -f $LOCKFILE" EXIT
touch "$LOCKFILE"

log "Starting Moltbot dependencies check..."

# Check Node.js version
NODE_VERSION=$(node -v 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1 || echo "0")
log "Current Node.js version: $NODE_VERSION"

if [ "$NODE_VERSION" -lt 22 ]; then
    log "Node.js 22+ required. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >> "$LOGFILE" 2>&1
    apt-get install -y nodejs >> "$LOGFILE" 2>&1
    log "Node.js installed: $(node -v)"
else
    log "Node.js 22+ already installed"
fi

# Check if clawdbot is installed
if ! command -v clawdbot &> /dev/null; then
    log "Clawdbot not found. Installing..."
    curl -fsSL https://molt.bot/install.sh | bash >> "$LOGFILE" 2>&1 || true
    
    # Verify installation
    if command -v clawdbot &> /dev/null; then
        log "Clawdbot installed: $(clawdbot --version)"
    else
        log "ERROR: Failed to install clawdbot"
        exit 1
    fi
else
    log "Clawdbot already installed: $(clawdbot --version)"
fi

log "Moltbot dependencies check complete!"
