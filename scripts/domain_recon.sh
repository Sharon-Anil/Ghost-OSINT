#!/bin/bash

# Domain Recon Script with Subfinder
# Usage: ./domain_recon.sh example.com

domain=$1

if [ -z "$domain" ]; then
    echo "[!] Usage: $0 <domain>"
    exit 1
fi

echo "[*] Starting Domain Recon for: $domain"
echo "-----------------------------------------"

# WHOIS Lookup
echo "[+] WHOIS Information:"
whois $domain 2>/dev/null | head -n 20
echo "-----------------------------------------"

# DNS Records
echo "[+] DNS Records:"
dig $domain ANY +short
echo "-----------------------------------------"

# HTTP Headers
echo "[+] HTTP Headers:"
curl -I -s $domain | head -n 15
echo "-----------------------------------------"

# Subdomain Enumeration (Subfinder)
if command -v subfinder &>/dev/null; then
    echo "[+] Subdomains found with Subfinder:"
    subfinder -silent -d $domain | head -n 20
else
    echo "[!] Subfinder not installed. Install it from https://github.com/projectdiscovery/subfinder"
fi
echo "-----------------------------------------"

echo "[*] Domain Recon complete."

