#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮：修正规则后重跑，输出最终逐行清单 + 问题清单"""
import json, re
from collections import Counter, OrderedDict

rules = json.load(open("/workspace/scripts/lastfm_rules.json", encoding="utf-8"))
tracks = json.load(open("/workspace/data/week41_raw.json", encoding="utf-8"))

# ===== 本周新增规则（待用户确认后写回 rules.json）=====
NEW_BL_ART = ["央视网", "毛老猫", "波士顿圆脸", "镜哥的世界", "镜哥是本人", "军情播报",
              "孤烟暮蝉", "快嘴摩卡酱", "移动端音游搬运小队", "非洲のGUMI酱", "花女星家帮",
              "skutalu asmr", "水音世界观"]
PENDING_REMOVE = ["一池周啾", "云绵安", "HEMRecords", "MyGO_AveMujica", "凉默Coolsilence_",
                  "AdeIiae", "惊饕骇浪", "好饿好饿我想吃饭", "吉他战士六花", "碱性猫毛",
                  "花园多惠Official", "用户_23570001", "只为百合而活", "AIChannel中国绊爱",
                  "OurNotesOfficial", "Zaeiba_Official", "StarTK_Official"]
# cover 括注恢复（版本后缀去除而非剔除）
NEW_TBS = {
    # Cover 恢复
    "Happy Around!|気分上々↑↑ (Cover) (心情HIGH翻天↑↑)": "気分上々↑↑",
    "水樹奈々/Raychell|WOW WAR TONIGHT～時には起こせよムーヴメント～ (Cover) (TV动画《D4DJ First Mix》片尾曲)": "WOW WAR TONIGHT～時には起こせよムーヴメント～",
    "水樹奈々|WOW WAR TONIGHT～時には起こせよムーヴメント～ (AIRI Cover Ver.)": "WOW WAR TONIGHT～時には起こせよムーヴメント～",
    "Raychell|WOW WAR TONIGHT～時には起こせよムーヴメント～ (SHANO Cover Ver.)": "WOW WAR TONIGHT～時には起こせよムーヴメント～",
    "millsage|unravel (Cover)": "unravel",
    "millsage|青のすみか (Cover)": "青のすみか",
    "millsage|ロウワー (Cover) (Lower one's eyes)": "ロウワー",
    "一家Dumb Rock!|微笑みの爆弾 (Cover)": "微笑みの爆弾",
    "一家Dumb Rock!|Mela! (Cover)": "Mela!",
    "一家Dumb Rock!|革命道中 (Cover)": "革命道中",
    # MV 转载清洗
    "millsage_家団_ofc|millsage「鳴らす（奏鸣）」【Official Music Video】": "鳴らす",
    "millsage_家団_ofc|一家Dumb Rock!「ピースフル・ピーシーズ！（Peaceful・Pieces!）」【Official Music Video】": "ピースフル・ピーシーズ！",
    # 歌手名修正（MV 转载归属）
    "millsage_家団_ofc|鳴らす": "millsage",
    "millsage_家団_ofc|ピースフル・ピーシーズ！": "一家Dumb Rock!",
    # 译名括注/版本清理
    "John Dreamer|Rise - Epic Music": "Rise",
    "Epic Score|Liberators (解放者)": "Liberators",
    "WyvernP|Clock Paradox (时钟悖论)": "Clock Paradox",
    "Plum - Melodic Artist|별이 보이지 않는 밤 (2021 Remake) (看不见星星的夜晚)": "별이 보이지 않는 밤",
    "久石譲|海の見える街 (能看见海的城市)": "海の見える街",
    "CrossingSound|Engine x Start!! (melody mix)": "Engine x Start!!",
    "Bandari|Annie's Wonderland (安妮的仙境)": "Annie's Wonderland",
    "Snakywine|Classy Kitty (优雅小猫)": "Classy Kitty",
    "Instupendo|Six Forty Seven (6：47)": "Six Forty Seven",
    "nyamura|cat reincarnation (猫重生)": "cat reincarnation",
    "Krescent/neur6sia/LABYRINTH/DJ Aomori|Celestial Winter Wake (天穹冬醒)": "Celestial Winter Wake",
    "ぺのれり|Vacant Rhapsody (空煦狂想)": "Vacant Rhapsody",
    "Queen of Wand|ハートのA (红心A)": "ハートのA",
    "단비|비 내리던 가로수길 (Raining Garosu-gil Road) (Piano)": "비 내리던 가로수길",
    "Junk|Life is PIANO (Club Extend) (琴键人生)": "Life is PIANO",
    "Qutabire|In the Garden (繁花之间)": "In the Garden",
    "Elliot Hsu|A Guiding Star (引航之星)": "A Guiding Star",
    "夜暮青|零号患者 (PVZ恐怖版序章BOSS战二阶段主题曲)": "零号患者",
    "いきづらい部！|Tale of Primavera - Off Vocal": "Tale of Primavera",
    "Nanahira, コツメカワウソ’S|乙女のタクティクス - Instrument": "乙女のタクティクス",
    "削除|D-Birth (Artcore)": "D-Birth",
    "Arch vs n3pu|Evoltex (poppi'n mix)": "Evoltex",
    "黒皇帝|Scattered Faith (分散的信仰)": "Scattered Faith",
    "ginkiha|Fading Star (褪色之星)": "Fading Star",
    "96猫/置鮎龍太郎/千葉翔也|気分上々↑↑ (心情嗨翻天↑↑)": "気分上々↑↑",
    "Loveit Core/z²/BigDog Oof|惑わせらいやー feat. z²,BigDogOof (魅惑骗子 feat. z²,BigDogOof)": "惑わせらいやー",
    "Dmitri Shostakovich|VI. Waltz 2 from Jazz Suite No. 2 (Eyes Wide Shut)": "Waltz 2 from Jazz Suite No. 2",
    "一家Dumb Rock!|ホーミー・タイッ！！ (Homie's Tie!!)": "ホーミー・タイッ！！",
    "拿弓子的波塞东|無人区-Vacuum Track#ADD8E6（翻自:咲夜） (翻奏: Catalpa Vs. SharK)": "無人区-Vacuum Track#ADD8E6",
    "Catalpa Vs. SharK|無人区-Vacuum Track#ADD8E6（翻自:咲夜）": "無人区-Vacuum Track#ADD8E6",
    "米缐p.|无人区-Vacuum Track#ADD8E6-": "無人区-Vacuum Track#ADD8E6",
    "816ThreeNumbers|無人区-Vacuum Track#ADD8E6": "無人区-Vacuum Track#ADD8E6",
    "千野依&秋野桜|無人区-Vacuum Track": "無人区-Vacuum Track#ADD8E6",
    "Plum - Melodic Artist|Vanilla Flavored Soda (香草味苏打)": "Vanilla Flavored Soda",
    "Plum - Melodic Artist|Kaleidoscope (万花筒)": "Kaleidoscope",
    "はるまきごはん|ディナーベル（Dinner Bell） (晚餐铃)": "ディナーベル（Dinner Bell）",
    "littlealone100/Saiakoup|Light (Piano Mix)": "Light",
    "Happy Around!|仲良しのシリウス (好友天狼星)": "仲良しのシリウス",
    "Happy Around!|カレーライスが大好き♡ (超喜欢咖喱饭♡)": "カレーライスが大好き♡",
}
# 歌手名归一
NEW_SOLO = {"290 André Rieu": "André Rieu", "Juggernaut.&アイロボ": "Juggernaut."}
# 按歌修正歌手（第一遍标题清洗后按『歌手|新标题』匹配）
NEW_ABS = {
    "millsage_家団_ofc|鳴らす": "millsage",
    "millsage_家団_ofc|ピースフル・ピーシーズ！": "一家Dumb Rock!",
}
# 组合映射（& 除非曲名标 feat.）
NEW_AMP = [
    "Zubin Mehta/Wiener Philharmoniker/Johann Strauss, Sr.", "Zubin Mehta/Wiener Philharmoniker/Josef Strauss",
    "Zubin Mehta/Wiener Philharmoniker/Johann Strauss, Jr.", "Wiener Philharmoniker/Willi Boskovsky",
    "Andy Beer/David Groves/Graham Kirkby/John Olive/Mike Clements/Riccardo Muti/Wiener Philharmoniker",
    "Christian Thielemann/Wiener Philharmoniker", "Riccardo Muti/Wiener Philharmoniker/Johann Strauss, Jr.",
    "Pardubice Czech Chamber Philharmonic Orchestra/John Georgiadis", "Mariss Jansons/Wiener Philharmoniker",
    "Wiener Philharmoniker/Riccardo Muti", "Andris Nelsons/Wiener Philharmoniker",
    "David Groves/Riccardo Muti/Wiener Philharmoniker", "Wiener Philharmoniker/Fritz Reiner/Johannes Brahms",
    "Wiener Philharmoniker/Herbert von Karajan", "Herbert von Karajan/Wiener Philharmoniker",
    "Wiener Philharmoniker/Claudio Abbado", "Herbert von Karajan/Berliner Philharmoniker",
    "Berliner Philharmoniker/Karl Böhm", "Daniel Barenboim/Wiener Philharmoniker",
    "Wiener Singverein/Helmut Froschauer/Wiener Philharmoniker/Herbert von Karajan",
    "Angela Gheorghiu/Roberto Alagna/Thomas Hampson/Michel Plasson",
    "Academy of St. Martin in the Fields/Neville Marriner",
    "Iona Brown/Academy of St. Martin in the Fields/Marisa Robles",
    "Leonard Bernstein/New York Philharmonic", "André Previn/Wiener Philharmoniker",
    "Wiener Philharmoniker/Josef Sivo/Emanuel Brabec/Herbert von Karajan",
    "ARMNHMR/Synymata/Medyk", "Abandoned/Nytrix/DVRKCLOUD", "Far Out/DVRKCLOUD/RBBTS",
    "Jason Ross/Trivecta/RBBTS", "Jason Ross/Grant/your friend polly", "Seven Lions/Dia Frampton",
    "Seven Lions/So Below", "Seven Lions/Jason Ross/Fiora", "Nurko/Crystal Skies/KnownAsNat",
    "Nurko/Devon Baldwin", "Trivecta/Jay Mason", "Yetep/Luma", "Nurko/Chandler Leighton",
    "Synymata/KLAXX/Eke", "DJ Genki/yukacco", "DJ Noriken/aran", "Kobaryo/かめりあ",
    "Synthion/Kotori", "*Luna/ゆある/ねんね", "Jeko/Syuenn/Krasper2", "Akiri/HowToPlayLN",
    "littlealone100/Saiakoup", "Krescent/neur6sia/LABYRINTH/DJ Aomori", "NormalM/f2",
    "Bellyjay/KPHK", "削除/xi", "Camellia, Nanahira", "Nanahira, コツメカワウソ’S",
    "Picco&nyamura", "今井麻美/近藤佳奈子", "石渡太輔/佐藤ノリチカ", "96猫/置鮎龍太郎/千葉翔也",
    "Jun Kuroda + はがね", "御莉姫&廉", "花鋏キョウ&藍月なくる",
]
# feat. 映射（曲名带 feat. 或主创+演唱关系明确）
NEW_FEAT = {
    "Seven Lions/Dia Frampton": ["Seven Lions", "Dia Frampton"],
    "Seven Lions/So Below": ["Seven Lions", "So Below"],
    "Trivecta/Jay Mason": ["Trivecta", "Jay Mason"],
    "DJ Genki/yukacco": ["DJ Genki", "Yukacco"],
    "Synymata/KLAXX/Eke": ["Synymata & KLAXX", "EKE"],
    "Juggernaut.&アイロボ": ["Juggernaut.", "アイロボ"],
    "Loveit Core/z²/BigDog Oof": ["Loveit Core", "z² & BigDog Oof"],
    "御莉姫&廉": ["御莉姫", "廉"],
    "花鋏キョウ&藍月なくる": ["花鋏キョウ", "藍月なくる"],
}

def amp_join(a):
    a = a.replace(", Jr.", " ~JR~").replace(", Sr.", " ~SR~")
    parts = re.split(r"[/&,、]|\s\+\s", a)
    parts = [p.strip().replace(" ~JR~", ", Jr.").replace(" ~SR~", ", Sr.") for p in parts]
    return " & ".join(p for p in parts if p)

# ===== 处理 =====
def process():
    kept = []
    for t in tracks:
        # 归一不间断空格
        t["artist"] = t["artist"].replace("\xa0", " ").strip()
        t["title"] = t["title"].replace("\xa0", " ").strip()
        a, ti = t["artist"], t["title"]
        if any(b in a for b in rules["blacklist_artists"] + NEW_BL_ART): continue
        if a in PENDING_REMOVE: continue  # 本轮按建议剔除，清单中标注
        low = ti.lower()
        if any(k in low for k in rules["filter_keywords"]): continue
        kept.append(t)
    # 去重前清洗：第一遍标题，第二遍歌手
    for t in kept:
        key = f"{t['artist']}|{t['title']}"
        if key in NEW_TBS: t["title"] = NEW_TBS[key]
    for t in kept:
        a = t["artist"]
        abs_key = f"{a}|{t['title']}"
        if abs_key in NEW_ABS: t["artist"] = NEW_ABS[abs_key]
        a = t["artist"]
        if a in rules["solo_alias"]: t["artist"] = rules["solo_alias"][a]
        if t["artist"] in NEW_SOLO: t["artist"] = NEW_SOLO[t["artist"]]
        a = t["artist"]
        if a in NEW_FEAT: t["artist"] = NEW_FEAT[a][0] + " feat. " + NEW_FEAT[a][1]
        elif a in NEW_AMP: t["artist"] = amp_join(a)
        elif re.search(r"[/&,、]|\s\+\s", a) and a not in rules["no_split"]:
            t["artist"] = amp_join(a)  # 兜底：未映射组合按 & 连接
        # ver. 2024 / 括注通用清理
        t["title"] = re.sub(r"\s*\(ver\. 2024\)\s*", " ", t["title"]).strip()
    # 去重（同歌手+同曲留最后）
    seen = {}
    for t in sorted(kept, key=lambda x: x["ts"]):
        seen[(t["artist"].lower(), t["title"].lower())] = t
    return sorted(seen.values(), key=lambda t: (t["date"], t["ts"]))

final = process()
by_day = OrderedDict()
for t in final: by_day.setdefault(t["date"], []).append(t)

print(f"最终条目：{len(final)}")
for d, items in by_day.items():
    print(f"\n### {d}（{len(items)} 首）")
    for t in items:
        print(f"{t['artist']} | {t['title']}")

# 同曲多版本检查
print("\n## 同曲不同歌手（需决定记录方式）")
tc = Counter(t["title"].lower() for t in final)
for title, n in tc.items():
    if n >= 2:
        vers = [f"{t['artist']}《{t['title']}》({t['date']})" for t in final if t["title"].lower() == title]
        print(f"  {title}: " + " / ".join(vers))

# 专辑候选
print("\n## 专辑候选（>=2 首）")
alb = Counter()
for t in final:
    if t["album"]: alb[(t["album"], t["artist"])] += 1
for (a, ar), n in sorted(alb.items(), key=lambda x: (-x[1], x[0])):
    if n >= 2: print(f"  {a} | {ar} | {n} 首")

json.dump(final, open("/workspace/data/week41_final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
