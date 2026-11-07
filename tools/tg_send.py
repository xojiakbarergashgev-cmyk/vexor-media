#!/usr/bin/env python3
"""Send a post described by a telegram.json file to the Telegram channel.

telegram.json format:
  {"method": "sendMediaGroup" | "sendMessage" | "sendPhoto" | "sendVideo",
   "payload": {...Bot API params, without chat_id...}}
Relative media paths ("2026-11-07/1800/s1.png") are turned into raw GitHub URLs.
"""
import json, os, sys, urllib.request

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ.get("TELEGRAM_CHAT_ID", "@vexor_uz")
REPO = os.environ.get("GITHUB_REPOSITORY", "xojiakbarergashgev-cmyk/vexor-media")
SHA = os.environ.get("GITHUB_SHA", "main")
RAW = f"https://raw.githubusercontent.com/{REPO}/{SHA}/"

def fix(v):
    return v if v.startswith(("http://", "https://")) else RAW + v.lstrip("/")

def send(path):
    spec = json.load(open(path, encoding="utf-8"))
    method, p = spec["method"], dict(spec["payload"])
    p["chat_id"] = CHAT
    if method == "sendMediaGroup":
        for m in p["media"]:
            m["media"] = fix(m["media"])
    for k in ("photo", "video", "animation", "document"):
        if isinstance(p.get(k), str):
            p[k] = fix(p[k])
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        print(path, "FAILED:", e.read().decode()); return False
    print(path, "OK" if r.get("ok") else r)
    return bool(r.get("ok"))

if __name__ == "__main__":
    ok = all([send(f) for f in sys.argv[1:] if f.strip()])
    sys.exit(0 if ok else 1)
