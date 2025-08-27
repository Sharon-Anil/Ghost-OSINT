#!/bin/bash
# Website Fingerprinting

URL=$1
if [ -z "$URL" ]; then
    echo "Usage: $0 <website-url>"
    exit 1
fi

echo "[*] Scanning $URL ..."

# 1️⃣ HTTP headers
echo -e "\n--- HTTP Headers ---"
curl -sI "$URL"

# 2️⃣ Server & X-Powered-By
SERVER=$(curl -sI "$URL" | grep -i "Server:")
XPOWER=$(curl -sI "$URL" | grep -i "X-Powered-By:")
echo -e "\n[*] Server: $SERVER"
echo "[*] X-Powered-By: $XPOWER"

# 3️⃣ Check for CMS hints
HTML=$(curl -s "$URL")
if echo "$HTML" | grep -q "wp-content"; then
    echo "[*] CMS: WordPress detected"
elif echo "$HTML" | grep -q "Joomla"; then
    echo "[*] CMS: Joomla detected"
elif echo "$HTML" | grep -q "Drupal"; then
    echo "[*] CMS: Drupal detected"
else
    echo "[*] CMS: Unknown"
fi

# 4️⃣ Frontend frameworks
if echo "$HTML" | grep -q "React"; then
    echo "[*] Frontend: React detected"
fi
if echo "$HTML" | grep -q "Angular"; then
    echo "[*] Frontend: Angular detected"
fi
if echo "$HTML" | grep -q "Vue"; then
    echo "[*] Frontend: Vue.js detected"
fi

echo -e "\n[*] Fingerprinting Complete"
