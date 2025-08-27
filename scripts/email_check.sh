#!/bin/bash
# Ghost OSINT - Fast Email Check

if [ -z "$1" ]; then
    echo "Usage: $0 <email>"
    exit 1
fi

EMAIL="$1"

echo "[*] Checking email: $EMAIL"
echo "-------------------------------------"

# Basic format check
if [[ "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "[+] Email format looks valid."
else
    echo "[-] Invalid email format!"
    exit 1
fi

# Extract domain
DOMAIN=$(echo "$EMAIL" | cut -d "@" -f 2)
echo "[*] Checking domain: $DOMAIN"

# Fast DNS resolution
if host "$DOMAIN" > /dev/null 2>&1; then
    echo "[+] Domain resolves: $DOMAIN"
else
    echo "[-] Domain not resolving!"
fi

# MX record lookup with fast timeout
if command -v dig > /dev/null; then
    MX=$(dig +short MX "$DOMAIN" +time=1 +tries=1)
elif command -v nslookup > /dev/null; then
    MX=$(nslookup -type=mx "$DOMAIN" | grep "mail exchanger")
else
    echo "[!] Neither dig nor nslookup found. Cannot check MX records."
    MX=""
fi

if [ -n "$MX" ]; then
    echo "[+] MX records found for $DOMAIN:"
    echo "$MX"
else
    echo "[-] No MX records found."
fi

echo "-------------------------------------"
echo "[*] Email check complete (fast mode)."
