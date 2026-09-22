# -*- coding: utf-8 -*-
import json, re
import jieba
from collections import Counter

with open("/tmp/diary_comments.json") as f:
    data = json.load(f)

SKIP_IDS = {5631444249, 5631450539, 5646741694}

NOISE = set("""px td style solid border ccc padding table width height background color font size center left right top bottom margin auto the of and in to for on with from by at was were is are not this that these those it its had back all my your we our they he she as or an be been being but if then them their there here when where who whom which why how via over under then than helvetica arial rgba rgb linear gradient repeat no repeat cover transparent important flex justify inherit initial html css tr th rowspan colspan align valign cell textalign borderradius border none display block inline grid opacity hover active div span fontweight whitespace wrap ellipsis overflow hidden contentsection content item imagetext textright textleft de today have DAY face value just one time set ve the a an and for with from this that or are all were was not been its had my our their then but didn don it's i'm we're they're you're i've で に の は を
""".split())

FUNC = "的地得着过下了上里中后前和与或在就把被但而或是也还又都不一个个对从为以于这那这些那些什么怎么如何可以可能应该不会不是没有就是还是也是都要能会自己我们你们他们它们已经正在将要开始结束最后现在今天明天昨天本周上周下周周月年小时分钟秒次第一共每个每张每首每次每回等这样那样如此比更有更最非常真的太不大够不少两三三种几多少一点十分特别越发更加周星期月份日期日又再但让被把对为从由只才只要既然就从而于是甚至居然竟然终于然后接着虽然但是因为所以因此由于无论不管只要如果那么并且或者还是另外此外总之例如比如作为关于对于按照根据由于及其甚至包括除了相比其中之间之一一种一个一位一项一条一座一个两个三种不管怎样无论如何想会要肯愿应该必须需要可能能够将要已经正在曾经当初起初原本本来一直始终常常往往偶尔经常总是每次每回身上手中这些那些极大不少挺十分非常特别十分超级格外故意特意全都统统完全彻底根本基本大约左右上下前后中间附近这样那样这么那么别的何其他另一种另一另一种单个独自一起各自具体来说总的来看说来话长总体所言不外乎总而言之换句话讲简而言之质言之专指专指具体某一般普遍通常常见偶尔少见罕见偶尔间或时而知乎大概也许或许大概可能说不清不得而知不确定不好说难说多半很可能说不定未必不见得未曾从前目前如今现时眼下现在此刻此时此刻当时将来未来以后往后今后日后日后来日方长今日昨日明天明日翌日当天当夜", "周星期月份日期日".split())

def clean_text(text):
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"<sup>.*?</sup>", "", text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\d+\.?\d*", " NUM ", text)
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z]", " ", text)
    return text

BLOCK_START = re.compile(r"^\s*[-*]?\s*(单曲|专辑|影音记录|观影记录|观影清单|观影手记|观影笔记|观影[：:（(]|音乐专辑|赏乐笔记|听歌记录|听歌笔记|音乐笔记|番剧|特摄|魔法卡片|魔卡|入册|套卡|歌单|本周入手|KTV|节奏大师|补番清单|Anime)")
MUSIC_LINE = re.compile(r"<sup>|单曲[:：]|专辑[:：]")
STRONG_SIGNAL = re.compile(r"张(专辑|原声|翻唱|单曲|现场)|专辑挑战|翻唱合辑|同人专辑|原声专辑|听歌|赏乐|LastFM|lastfm|网易云|ウルトラマン|ウルトラセブン|劇場版|アニメ|プリキュア|リコリス|やがて|第\d+-\d+话|第\d+话|补完|追番|补番|现场专辑|钢琴曲|配乐|原声带|唱片|合辑")
KTV_SONG = re.compile(r"^\s*\d+[.、]\s*[^《\n]{1,20}《[^》]*》\s*$")
CARD_DEF = re.compile(r"^\[\^[^\]]+\]:\s*共\s*\d+\s*张|面值|入册套卡")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")

def keep_line(line):
    s = line.strip()
    if not s or s.startswith("#") or s.startswith("|") or s.startswith("<!--"):
        return False
    if TABLE_ROW.match(s) or BLOCK_START.match(s) or MUSIC_LINE.search(s) \
       or STRONG_SIGNAL.search(s) or KTV_SONG.match(s) or CARD_DEF.search(s):
        return False
    return True

def extract(num):
    parts = []
    for c in data[str(num)]:
        if c["id"] in SKIP_IDS: continue
        out, ins = [], False
        for ln in c["body"].split("\n"):
            if re.match(r"^#+\s*(脚注|备注)\b", ln.strip()): ins = True
            if ins: continue
            if keep_line(ln): out.append(ln)
        parts.append(clean_text("\n".join(out)))
    return " ".join(parts)

for num, label in ((27, "2025"), (28, "2026")):
    t = extract(num)
    words = [w for w in jieba.cut(t) if len(w) >= 2 and w not in NOISE and w.lower() not in NOISE and w not in FUNC]
    c = Counter(words)
    print(f"########## {label} 日常 TOP15 ##########")
    for w, cnt in c.most_common(15):
        print(f"{cnt}\t{w}")
    print()

# 2026 前10可疑词来源
import collections
lines28 = []
for c in data["28"]:
    if c["id"] in SKIP_IDS: continue
    ins = False
    for ln in c["body"].split("\n"):
        if re.match(r"^#+\s*(脚注|备注)\b", ln.strip()): ins = True
        if ins: continue
        if keep_line(ln): lines28.append(ln)

print("###### '魔法'/'卡片' 保留行来源 ######")
for w in ("魔法", "卡片"):
    print("== ", w)
    for ln in lines28:
        if w in ln:
            idx = ln.find(w)
            print("  ", ln[max(0,idx-30):idx+40].strip()[:90])