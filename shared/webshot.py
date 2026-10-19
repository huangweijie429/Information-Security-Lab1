"""Headless Edge screenshots over the DevTools protocol (no extra browsers needed).

Usage:
  python webshot.py URL OUT.png [--width 1440] [--height 900] [--wait 3] [--js "expr"] [--full]
"""
import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.request

import websocket

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
PORT = 9333
DIALOGS = []


def edge_path():
    import os
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("Edge not found")


def start_edge(url):
    subprocess.Popen([
        edge_path(), "--headless=new", f"--remote-debugging-port={PORT}",
        "--remote-allow-origins=*",
        r"--user-data-dir=D:\others\edgeprof", "--disable-gpu", "--hide-scrollbars",
        "--no-first-run", "--window-size=1440,900", url,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def page_target(prefix="", timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json") as r:
                pages = [t for t in json.load(r) if t.get("type") == "page"]
                for t in pages:
                    if prefix and prefix in t.get("url", ""):
                        return t["webSocketDebuggerUrl"]
                if pages:
                    return pages[-1]["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.5)
    raise SystemExit("no devtools target")


class CDP:
    def __init__(self, url):
        self.ws = websocket.create_connection(url, max_size=64 * 1024 * 1024)
        self.id = 0
        self.ws.settimeout(0.2)

    def send(self, method, **params):
        self.id += 1
        self.ws.send(json.dumps({"id": self.id, "method": method, "params": params}))
        target = self.id
        end = time.time() + 30
        while time.time() < end:
            try:
                msg = json.loads(self.ws.recv())
            except Exception:
                continue
            if msg.get("method") == "Page.javascriptDialogOpening":
                DIALOGS.append(msg["params"].get("message", ""))
                self.id += 1
                self.ws.send(json.dumps({"id": self.id, "method": "Page.handleJavaScriptDialog",
                                         "params": {"accept": True}}))
                continue
            if msg.get("id") == target:
                return msg.get("result", {})
        return {}

    def screenshot(self, path, full=False, width=1440, height=900):
        self.send("Emulation.setDeviceMetricsOverride", width=width, height=height,
                  deviceScaleFactor=1, mobile=False)
        res = self.send("Page.captureScreenshot", format="png", captureBeyondViewport=full)
        data = res.get("data")
        if not data:
            raise SystemExit("screenshot failed")
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--wait", type=float, default=4)
    ap.add_argument("--js", default="")
    ap.add_argument("--js-file", default="")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--post", type=float, default=2)
    a = ap.parse_args()
    if a.js_file:
        a.js = open(a.js_file, encoding="utf-8").read()

    start_edge(a.url)
    cdp = CDP(page_target(a.url))
    cdp.send("Page.enable")
    cdp.send("Runtime.enable")
    cdp.send("Page.navigate", url=a.url)
    time.sleep(a.wait)
    if a.js:
        res = cdp.send("Runtime.evaluate", expression=a.js, awaitPromise=True, returnByValue=True)
        val = res.get("result", {}).get("value")
        if val is not None:
            print("JS_RESULT:", str(val)[:2000])
        time.sleep(a.post)
    path = cdp.screenshot(a.out, a.full, a.width, a.height)
    print("saved", path)
    if DIALOGS:
        print("DIALOGS:", " | ".join(DIALOGS))
    cdp.ws.close()


if __name__ == "__main__":
    main()
