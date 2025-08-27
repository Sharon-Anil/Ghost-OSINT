#!/bin/bash
photo="$1"

if [ -z "$photo" ]; then
  echo "[!] No photo provided!"
  exit 1
fi

echo "[*] Analyzing: $photo"
echo "----------------------------------"

# Step 1: EXIF Metadata
if command -v exiftool >/dev/null 2>&1; then
    echo "[*] Extracting EXIF metadata..."
    exiftool "$photo" | head -n 20
else
    echo "[!] exiftool not installed."
fi

# Step 2: Check if AI-generated
echo "[*] Detecting if photo might be AI-generated..."
if strings "$photo" | grep -iq "AI|StableDiffusion|Midjourney"; then
    echo "[⚠️] This image might be AI-generated."
else
    echo "[✓] Looks like a real photo (not AI detected)."
fi

# Step 3: Location (if GPS data available)
gps=$(exiftool "$photo" | grep "GPS Position")
if [ ! -z "$gps" ]; then
    echo "[*] GPS Data Found: $gps"
    echo "[*] Opening Google Maps..."
    coords=$(echo "$gps" | awk -F': ' '{print $2}')
    xdg-open "https://www.google.com/maps/search/?api=1&query=$coords" >/dev/null 2>&1
fi

# Step 4: Google Reverse Image Search
echo "[*] Opening Reverse Image Search..."
xdg-open xdg-open "https://www.duplichecker.com/reverse-image-search.php" >/dev/null 2>&1


# Step 5: Leaked DB Check (using hashes)
echo "[*] Checking leaked DBs (hash search)..."
hash=$(sha256sum "$photo" | awk '{print $1}')
curl -s "https://leakix.net/search?q=$hash" | grep -o "Leak\|Found" || echo "[✓] No leaks found."

echo "----------------------------------"
echo "[*] Photo analysis completed."
