#!/bin/bash
# Ghost OSINT - Username Lookup

if [ -z "$1" ]; then
    echo "Usage: $0 <username>"
    exit 1
fi

USERNAME="$1"
echo "[*] Searching for username: $USERNAME"
echo "-------------------------------------"

# GitHub
if curl -s -f "https://github.com/$USERNAME" > /dev/null; then
    echo "[+] Found on GitHub: https://github.com/$USERNAME"
else
    echo "[-] Not on GitHub"
fi

# Twitter/X
if curl -s -f "https://x.com/$USERNAME" > /dev/null; then
    echo "[+] Found on Twitter (X): https://x.com/$USERNAME"
else
    echo "[-] Not on Twitter (X)"
fi

# Instagram
if curl -s -f "https://www.instagram.com/$USERNAME/" > /dev/null; then
    echo "[+] Found on Instagram: https://www.instagram.com/$USERNAME/"
else
    echo "[-] Not on Instagram"
fi

# Reddit
if curl -s -f "https://www.reddit.com/user/$USERNAME" > /dev/null; then
    echo "[+] Found on Reddit: https://www.reddit.com/user/$USERNAME"
else
    echo "[-] Not on Reddit"
fi

echo "-------------------------------------"
echo "[*] Username lookup complete."
