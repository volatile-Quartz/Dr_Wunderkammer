# -*- coding: utf-8 -*-
import json, re
import jieba
from collections import Counter

with open("/tmp/diary_comments.json") as f:
    data = json.load(f)

SKIP_IDS = {5631444249, 5631450539, 5646741694}

NOISE = set("""px td style solid border ccc padding table width height background color font size center left right top bottom margin auto the of and in to for on with from by at was were is are not this that these those it its had back all my your we our they he she as or an be been being but if then them their there here when where who whom which why how via over under then than helvetica arial rgba rgb linear gradient repeat no repeat cover transparent important flex justify inherit initial html css tr th rowspan colspan align valign cell textalign borderradius border none display block inline grid opacity hover active div span fontweight whitespace wrap ellipsis overflow hidden contentsection content item imagetext textright textleft orz
""".split())

FUNC = set("的地得着过下了上里中后前和与或在就把被但而或是也还又都不一个个对从为以于这那这些那些什么怎么如何可以可能应该不会不是没有就是还是也是都要能会自己我们你们他们它们已经正在将要开始结束最后现在今天明天昨天本周上周下周周月年小时分钟秒次第一共每个每张每首每次每回等这样那样如此比更有更最非常真的太不大够不少两三三种几多少一点十分特别越发更加周星期月份日期日".split())

BLOCK_START = re.compile(r"^\s*[-*]?\s*(单曲|专辑|影音记录|观影记录|观影清单|观影手记|观影笔记|观影[：:（(]|音乐专辑|赏乐笔记|听歌记录|听歌笔记|音乐笔记|番剧|特摄|魔法卡片|魔卡|入册|套卡|歌单|本周入手|KTV|节奏大师|补番清单|Anime)")
MUSIC_LINE = re.compile(r"<sup>|单曲[:：]|专辑[:：]")
STRONG_SIGNAL = re.compile(r"张(专辑|原声|翻唱|单曲|现场)|专辑挑战|翻唱合辑|同人专辑|原声专辑|听歌|赏乐|LastFM|lastfm|网易云|ウルトラマン|ウルトラセブン|劇場版|アニメ|プリキュア|リコリス|やがて|第\d+-\d+话|第\d+话|补完|追番|补番|现场专辑|钢琴曲|配乐|原声带|唱片|合辑")
KTV_SONG = re.compile(r"^\s*\d+[.、]\s*[^《\n]{1,20}《[^》]*》\s*$")
CARD_DEF = re.compile(r"^\[\^[^\]]+\]:\s*共\s*\d+\s*张|面值|入册套卡")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")

FOREIGN_SIGNAL = re.compile(r"\b(de|Op\.|Act\.|No\.|Philharmonique|Orchestre|Orchestra|Overture|Prelude|Libro|quadrille|caprice|Concert|Symphoni|Sinfonia|Cantata|Sonata|Chœur|Choeur)\b", re.I)
TRACK_ROW = re.compile(r"^\s*\d+[ ||.|、]?\s*\S+.*\|\s*\d\d?:\d\d")

def keep_line(line):
    s = line.strip()
    if not s: return False
    if s.startswith("#"): return True
    if s.startswith("|") or s.startswith("<!--"): return False
    if TABLE_ROW.match(s): return False
    if BLOCK_START.match(s): return False
    if MUSIC_LINE.search(s): return False
    if STRONG_SIGNAL.search(s): return False
    if KTV_SONG.match(s): return False
    if CARD_DEF.search(s): return False
    if FOREIGN_SIGNAL.search(s): return False
    if TRACK_ROW.match(s): return False
    return True

def extract_comment(body):
    out = []
    ins = False
    for ln in body.split("\n"):
        if re.match(r"^#+\s*脚注\b", ln.strip()) or re.match(r"^#+\s*备注\b", ln.strip()) or re.match(r"^.*脚注：$", ln.strip()):
            ins = True
        if ins: continue
        if keep_line(ln): out.append(ln)
    return "\n".join(out)

def count_year(num):
    parts = []
    for c in data[str(num)]:
        if c["id"] in SKIP_IDS: continue
        body = extract_comment(c["body"])
        body = re.sub(r"\[\^[^\]]+\]", "", body)
        body = re.sub(r"<br\s*/?>", " ", body, flags=re.I)
        body = re.sub(r"\[[^\]]*\]\([^)]*\)", "", body)
        body = re.sub(r"https?://\S+", "", body)
        body = re.sub(r"\d+\.?\d*", " NUM ", body)
        body = re.sub(r"[^\u4e00-\u9fa5A-Za-z]", " ", body)
        parts.append(body)
    t = " ".join(parts)
    words = [w for w in jieba.cut(t)
             if len(w) >= 2 and w not in NOISE and w.lower() not in NOISE and w not in FUNC]
    return Counter(words), len(t)

c25, n25 = count_year(27)
c26, n26 = count_year(28)

for label, c, n in (("2025", c25, n25), ("2026", c26, n26)):
    print(f"\n########## {label} 日常 TOP 20 (字数 {n}) ##########")
    for w, cnt in c.most_common(20):
        print(f"{cnt}\t{w}")