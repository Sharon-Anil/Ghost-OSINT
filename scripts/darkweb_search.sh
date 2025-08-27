#!/bin/bash
# ===============================
# Ghost OSINT - Dark Web Search (Tor)
# ===============================
# Usage: ./darkweb_search.sh keyword
# ===============================

TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: $0 <keyword/email/username>"
    exit 1
fi

echo "[*] Starting Dark Web search for: $TARGET"
echo "--------------------------------------"

# Ensure Tor is running
if ! pgrep tor > /dev/null; then
    echo "[!] Tor is not running. Start it with: sudo systemctl start tor"
    exit 1
fi

# 1. Ahmia (clearnet search for onion sites)
echo "[*] Querying Ahmia.fi..."
torsocks curl -s "https://ahmia.fi/search/?q=$TARGET" \
    | grep -Eo 'https?://[^"]+' \
    | grep -i "\.onion" \
    | head -n 10

echo "--------------------------------------"

# 2. Haystak (dark web search engine, login required for full)
echo "[*] Open Haystak search manually (requires account):"
echo "    https://haystakvxad7wbk5.onion"

# 3. Torch (classic onion search engine)
echo "[*] Open Torch (manual):"
echo "    http://xmh57jrzrnw6insl.onion"

# 4. IntelligenceX (if API key set)
API_KEY="YOUR_API_KEY"
if [ "$API_KEY" != "YOUR_API_KEY" ]; then
    echo "[*] Querying IntelligenceX..."
    torsocks curl -s "https://2.intelx.io/intelligent/search?k=$API_KEY&s=$TARGET" | jq .
else
    echo "[!] IntelligenceX API key not set. Skipping..."
fi

echo "--------------------------------------"
echo "[*] Dark Web lookup complete!"
