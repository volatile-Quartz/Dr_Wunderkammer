#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拉取 10.5-10.11 Last.fm 听歌记录并按规则初步整理，输出逐行清单"""
import json, time, urllib.request, urllib.parse, os

API_KEY = "66b1c1ad34af302bb1672147f78e9e90"
USER = "volatile-Quartz"
FROM = 1791129600   # 2026-10-05 00:00:00 +08:00
TO = 1791734399     # 2026-10-11 23:59:59 +08:00

def fetch_page(page):
    qs = urllib.parse.urlencode({
        "method": "user.getrecenttracks", "user": USER, "api_key": API_KEY,
        "from": FROM, "to": TO, "format": "json", "limit": 200, "page": page
    })
    url = f"http://ws.audioscrobbler.com/2.0/?{qs}"
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if proxy:
        return json.load(urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy})).open(url, timeout=60))
    return json.load(urllib.request.urlopen(url, timeout=60))

tracks = []
page, total_pages = 1, 1
while page <= total_pages:
    data = fetch_page(page)
    attr = data["recenttracks"]["@attr"]
    total_pages = int(attr["totalPages"])
    for t in data["recenttracks"].get("track", []):
        if "@attr" in t and t["@attr"].get("nowplaying") == "true":
            continue  # 跳过正在播放
        ts = t.get("date", {}).get("uts")
        if ts and FROM <= int(ts) <= TO:
            tracks.append({
                "artist": t["artist"]["#text"], "title": t["name"],
                "album": t.get("album", {}).get("#text", ""),
                "ts": int(ts), "date": time.strftime("%Y-%m-%d", time.gmtime(int(ts) + 8*3600))
            })
    page += 1
    time.sleep(0.3)

print(f"共 {len(tracks)} 条 scrobble")
# 按日期统计
from collections import Counter
cnt = Counter(t["date"] for t in tracks)
for d in sorted(cnt): print(f"  {d}: {cnt[d]}")

# 存原始数据
os.makedirs("/workspace/data", exist_ok=True)
with open("/workspace/data/week41_raw.json", "w", encoding="utf-8") as f:
    json.dump(tracks, f, ensure_ascii=False, indent=1)
print("saved -> /workspace/data/week41_raw.json")
