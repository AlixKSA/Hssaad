import requests
import time
from multiprocessing import Process, Barrier
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ================= إعدادات الحساب =================
SESSION = "session=56vjDxx6Xy1k5tJpk317DWyDvc-3VLvAEPM0ngKW-Rk"
NUM_HITS = 50 

headers_template = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Origin": "https://doge.tube",
    "Referer": "https://doge.tube/app",
    "Connection": "close" 
}

# --- سيرفر وهمي لإبقاء Render سعيداً ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- منطق الهجوم (نفس كودك الناجح) ---
def single_process_hit(vid_id, barrier, current_session):
    url = "https://doge.tube/api/feed/reward"
    payload = {"contentId": vid_id, "watchedSeconds": 65}
    local_headers = headers_template.copy()
    local_headers["Cookie"] = current_session
    try:
        barrier.wait(timeout=10)
        requests.post(url, headers=local_headers, json=payload, timeout=5)
    except: pass

def launch_reset_burst(vid_id):
    barrier = Barrier(NUM_HITS)
    processes = []
    for _ in range(NUM_HITS):
        p = Process(target=single_process_hit, args=(vid_id, barrier, SESSION))
        p.start()
        processes.append(p)
    for p in processes: p.join()

def run_bot():
    feed_url = "https://doge.tube/api/feed"
    main_headers = headers_template.copy()
    main_headers["Cookie"] = SESSION
    while True:
        try:
            res = requests.get(feed_url, headers=main_headers, timeout=10)
            items = res.json().get("items", [])
            unwatched = [v for v in items if v and not v.get('watched')]
            if not unwatched:
                time.sleep(30)
                continue
            for video in unwatched:
                launch_reset_burst(video.get("id"))
                time.sleep(5)
        except: time.sleep(10)

if __name__ == "__main__":
    # تشغيل السيرفر الوهمي في خيط منفصل
    threading.Thread(target=run_health_server, daemon=True).start()
    # تشغيل البوت الأساسي
    run_bot()
