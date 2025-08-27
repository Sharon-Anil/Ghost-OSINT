#!/bin/bash

# ===============================
# Ghost OSINT - Phone Lookup Tool
# ===============================
# Usage: ./phone_lookup.sh +919876543210
# ===============================

PHONE=$1
API_KEY="YOUR_NUMVERIFY_API_KEY"  # 🔑 Replace with https://numverify.com key

if [ -z "$PHONE" ]; then
    echo "Usage: $0 <phone_number>"
    exit 1
fi

echo "[*] Searching for phone number: $PHONE"
echo "--------------------------------------"

# 1. Numverify API - Carrier, Location, Line Type
if [ "$API_KEY" != "YOUR_NUMVERIFY_API_KEY" ]; then
    echo "[*] Querying Numverify API..."
    RESPONSE=$(curl -s "http://apilayer.net/api/validate?access_key=$API_KEY&number=$PHONE")

    VALID=$(echo $RESPONSE | jq -r '.valid')
    COUNTRY=$(echo $RESPONSE | jq -r '.country_name')
    LOCATION=$(echo $RESPONSE | jq -r '.location')
    CARRIER=$(echo $RESPONSE | jq -r '.carrier')
    LINETYPE=$(echo $RESPONSE | jq -r '.line_type')

    if [ "$VALID" == "true" ]; then
        echo "[+] Number is VALID"
        echo "[+] Country : $COUNTRY"
        echo "[+] Location: $LOCATION"
        echo "[+] Carrier : $CARRIER"
        echo "[+] LineType: $LINETYPE"
    else
        echo "[-] Invalid phone number"
    fi
else
    echo "[!] Numverify API key not set. Skipping carrier/location lookup."
fi

echo "--------------------------------------"

# 2. Google & Social Media Dorks
echo "[*] Opening Google & social media lookups..."
xdg-open "https://www.google.com/search?q=$PHONE" >/dev/null 2>&1
xdg-open "https://www.facebook.com/search/top/?q=$PHONE" >/dev/null 2>&1
xdg-open "https://www.linkedin.com/search/results/all/?keywords=$PHONE" >/dev/null 2>&1

echo "--------------------------------------"

# 3. Leak Search (DeHashed & IntelligenceX instead of HIBP)
echo "[*] Checking leaks on DeHashed & IntelligenceX..."
xdg-open "https://www.dehashed.com/search?query=$PHONE" >/dev/null 2>&1
xdg-open "https://intelx.io/?s=$PHONE" >/dev/null 2>&1

echo "--------------------------------------"

# 4. Experimental Truecaller-style Lookup
# Using free API scrapers (sometimes blocked)
echo "[*] Trying Truecaller-style API..."
SCRAPER=$(curl -s "https://api.telnyx.com/v2/number_lookup/$PHONE" | jq -r '.data.carrier.name')
if [ "$SCRAPER" != "null" ]; then
    echo "[+] Found carrier info from Telnyx: $SCRAPER"
else
    echo "[-] No public info from Telnyx."
fi

echo "--------------------------------------"
echo "[*] Phone lookup complete!"
