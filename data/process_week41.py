#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 lastfm_rules.json 处理 10.5-10.11 数据，输出逐行清单 + 专辑候选"""
import json, re
from collections import Counter, OrderedDict

rules = json.load(open("/workspace/scripts/lastfm_rules.json", encoding="utf-8"))
tracks = json.load(open("/workspace/data/week41_raw.json", encoding="utf-8"))

BL_ART = rules["blacklist_artists"]
KW = [k.lower() for k in rules["filter_keywords"]]
BL_TR = rules["blacklist_tracks"]
FEAT = rules["feat_map"]
AMP = rules["amp_map"]
SOLO = rules["solo_alias"]
ABS = rules["artist_by_song"]
TBS = rules["title_by_song"]
NO_SPLIT = set(rules["no_split"])

def norm_artist(a):
    a = a.strip()
    # 不拆含 & 、、/ 的（先查 no_split 与映射表）
    if a in NO_SPLIT: return a
    if a in SOLO: return SOLO[a]
    return a

# 1) 过滤
removed, kept = [], []
for t in tracks:
    a, ti = t["artist"].strip(), t["title"].strip()
    key = f"{a}|{ti}"
    if any(b in a for b in BL_ART):
        removed.append((key, "blacklist_artists")); continue
    if any(k in ti.lower() for k in KW):
        removed.append((key, "keyword:" + next(k for k in KW if k in ti.lower()))); continue
    if key in BL_TR:
        removed.append((key, "blacklist_tracks")); continue
    kept.append(t)

# 2) 去重（同歌手+曲名留最后一次）+ 同日去重
kept.sort(key=lambda t: t["ts"])
seen = {}
for t in kept:
    seen[(t["artist"].lower(), t["title"].lower())] = t  # 后播放覆盖
dedup = sorted(seen.values(), key=lambda t: (t["date"], t["ts"]))

# 3) 组合歌手归一（按出现频次归组，输出待确认组）
def artist_group(a):
    if a in FEAT: return ("feat", FEAT[a][0], FEAT[a][1])
    if a in AMP: return ("amp", AMP[a])
    # 含分隔符且无映射 → 待确认
    if re.search(r"[/&,、]", a) and a not in NO_SPLIT:
        return ("split?", a)
    return ("solo", a)

by_day = OrderedDict()
for t in dedup:
    by_day.setdefault(t["date"], []).append(t)

print("=" * 60)
print(f"拉取 {len(tracks)} → 过滤 {len(removed)} → 去重后 {len(dedup)}")
for k, why in removed: print(f"  [剔除] {k}  ({why})")
print("=" * 60)

# 待确认拆分
print("\n## 待确认歌手组合（无映射、含分隔符）")
need = set()
for t in dedup:
    g = artist_group(t["artist"])
    if g[0] == "split?": need.add(t["artist"])
for a in sorted(need): print(f"  {a}")
print("----")

# 逐行清单（含专辑信息）
print("\n## 逐行清单")
for d, items in by_day.items():
    print(f"\n### {d}（{len(items)} 首）")
    for t in items:
        alb = f"  《专辑:{t['album']}》" if t["album"] else ""
        print(f"{t['artist']} | {t['title']}{alb}")

# 4) 专辑候选（同专辑 >=2 首）
print("\n## 专辑候选（同专辑听满 2 首及以上）")
alb_cnt = Counter()
alb_art = {}
for t in dedup:
    if t["album"]:
        k = (t["album"], t["artist"])
        alb_cnt[k] += 1
        alb_art.setdefault(k, set()).add(t["title"])
for (alb, art), n in sorted(alb_cnt.items(), key=lambda x: -x[1]):
    if n >= 2:
        print(f"{alb} | {art} | {n} 首")
