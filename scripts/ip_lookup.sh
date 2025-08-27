#!/bin/bash
# Ghost OSINT - IP Lookup (Public & Private Modes)

IP=$1
MODE=$2   # passed from Python (public/private)

if [ -z "$IP" ]; then
    echo "Usage: $0 <IP> [public|private]"
    exit 1
fi

# Default to public if no mode is given
if [ -z "$MODE" ]; then
    MODE="public"
fi

echo "[*] Looking up geolocation for: $IP"

RESPONSE=$(curl -s "http://ip-api.com/json/$IP")

if [ -z "$RESPONSE" ]; then
    echo "[!] Failed to fetch data."
    exit 1
fi

# Output formatting
if command -v jq >/dev/null 2>&1; then
    if [ "$MODE" == "public" ]; then
        echo "$RESPONSE" | jq '{country, regionName, city}'
    elif [ "$MODE" == "private" ]; then
        echo "$RESPONSE" | jq '{country, regionName, city, isp, org, query, timezone, lat, lon}'
    else
        echo "[!] Unknown mode. Use: public | private"
    fi
else
    echo "$RESPONSE"
fi

echo "[*] Done."
