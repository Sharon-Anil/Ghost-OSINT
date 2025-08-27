# Ghost-OSINT
👻 Ghost OSINT – A spooky Python tool for IP lookup, Tor usage, and OSINT tasks with GUI,
## ⚙️ Installation

### 1️⃣ Clone the Repository
git clone https://github.com/Sharon-Anil/Ghost-OSINT.git
cd Ghost-OSINT
2️⃣ Install Python Requirements.txt
pip install -r requirements.txt
3️⃣ (Optional) Install Tor
sudo apt update && sudo apt install tor -y
tor &

🚀 Run Ghost OSINT
python ghost_osint.py


When launched:

🎙️ Plays intro.mp3

👻 Shows ghost logo

🖥️ Loads the console with cyberpunk theme

🔮 The 9 Tools in Ghost OSINT
1. 🌍 IP Lookup

Check details about any IP.

Usage:

Select IP Lookup

Enter IP (example: 8.8.8.8)

Output:

[*] Running IP lookup for: 8.8.8.8
[+] Country: United States
[+] Region: California
[+] City: Mountain View

2. 🧅 Tor Mode (Anonymous Lookup)

Run your lookups through Tor for anonymity.

Steps:

tor &
python ghost_osint.py


Output:

[*] Routing through Tor...
[+] Public IP (Tor Exit): 185.220.101.47

3. 🔎 WHOIS Lookup

Get registration info of a domain.

Usage:

Select WHOIS Lookup

Enter domain: example.com

Output:

[+] Domain: example.com
[+] Registrar: IANA
[+] Creation Date: 1995-08-14
[+] Expiry: 2025-08-13

4. 🛰️ DNS Recon

Find DNS records (A, MX, NS, TXT).

Usage:

Select DNS Recon

Enter target: google.com

Output:

[+] A Record: 142.250.190.14
[+] MX Record: aspmx.l.google.com
[+] TXT Record: v=spf1 include:_spf.google.com ~all

5. 🌐 Subdomain Finder

Find subdomains of a target.

Usage:

Select Subdomain Finder

Enter target: yahoo.com

Output:

[+] Found: mail.yahoo.com
[+] Found: api.yahoo.com
[+] Found: login.yahoo.com

6. 🕵️ Port Scanner

Scan open ports on a host.

Usage:

Select Port Scanner

Enter IP/Host: scanme.nmap.org

Output:

[+] Port 22: Open (SSH)
[+] Port 80: Open (HTTP)
[+] Port 443: Open (HTTPS)

7. 📡 Banner Grabbing

Grab service banners from open ports.

Usage:

Select Banner Grabber

Enter IP: scanme.nmap.org

Enter port: 80

Output:

[+] HTTP/1.1 200 OK
[+] Server: Apache/2.4.18 (Ubuntu)

8. 📱 Social Media OSINT

Find profiles by username.

Usage:

Select Social OSINT

Enter username: elonmusk

Output:

[+] Twitter: https://twitter.com/elonmusk
[+] Instagram: https://instagram.com/elonmusk
[+] LinkedIn: Not Found

9. 🔦 Dark Web Checker

Check .onion sites via Tor.

Usage:

Start Tor (tor &)

Select Dark Web Checker

Enter onion address: http://duskgytldkxiuqc6.onion/

Output:

[*] Connecting via Tor...
[+] Status: Online
[+] Title: Dusk Hidden Service

📦 Project Structure
Ghost-OSINT/
│── ghost_osint.py       # main tool
│── requirements.txt     # dependencies
│── README.md            # documentation
│── intro.mp3            # ghost intro voice
│── ghost.png            # mascot
│── intro_bg.png         # background (optional)

⚡ Example Workflow
# Start Tor
tor &

# Run Ghost OSINT
python ghost_osint.py

# Use tools:
# - Lookup IPs
# - Run WHOIS
# - DNS Recon
# - Port Scan
# - Social OSINT

⚠️ Disclaimer

This project is for educational purposes only 🛡️.
Do not use for illegal activity. Author is not responsible for misuse.

📺 Follow Me

YouTube: HackWSharon

Instagram: @sharon_anil
