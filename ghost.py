import tkinter as tk
from tkinter import simpledialog, scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk, ImageStat
import subprocess, threading, webbrowser, shutil, pyfiglet, os, queue, time

# ---------- Optional audio dependency ----------
# We'll try playsound; if missing, we fall back to system players.
try:
    from playsound import playsound
except Exception:  # not installed or env issue
    playsound = None

# -------------------------------------------------
# Config
# -------------------------------------------------
APP_TITLE   = "👻 Ghost OSINT"
CONSOLE_FONT = ("Cascadia Mono", 12)
HEADER_FONT  = ("Helvetica", 26, "bold")
BTN_FONT     = ("Helvetica", 12, "bold")

FG_NEON = "#00F5FF"
BG_DARK = "#000000"
FG_OK   = "#7CFC00"
FG_INFO = "#7FD1FF"
FG_WARN = "#FFD166"
FG_ERR  = "#FF6B6B"
FG_DIM  = "#B0B0B0"

YOUTUBE_URL = "https://www.youtube.com/@sharon_anil"

# Your assets (provide if you want)
INTRO_AUDIO = "intro.mp3"     # your voice: “I am inevitable.”
INTRO_IMAGE = "intro_bg.png"  # background for intro (optional)
GHOST_IMAGE = "ghost.png"     # ghost icon/logo (optional)

# -------------------------------------------------
# Globals
# -------------------------------------------------
root = tk.Tk()
output_text: scrolledtext.ScrolledText | None = None
status_lbl: tk.Label | None = None
current_proc: subprocess.Popen | None = None
loading_running = False

# -------------------------------------------------
# Helpers: logging + colors
# -------------------------------------------------
def log_line(text, tag=None):
    if not output_text:
        return
    output_text.configure(state="normal")
    output_text.insert(tk.END, text + "\n", tag)
    output_text.see(tk.END)
    output_text.configure(state="disabled")

def colorize_and_log(raw):
    line = raw.rstrip("\n")
    tag = None
    if line.startswith("[+]"):
        tag = "ok"
    elif line.startswith("[*]"):
        tag = "info"
    elif line.startswith("[-]"):
        tag = "warn"
    elif line.startswith("[!]"):
        tag = "err"
    log_line(line, tag)

# -------------------------------------------------
# Audio playback (robust, non-blocking)
# -------------------------------------------------
def _play_with_system_player(path: str) -> bool:
    """Try common CLI players; return True if started."""
    players = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
        ["mpg123", "-q", path],
        ["mpv", "--no-video", "--really-quiet", path],
        ["cvlc", "--play-and-exit", "--intf", "dummy", path],
        ["paplay", path],
        ["aplay", "-q", path],  # wav only
        ["afplay", path],       # mac
    ]
    for cmd in players:
        if shutil.which(cmd[0]):
            try:
                threading.Thread(
                    target=lambda: subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
                    daemon=True
                ).start()
                return True
            except Exception:
                continue
    return False

def play_audio_file(path: str):
    """Play audio in a background thread; quietly do nothing if it fails."""
    def worker():
        try:
            if not os.path.exists(path):
                return
            if playsound is not None:
                try:
                    playsound(path)  # blocks this thread only
                    return
                except Exception:
                    pass
            _play_with_system_player(path)
        except Exception:
            pass
    threading.Thread(target=worker, daemon=True).start()

# -------------------------------------------------
# Intro / Splash (only Ghost + banner + quote + creator)
# -------------------------------------------------
def show_intro():
    intro = tk.Toplevel(root)
    intro.configure(bg=BG_DARK)
    intro.geometry("920x500+300+120")
    intro.overrideredirect(True)

    # Background image (optional)
    if os.path.exists(INTRO_IMAGE):
        try:
            bg_img = Image.open(INTRO_IMAGE).resize((920, 500))
            bg_photo = ImageTk.PhotoImage(bg_img)
            bg_label = tk.Label(intro, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            pass

    # Content container (centered)
    frame = tk.Frame(intro, bg=BG_DARK)
    frame.pack(expand=True)

    # Ghost image or emoji
    try:
        if os.path.exists(GHOST_IMAGE):
            ghost_img = Image.open(GHOST_IMAGE).resize((140, 140))
            ghost_photo = ImageTk.PhotoImage(ghost_img)
            tk.Label(frame, image=ghost_photo, bg=BG_DARK).pack(pady=6)
            frame.ghost_photo = ghost_photo
        else:
            raise FileNotFoundError
    except Exception:
        tk.Label(frame, text="👻", font=("Helvetica", 56), fg=FG_NEON, bg=BG_DARK).pack(pady=6)

    # ASCII banner
    banner = pyfiglet.figlet_format("GHOST")
    tk.Label(frame, text=banner, font=("Courier", 16, "bold"),
             fg=FG_NEON, bg=BG_DARK, justify="center").pack()

    # Quote + creator
    tk.Label(frame, text='"I am inevitable."', font=("Helvetica", 18, "italic"),
             fg="#FF4B4B", bg=BG_DARK).pack(pady=(4, 8))
    tk.Label(frame, text="Created by Sharon Anil ⚡", font=("Helvetica", 14, "bold"),
             fg=FG_OK, bg=BG_DARK).pack()

    # Subtle pulsing dots under quote
    pulse_lbl = tk.Label(intro, text="[*] Initializing", font=("Courier", 13),
                         fg=FG_WARN, bg=BG_DARK)
    pulse_lbl.pack(pady=4)

    def pulse(c=0):
        pulse_lbl.config(text="[*] Initializing" + "." * (c % 4))
        intro.after(420, pulse, c + 1)

    pulse()
    play_audio_file(INTRO_AUDIO)  # voice/music
    # After splash, open main
    intro.after(4500, lambda: (intro.destroy(), show_main()))

# -------------------------------------------------
# Loading status bar
# -------------------------------------------------
def start_loading():
    global loading_running
    loading_running = True
    if status_lbl:
        status_lbl.config(text="[*] Working", fg=FG_WARN)
    animate_status(0)

def stop_loading():
    global loading_running
    loading_running = False
    if status_lbl:
        status_lbl.config(text="[✓] Done", fg=FG_OK)

def animate_status(step):
    if not loading_running:
        return
    if status_lbl:
        bar = "█" * ((step % 12) + 1)
        status_lbl.config(text=f"[*] Working {bar}")
    root.after(160, animate_status, step + 1)

# -------------------------------------------------
# Run scripts (streamed) + Stop support
# -------------------------------------------------
def run_script(script, args=None):
    """Run bash script under scripts/ and stream output lines safely to UI."""
    def worker(cmd, outq):
        global current_proc
        try:
            current_proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in current_proc.stdout:
                outq.put(line.rstrip("\n"))
            current_proc.wait()
        except Exception as e:
            outq.put(f"[!] Error: {e}")
        finally:
            outq.put("__PROC_DONE__")
            current_proc = None

    cmd = ["bash", os.path.join("scripts", script)]
    if args:
        if isinstance(args, (list, tuple)):
            cmd.extend(list(args))
        else:
            cmd.append(str(args))

    start_loading()
    if output_text:
        output_text.configure(state="normal")
        output_text.insert(tk.END, "\n", "dim")
        output_text.configure(state="disabled")

    outq = queue.Queue()
    threading.Thread(target=worker, args=(cmd, outq), daemon=True).start()

    def pump():
        try:
            while True:
                line = outq.get_nowait()
                if line == "__PROC_DONE__":
                    stop_loading()
                    return
                colorize_and_log(line)
        except queue.Empty:
            root.after(120, pump)

    pump()

def stop_current_job():
    global current_proc
    if current_proc and current_proc.poll() is None:
        try:
            current_proc.terminate()
            time.sleep(0.3)
            if current_proc.poll() is None:
                current_proc.kill()
            log_line("[!] Job stopped by user.", "warn")
        except Exception as e:
            log_line(f"[!] Failed to stop: {e}", "err")
    stop_loading()

# -------------------------------------------------
# Smart Photo Analysis (simple heuristic)
# -------------------------------------------------
def analyze_image(photo_path):
    try:
        img = Image.open(photo_path).convert("RGB")
        stat = ImageStat.Stat(img)
        variance = sum(stat.var) / max(1, len(stat.var))
        if variance < 50:
            return "⚠️ Possible AI-generated or overly smooth image"
        return "✅ Looks like a real photo (natural variance)"
    except Exception as e:
        return f"[!] Error analyzing image: {e}"

# -------------------------------------------------
# Tool handlers
# -------------------------------------------------
def username_lookup():
    username = simpledialog.askstring("Username Lookup", "Enter username:")
    if username:
        log_line(f"[1] Running username lookup for: {username}", "title")
        run_script("username_lookup.sh", username)

def email_check():
    email = simpledialog.askstring("Email Check", "Enter email address:")
    if email:
        log_line(f"[2] Running email check for: {email}", "title")
        run_script("email_check.sh", email)

def domain_recon():
    domain = simpledialog.askstring("Domain Recon", "Enter domain (example.com):")
    if domain:
        log_line(f"[3] Running domain recon for: {domain}", "title")
        run_script("domain_recon.sh", domain)

def photo_check():
    photo = filedialog.askopenfilename(
        title="Select an image file",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
    )
    if photo:
        log_line(f"[4] Running photo check on: {photo}", "title")
        log_line(analyze_image(photo), "warn")
        run_script("photo_leak_check.sh", photo)
        log_line("[+] Opening Google Images for reverse search...", "ok")
        webbrowser.open("https://images.google.com/")

def ip_lookup():
    ip = simpledialog.askstring("IP Lookup", "Enter IP address:")
    if not ip:
        return

    # Mode selector dialog
    mode = None
    def choose(x):
        nonlocal mode
        mode = x
        dlg.destroy()

    dlg = tk.Toplevel(root)
    dlg.title("IP Mode")
    dlg.configure(bg=BG_DARK)
    dlg.geometry("360x160+520+300")
    tk.Label(dlg, text="Choose lookup mode:", font=BTN_FONT,
             fg=FG_NEON, bg=BG_DARK).pack(pady=12)

    btnf = tk.Frame(dlg, bg=BG_DARK); btnf.pack(pady=8)
    tk.Button(btnf, text="Public (Country/Region/City)", command=lambda: choose("public"),
              width=28, bg="#1E1E1E", fg=FG_INFO, font=BTN_FONT).grid(row=0, column=0, padx=6, pady=4)
    tk.Button(btnf, text="Private (Full details)", command=lambda: choose("private"),
              width=28, bg="#1E1E1E", fg=FG_OK, font=BTN_FONT).grid(row=1, column=0, padx=6, pady=4)

    dlg.transient(root); dlg.grab_set()
    root.wait_window(dlg)

    if mode:
        log_line(f"[5] Running IP lookup for: {ip} [{mode}]", "title")
        run_script("ip_lookup.sh", [ip, mode])

def phone_lookup():
    phone = simpledialog.askstring("Phone Lookup", "Enter phone number (with country code):")
    if phone:
        log_line(f"[6] Running phone lookup for: {phone}", "title")
        run_script("phone_lookup.sh", phone)

def darkweb_search():
    keyword = simpledialog.askstring("Dark Web Search", "Enter search keyword:")
    if keyword:
        log_line(f"[7] Running dark web search for: {keyword}", "title")
        run_script("darkweb_search.sh", keyword)

def metadata_extractor():
    fpath = filedialog.askopenfilename(title="Select a file for metadata extraction")
    if not fpath:
        return
    log_line(f"[8] Extracting metadata from: {fpath}", "title")

    tool = os.path.join("scripts", "metadata_tool.sh")
    if os.path.exists(tool) and os.access(tool, os.X_OK):
        run_script("metadata_tool.sh", ["extract", fpath])
    elif shutil.which("exiftool"):
        def run_exiftool():
            start_loading()
            try:
                res = subprocess.run(["exiftool", fpath], capture_output=True, text=True)
                for ln in res.stdout.splitlines():
                    colorize_and_log(f"[*] {ln}")
            except Exception as e:
                colorize_and_log(f"[!] Error running exiftool: {e}")
            finally:
                stop_loading()
        threading.Thread(target=run_exiftool, daemon=True).start()
    else:
        try:
            import exifread
            def run_exifread():
                start_loading()
                try:
                    with open(fpath, "rb") as f:
                        tags = exifread.process_file(f)
                        if tags:
                            for k, v in tags.items():
                                colorize_and_log(f"[*] {k}: {v}")
                        else:
                            colorize_and_log("[-] No EXIF metadata found.")
                except Exception as e:
                    colorize_and_log(f"[!] Metadata extraction failed: {e}")
                finally:
                    stop_loading()
            threading.Thread(target=run_exifread, daemon=True).start()
        except ImportError:
            messagebox.showerror("Dependency missing",
                                 "Install one of:\n  sudo apt install exiftool\nor\n  pip install exifread")

def website_fingerprint():
    url = simpledialog.askstring("Website Fingerprint", "Enter website URL (https://example.com):")
    if url:
        log_line(f"[9] Running website fingerprint for: {url}", "title")
        run_script("website_fingerprint.sh", url)

def clear_console():
    if output_text:
        output_text.configure(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.configure(state="disabled")

# -------------------------------------------------
# Main GUI
# -------------------------------------------------
def show_main():
    root.deiconify()
    root.title(APP_TITLE)
    root.configure(bg=BG_DARK)
    root.geometry("1180x740+200+40")

    # Top bar
    topbar = tk.Frame(root, bg=BG_DARK); topbar.pack(fill="x")
    try:
        if os.path.exists(GHOST_IMAGE):
            ghost_img = Image.open(GHOST_IMAGE).resize((64, 64))
            ghost_photo = ImageTk.PhotoImage(ghost_img)
            gl = tk.Label(topbar, image=ghost_photo, bg=BG_DARK)
            gl.image = ghost_photo
            gl.pack(side="left", padx=10, pady=6)
        else:
            raise FileNotFoundError
    except Exception:
        tk.Label(topbar, text="👻", font=("Helvetica", 28), fg=FG_NEON, bg=BG_DARK).pack(side="left", padx=10, pady=6)
    tk.Label(topbar, text="Ghost OSINT", font=HEADER_FONT, fg=FG_NEON, bg=BG_DARK).pack(side="left", pady=8)

    # Main area
    main = tk.Frame(root, bg=BG_DARK); main.pack(fill="both", expand=True, padx=10, pady=6)

    # Left panel (tools)
    left_panel = tk.Frame(main, bg="#0E0E0E", bd=1, relief="ridge")
    left_panel.pack(side="left", fill="y", padx=(0,8), pady=4)

    tk.Label(left_panel, text="🛠️ Tools", font=("Helvetica", 14, "bold"),
             fg=FG_INFO, bg="#0E0E0E").pack(anchor="w", padx=10, pady=(10,6))

    buttons = [
        ("1️⃣  Username Lookup", username_lookup),
        ("2️⃣  Email Check", email_check),
        ("3️⃣  Domain Recon", domain_recon),
        ("4️⃣  Photo Check", photo_check),
        ("5️⃣  IP Lookup", ip_lookup),
        ("6️⃣  Phone Lookup", phone_lookup),
        ("7️⃣  Dark Web Search", darkweb_search),
        ("8️⃣  Metadata Extractor", metadata_extractor),
        ("9️⃣  Website Fingerprint", website_fingerprint),
    ]
    for (text, cmd) in buttons:
        tk.Button(left_panel, text=text, command=cmd, width=22,
                  bg="#1E1E1E", fg=FG_INFO, font=BTN_FONT,
                  activebackground="#2A2A2A", activeforeground=FG_NEON).pack(padx=10, pady=4)

    # Center (console + controls)
    center = tk.Frame(main, bg=BG_DARK); center.pack(side="left", fill="both", expand=True)

    controls = tk.Frame(center, bg=BG_DARK); controls.pack(anchor="w")
    tk.Button(controls, text="🧹 Clear", command=clear_console, width=10,
              bg="#333333", fg="#FFFFFF", font=BTN_FONT).grid(row=0, column=0, padx=6, pady=6)
    tk.Button(controls, text="⛔ Stop", command=stop_current_job, width=10,
              bg="#8B0000", fg="#FFFFFF", font=BTN_FONT).grid(row=0, column=1, padx=6, pady=6)
    tk.Button(controls, text="❌ Quit", command=root.quit, width=10,
              bg="#C62828", fg="white", font=BTN_FONT).grid(row=0, column=2, padx=6, pady=6)

    global status_lbl
    status_lbl = tk.Label(controls, text="Ready", font=("Courier", 12), fg=FG_DIM, bg=BG_DARK)
    status_lbl.grid(row=0, column=3, padx=10)

    global output_text
    output_text = scrolledtext.ScrolledText(center, width=100, height=30, bg="#0A0A0A",
                                            fg="#D7FFD7", insertbackground="#FFFFFF",
                                            font=CONSOLE_FONT, wrap="word")
    output_text.tag_config("ok", foreground=FG_OK)
    output_text.tag_config("info", foreground=FG_INFO)
    output_text.tag_config("warn", foreground=FG_WARN)
    output_text.tag_config("err", foreground=FG_ERR)
    output_text.tag_config("title", foreground=FG_NEON)
    output_text.tag_config("dim", foreground=FG_DIM)
    output_text.configure(state="disabled")
    output_text.pack(fill="both", expand=True, pady=(2,8))

    # Right panel (about + link)
    right_panel = tk.Frame(main, bg="#0E0E0E", bd=1, relief="ridge")
    right_panel.pack(side="right", fill="y", padx=(8,0), pady=4)

    tk.Label(right_panel, text="ℹ️ About", font=("Helvetica", 14, "bold"),
             fg=FG_INFO, bg="#0E0E0E").pack(anchor="w", padx=10, pady=(10,6))
    tk.Label(right_panel, text=(
        "• 👻 Ghost OSINT GUI\n"
        "• Built for ethical hacking / OSINT\n"
        "• Keep it legal & responsible\n"
    ), justify="left", fg="#E0E0E0", bg="#0E0E0E", font=("Helvetica", 12)).pack(anchor="w", padx=10)

    def open_yt(_evt=None): webbrowser.open(YOUTUBE_URL)
    yt = tk.Label(right_panel, text="▶️  HackWSharon (YouTube) — click",
                  fg=FG_WARN, bg="#0E0E0E", cursor="hand2", font=("Helvetica", 12, "bold"))
    yt.pack(anchor="w", padx=10, pady=(12,6))
    yt.bind("<Button-1>", open_yt)

# -------------------------------------------------
# Boot
# -------------------------------------------------
root.withdraw()          # hide root while intro shows
show_intro()             # intro will open main after it closes
root.mainloop()
