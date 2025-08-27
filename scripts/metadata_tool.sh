#!/bin/bash
# =====================================
# Ghost OSINT - Metadata Extractor + Cleaner
# =====================================
# Usage:
#   ./metadata_tool.sh extract file.jpg
#   ./metadata_tool.sh clean file.jpg
# =====================================

MODE=$1
FILE=$2

if [ -z "$MODE" ] || [ -z "$FILE" ]; then
    echo "Usage: $0 <extract|clean> <file>"
    exit 1
fi

if ! command -v exiftool &> /dev/null; then
    echo "[!] exiftool not installed. Install it: sudo apt install exiftool -y"
    exit 1
fi

case $MODE in
    extract)
        echo "[*] Extracting metadata from: $FILE"
        echo "--------------------------------------"
        exiftool "$FILE"

        echo "--------------------------------------"
        GPS=$(exiftool "$FILE" | grep -i "GPS Position")
        if [ -n "$GPS" ]; then
            echo "[+] GPS Data Found: $GPS"
            echo "[*] Google Maps: https://www.google.com/maps?q=$(echo $GPS | awk '{print $3","$6}')"
        else
            echo "[-] No GPS data found."
        fi

        echo "--------------------------------------"
        echo "[*] Device & Software Details:"
        exiftool "$FILE" | grep -E "Camera|Make|Model|Software|Producer"
        echo "--------------------------------------"
        echo "[*] Metadata extraction complete!"
        ;;
    
    clean)
        echo "[*] Cleaning metadata from: $FILE"
        BACKUP="${FILE}_original"
        cp "$FILE" "$BACKUP"
        exiftool -all= "$FILE" > /dev/null
        echo "[+] All metadata wiped. Backup saved as: $BACKUP"
        ;;
    
    *)
        echo "[!] Invalid mode. Use extract or clean."
        ;;
esac
