#!/usr/bin/env python3
"""splicecraft: turn a raw talking-head clip into an edited short.

Only hard dependency is ffmpeg/ffprobe on PATH (built with libass).
Python 3.9+ standard library only.

Subcommands (run in order, or use `auto`):
  probe       print stream facts as JSON
  transcribe  word-level transcript -> words.json (Groq Whisper API or local faster-whisper)
  plan        words.json + level -> edl.json (cuts, captions, cards, zooms, sfx)
  render      source + edl.json -> finished mp4
  qa          check a render against the gates in SKILL.md step 6
  sheet       contact sheet jpg for visual review
  compare     side-by-side before/after mp4
  synth-music generate a license-free music bed wav
  auto        transcribe -> plan -> render -> qa -> sheet in one go
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import uuid
import wave
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRESETS = HERE.parent / "presets"


# ----------------------------------------------------------------- helpers
def die(msg: str, code: int = 1):
    print(f"[splicecraft] error: {msg}", file=sys.stderr)
    sys.exit(code)


def log(msg: str):
    print(f"[splicecraft] {msg}", file=sys.stderr)


def need(tool: str):
    if not shutil.which(tool):
        die(f"{tool} not found on PATH. Install ffmpeg first (see SKILL.md step 0).")


def run(cmd: list[str], quiet: bool = True) -> subprocess.CompletedProcess:
    log("$ " + " ".join(f'"{c}"' if " " in c else c for c in cmd)[:400])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        die(f"command failed: {cmd[0]}")
    return r


def read_json(p) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def write_json(p, data):
    Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def probe(src: str) -> dict:
    need("ffprobe")
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", src])
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        die("no video stream")
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    w, h = int(v["width"]), int(v["height"])
    if abs(rot) in (90, 270):
        w, h = h, w
    return {
        "width": w,
        "height": h,
        "fps": round(float(num) / float(den or 1), 3),
        "duration": float(d["format"]["duration"]),
        "has_audio": a is not None,
        "orientation": "vertical" if h > w else ("square" if h == w else "horizontal"),
    }


# ------------------------------------------------------------- transcribe
def read_key(env: str, file_hint: str | None) -> str | None:
    k = os.environ.get(env)
    if not k and file_hint and Path(file_hint).exists():
        k = Path(file_hint).read_text(encoding="utf-8-sig")
    if not k:
        return None
    k = k.replace("\ufeff", "").strip()
    m = re.search(r"gsk_[A-Za-z0-9]+", k)
    return m.group(0) if m else k.split()[0]


def multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    b = uuid.uuid4().hex
    out = bytearray()
    for k, vals in fields.items():
        for v in vals if isinstance(vals, list) else [vals]:
            out += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    for k, (name, data, ctype) in files.items():
        out += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{name}\"\r\nContent-Type: {ctype}\r\n\r\n".encode()
        out += data + b"\r\n"
    out += f"--{b}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={b}"


def transcribe(src: str, out: str, language: str | None, key_file: str | None, engine: str):
    need("ffmpeg")
    tmp = Path(tempfile.mkdtemp()) / "voice.mp3"
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", str(tmp)])
    words, segments, lang = [], [], language
    key = read_key("GROQ_API_KEY", key_file)
    if engine in ("auto", "groq") and key:
        if tmp.stat().st_size > 24 * 1024 * 1024:
            die("audio over 24MB; split the clip or use --engine local")
        fields = {"model": "whisper-large-v3", "response_format": "verbose_json",
                  "timestamp_granularities[]": ["word", "segment"]}
        if language:
            fields["language"] = language
        body, ctype = multipart(fields, {"file": ("voice.mp3", tmp.read_bytes(), "audio/mpeg")})
        req = urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=body,
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": ctype,
                                              "User-Agent": "splicecraft/1.0"})
        log("transcribing with Groq whisper-large-v3")
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode())
        words = [{"w": x["word"].strip(), "s": float(x["start"]), "e": float(x["end"])} for x in d.get("words", [])]
        segments = [{"text": s["text"].strip(), "s": float(s["start"]), "e": float(s["end"])} for s in d.get("segments", [])]
        lang = d.get("language", language)
    elif engine in ("auto", "local"):
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError:
            die("no GROQ_API_KEY and faster-whisper is not installed. Either export GROQ_API_KEY "
                "or run: pip install faster-whisper")
        log("transcribing locally with faster-whisper small")
        model = WhisperModel("small", compute_type="int8")
        segs, info = model.transcribe(str(tmp), word_timestamps=True, language=language)
        for s in segs:
            segments.append({"text": s.text.strip(), "s": s.start, "e": s.end})
            for x in s.words or []:
                words.append({"w": x.word.strip(), "s": x.start, "e": x.end})
        lang = info.language
    else:
        die("engine groq selected but GROQ_API_KEY is missing")
    words = attach_punctuation(words, segments)
    write_json(out, {"source": os.path.basename(src), "language": lang, "words": words, "segments": segments})
    log(f"wrote {out} ({len(words)} words)")


def norm(t: str) -> str:
    return re.sub(r"[^\w%]", "", t.lower())


def attach_punctuation(words, segments):
    """Whisper word lists often drop punctuation; copy it back from segment text."""
    toks, seg_of = [], []
    for gi, s in enumerate(segments):
        for tok in s["text"].split():
            toks.append(tok)
            seg_of.append(gi)
    j = 0
    for w in words:
        nw = norm(w["w"])
        for k in range(j, min(j + 4, len(toks))):
            if norm(toks[k]) == nw:
                w["w"] = toks[k]
                w["g"] = seg_of[k]
                j = k + 1
                break
        else:
            w["g"] = seg_of[j - 1] if j and seg_of else 0
    return words


# ------------------------------------------------------------------ plan
NUMBER_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10, "twenty": 20, "fifty": 50, "hundred": 100, "thousand": 1000,
                "nol": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5, "enam": 6, "tujuh": 7,
                "delapan": 8, "sembilan": 9, "sepuluh": 10, "seratus": 100, "seribu": 1000}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
            "pertama": 1, "kedua": 2, "ketiga": 3, "keempat": 4, "kelima": 5}
VERSUS = {"vs", "versus", "or", "compare", "before", "after", "atau", "lawan", "banding", "sebelum", "sesudah"}
QUOTE = {"they say", "quote", "said", "kata orang", "pepatah"}
CTA = {"follow", "subscribe", "comment", "like", "share", "link", "ikuti", "komentar", "bagikan"}
STOP = set("a an the and or but so to of in on at is are was were be it this that i you he she we they my your "
           "for with as by from not just one do does did have has had here there what which who how why "
           "yang dan di ke dari ini itu aku saya kamu kita untuk dengan atau tapi jadi "
           "thats its im ive youre dont doesnt heres theres lets whats well okay yeah thanks bye now "
           "some every all about into only really very".split())
FILLER = {"thats it", "thanks", "bye", "okay", "thats it for now"}


def params_for(level: int) -> dict:
    L = clamp(int(level), 1, 100)
    presets = read_json(PRESETS / "levels.json")["tiers"]
    tier = next(t for t in presets if t["min"] <= L <= t["max"])
    f = L / 100.0
    p = dict(tier["params"])
    p.update({
        "level": L,
        "tier": tier["name"],
        "silence_gap": round(0.95 - 0.65 * f, 3),       # remove pauses longer than this (s)
        "cards_per_min": round(10 * f, 1),             # density ceiling
        "min_card_gap": round(max(2.0, 11 - 9 * f), 2),  # breathing room between cards (s)
        "zoom_amount": round(1.0 + 0.22 * f, 3),
        "grade_strength": round(0.25 + 0.75 * f, 3),
    })
    return p


def sentences(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r"[.?!]$", w["w"]) or w.get("brk") or i + 1 == len(words):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def number_value(tok: str):
    t = norm(tok)
    if re.fullmatch(r"\d+(\.\d+)?%?", t):
        return t
    if t in NUMBER_WORDS:
        return str(NUMBER_WORDS[t])
    return None


def build_keep(words, gap, pad, duration):
    """Segments of source time to keep. Long pauses between words are removed."""
    if not words:
        return [[0.0, duration]]
    keep = [[max(0.0, words[0]["s"] - pad), words[0]["e"]]]
    for a, b in zip(words, words[1:]):
        if b["s"] - a["e"] > gap:
            keep[-1][1] = min(duration, a["e"] + pad)
            keep.append([max(0.0, b["s"] - pad), b["e"]])
        else:
            keep[-1][1] = b["e"]
    keep[-1][1] = min(duration, keep[-1][1] + pad * 3)
    merged = []
    for s, e in keep:
        if merged and s <= merged[-1][1] + 0.02:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([round(s, 3), round(e, 3)])
    return merged


def remap_fn(keep):
    offs, acc = [], 0.0
    for s, e in keep:
        offs.append((s, e, acc))
        acc += e - s

    def f(t):
        for s, e, o in offs:
            if t < s:
                return o
            if t <= e:
                return o + (t - s)
        return acc
    return f, acc


def detect_genre(words) -> dict:
    """Score every genre in presets/genres.json against the transcript. Returns the ranking."""
    text = " " + " ".join(norm_sentence(w["w"]) for w in words) + " "
    text = re.sub(r"\s+", " ", text)
    n = max(1, len(words))
    genres = read_json(PRESETS / "genres.json")["genres"]
    scores = {}
    for name, g in genres.items():
        hits = {}
        for k in g["keywords"]:
            kk = " " + re.sub(r"\s+", " ", norm_sentence(k)).strip() + " "
            c = text.count(kk)
            if c:
                hits[k.strip()] = c * (2 if (" " in kk.strip() or len(kk.strip()) >= 7) else 1)
        scores[name] = {"score": sum(hits.values()) * 100.0 / n, "hits": hits}
    nums = sum(1 for w in words if number_value(w["w"]) is not None)
    qs = sum(1 for w in words if w["w"].endswith("?"))
    scores["education_explainer"]["score"] += nums * 40.0 / n
    scores["podcast_talk"]["score"] += qs * 60.0 / n
    ranked = sorted(scores.items(), key=lambda kv: -kv[1]["score"])
    best = ranked[0][0] if ranked[0][1]["score"] >= 1.0 else "education_explainer"
    return {"genre": best, "label": genres[best]["label"], "ranking": [
        {"genre": k, "score": round(v["score"], 2), "hits": v["hits"]} for k, v in ranked]}


def variant_theme(theme, genre_cfg, variants, seed):
    """Deterministic per-video variation: accent from the genre palette, caption size, card height, grade."""
    pal = genre_cfg["palettes"]
    theme["accent"] = pal[seed % len(pal)]
    theme["caption_size"] = int(round(theme.get("caption_size", 74) * variants["caption_size_scale"][(seed // 8) % 3]))
    theme["card_y"] = theme.get("card_y", 230) + variants["card_y_offset"][(seed // 24) % 3]
    g = variants["grade"][(seed // 72) % len(variants["grade"])]
    if g != "style":
        theme["grade"] = g
    theme["cta_text"] = genre_cfg["cta_text"]
    theme["music_mood"] = genre_cfg["music_mood"]
    theme["bpm"] = genre_cfg["bpm"]
    return theme


def option_count() -> dict:
    """How many distinct edit setups the planner can produce, computed from the preset files."""
    styles = read_json(PRESETS / "styles.json")
    gp = read_json(PRESETS / "genres.json")
    v = gp["variants"]
    palettes = len(next(iter(gp["genres"].values()))["palettes"])
    per = palettes * len(v["caption_size_scale"]) * len(v["card_y_offset"]) * len(v["grade"])
    total = len(gp["genres"]) * len(styles) * per * 100 * 3
    return {"music_templates": len(music_templates()), "genres": len(gp["genres"]), "styles": len(styles), "variants_per_genre_and_style": per,
            "levels": 100, "aspect_ratios": 3, "total_combinations": total}


BRIEF_ORDER = ["platform", "market", "age", "stage", "funnel", "niche"]


def load_brief(path: str | None) -> dict:
    if not path:
        return {}
    b = read_json(path)
    aud = read_json(PRESETS / "audience.json")
    for k in BRIEF_ORDER:
        if b.get(k) and b[k] not in aud[k]:
            die(f"brief: unknown {k} '{b[k]}'; choose from {', '.join(aud[k])}")
    return b


def brief_effects(b: dict) -> dict:
    """Fold a brief into one set of edit decisions, with the reason for each."""
    aud = read_json(PRESETS / "audience.json")
    eff = {"level": 0, "density": 1.0, "caption_scale": 1.0, "caption_modes": [], "style": None, "energy": None,
           "grade": None, "cta": None, "size": None, "moods": [], "frameworks": [], "compliance": [], "why": []}
    for k in BRIEF_ORDER:
        if not b.get(k):
            continue
        e = aud[k][b[k]]
        eff["level"] += e.get("level", 0)
        eff["density"] *= e.get("density", 1.0)
        eff["caption_scale"] *= e.get("caption_scale", 1.0)
        for m in e.get("caption_modes", []):
            if m in CAPTION_MODES and m not in eff["caption_modes"]:
                eff["caption_modes"].append(m)
        for f in ("style", "energy", "grade", "cta", "size"):
            if e.get(f) and not (f == "cta" and eff["cta"] not in (None, "follow") and k == "funnel"):  # a specific market CTA beats the funnel CTA
                eff[f] = e[f]
        eff["moods"] += e.get("moods", [])
        eff["frameworks"] += e.get("frameworks", [])
        if e.get("compliance"):
            eff["compliance"].append(e["compliance"])
        eff["why"].append(f"{k}={b[k]}: {e.get('note', '')}".rstrip(": "))
    eff["density"] = round(eff["density"], 3)
    eff["caption_scale"] = round(eff["caption_scale"], 3)
    return eff


def brief_report(b: dict) -> dict:
    eff = brief_effects(b)
    aud = read_json(PRESETS / "audience.json")
    rep_ = {"effects": eff, "checks": []}
    tam, sam, som = (b.get("tam"), b.get("sam"), b.get("som"))
    if tam and sam and som:
        if not (som <= sam <= tam):
            rep_["checks"].append("FAIL: need SOM <= SAM <= TAM")
        else:
            rep_["checks"].append(f"market: SAM is {sam / tam:.0%} of TAM, SOM is {som / sam:.1%} of SAM")
    if b.get("revenue_target") and b.get("price"):
        fd = dict(aud["funnel_defaults"])
        fd.update({k: b[k] for k in ("view_to_profile", "profile_to_click", "click_to_buy") if k in b})
        buyers = b["revenue_target"] / b["price"]
        views = buyers / (fd["view_to_profile"] * fd["profile_to_click"] * fd["click_to_buy"])
        rep_["revenue_math"] = {"buyers_needed": round(buyers), "views_needed": round(views),
                                "assumptions": {k: fd[k] for k in ("view_to_profile", "profile_to_click", "click_to_buy")},
                                "warning": "Assumptions are placeholders unless the brief sets them from real analytics."}
        if som and buyers > som:
            rep_["checks"].append(f"FAIL: revenue target needs {round(buyers)} buyers but SOM is {som}")
    p_ = b.get("platform")
    if p_ and b.get("seconds"):
        lo, hi = aud["platform"][p_]["ideal_seconds"]
        if not lo <= b["seconds"] <= hi:
            rep_["checks"].append(f"WARN: {b['seconds']} s is outside {p_}'s usual {lo}-{hi} s")
    return rep_


def plan(words_path: str, out: str, level: int, style: str, duration: float | None, brand: str | None,
         no_cut: bool, genre: str = "none", variant: int | None = None, captions: str | None = None,
         brief: str | None = None):
    data = read_json(words_path)
    words = data["words"]
    if not words:
        die("transcript has no words")
    styles = read_json(PRESETS / "styles.json")
    gp = read_json(PRESETS / "genres.json")
    detected, gcfg = None, None
    if genre == "auto" or style == "auto":
        detected = detect_genre(words)
        if genre in ("auto", "none"):
            genre = detected["genre"]
    if genre != "none":
        if genre not in gp["genres"]:
            die(f"unknown genre {genre}; choose from auto, none, {', '.join(gp['genres'])}")
        gcfg = gp["genres"][genre]
        level = clamp(int(level) + gcfg["level_shift"], 1, 100)
    bf = load_brief(brief)
    eff = brief_effects(bf) if bf else None
    if eff:
        level = clamp(int(level) + eff["level"], 1, 100)
    if style == "auto":
        style = (eff or {}).get("style") or (gcfg["style"] if gcfg else "studio")
    if style not in styles:
        die(f"unknown style {style}; choose from auto, {', '.join(styles)}")
    p = params_for(level)
    if captions:
        p["captions"] = captions
    theme = dict(styles[style])
    theme["style"] = style
    if gcfg:
        if variant is None:
            variant = int(hashlib.sha1(" ".join(w["w"] for w in words).encode("utf8")).hexdigest(), 16) % 360
        o = dict(gcfg["params"])
        p["cards_per_min"] = round(p["cards_per_min"] * o.pop("cards_per_min_scale", 1.0), 2)
        p["zoom_amount"] = round(1 + (p["zoom_amount"] - 1) * o.pop("zoom_scale", 1.0), 3)
        p.update(o)
        if not captions and p["level"] > 20:
            cm = gcfg.get("caption_modes") or [p["captions"]]
            p["captions"] = cm[(int(variant or 0) // 5) % len(cm)] if variant is not None else cm[0]
        p["genre"] = genre
        p["drop_beats"] = gcfg["drop_beats"]
        theme = variant_theme(theme, gcfg, gp["variants"], int(variant))
        p["variant"] = int(variant)
    if eff:
        p["cards_per_min"] = round(p["cards_per_min"] * eff["density"], 2)
        theme["caption_size"] = int(round(theme.get("caption_size", 74) * eff["caption_scale"]))
        if eff["caption_modes"] and not captions and p["level"] > 20:
            p["captions"] = eff["caption_modes"][int(variant or 0) % len(eff["caption_modes"])]
        if eff["grade"]:
            theme["grade"] = eff["grade"]
        if eff["cta"]:
            theme["cta_text"] = eff["cta"][0].upper() + eff["cta"][1:]
        if p["level"] >= 81 and bf.get("age") in ("gen_x", "boomer"):
            p["flash"] = False
        p["brief"] = {"input": bf, "why": eff["why"], "compliance": eff["compliance"]}
    mp = pick_music(words, genre if genre != "none" else None, style, int(variant or 0))
    if eff and (eff["energy"] or eff["moods"]):
        mood, key, drums, timbre, energy = mp["template"].split(".")
        mm = read_json(PRESETS / "music.json")["moods"]
        moods = [m for m in eff["moods"] if m in mm]
        mp["template"] = ".".join([moods[int(variant or 0) % len(moods)] if moods else mood, key, drums, timbre,
                                   eff["energy"] or energy])
        mp["reason"] += "; brief adjusted mood/energy"
    theme["music_template"] = mp["template"]
    p["music_pick"] = mp
    if brand:
        theme.update(read_json(brand))
    dur = duration or (words[-1]["e"] + 0.8)
    keep = [[0.0, dur]] if no_cut or p["silence_gap"] > 5 else build_keep(words, p["silence_gap"], 0.12, dur)
    rm, out_dur = remap_fn(keep)
    W = []
    for i, w in enumerate(words):
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = nxt is None or (nxt["s"] - w["e"] > 0.5) or (nxt.get("g", 0) != w.get("g", 0))
        W.append({"w": w["w"], "s": round(rm(w["s"]), 3), "e": round(rm(w["e"]), 3), "brk": bool(brk)})
    sents = sentences(W)

    cards, zooms, sfx, seen_numbers = [], [], [], {}
    last_card_end = -99.0
    budget = max(0, int(round(p["cards_per_min"] * out_dur / 60.0)))
    ranking = None
    pending_quote = False
    cta_done = False

    announced = False

    def room(t, strong=False):
        # strong beats (numbers, rankings, comparisons) and announced beats only need a short gap
        if strong or announced:
            return t - last_card_end >= 0.9
        return t - last_card_end >= p["min_card_gap"]

    def add_card(c):
        nonlocal last_card_end, budget
        if budget <= 0 and c["type"] not in ("hook", "cta"):
            return False
        cards.append(c)
        last_card_end = c["end"]
        if c["type"] not in ("hook", "cta"):
            budget -= 1
        if p.get("sfx"):
            sfx.append({"t": c["start"], "kind": "whoosh" if c["type"] in ("versus", "ranking") else "pop"})
        return True

    prev_low = ""
    for si, idx in enumerate(sents):
        sw = [W[i] for i in idx]
        text = " ".join(w["w"] for w in sw)
        low = " " + norm_sentence(text) + " "
        s0, s1 = sw[0]["s"], sw[-1]["e"]
        end = min(out_dur, max(s0 + 1.6, min(s1 + 0.6, s0 + 4.2)))
        announced = si > 0 and len(sents[si - 1]) <= 7 and bool(
            re.match(r"(here s|heres|here is|here are|now|ini|berikut)\b", prev_low))
        prev_low = low.strip()

        # hook: first sentence gets a kinetic title
        if si == 0 and p.get("hook_title"):
            add_card({"type": "hook", "start": s0, "end": max(end, s0 + 2.4),
                      "text": clean(text), "label": ""})
            if p["zoom"]:
                zooms.append({"start": s0, "end": min(s1, s0 + 2.0), "amount": p["zoom_amount"], "ease": "in"})
            continue

        if any(w in low for w in (" " + c + " " for c in CTA)) and s0 > out_dur * 0.6:
            if not cta_done and re.search(r"\b(follow|subscribe|ikuti)\b", low):
                cta_done = True
                add_card({"type": "cta", "start": s0, "end": min(out_dur, s1 + 1.5), "text": clean(text), "label": ""})
                continue
            m = re.search(r"\bcomment\W+(\w+)", text, re.I)
            if m and room(s0):
                add_card({"type": "question", "start": s0, "end": min(out_dur, s0 + 3.2), "label": "",
                          "text": f"Comment {m.group(1).upper()}"})
                continue

        was_pending, pending_quote = pending_quote, False
        if (any(q in low for q in QUOTE) or was_pending) and room(s0):
            if len(sw) <= 4 and not was_pending:
                pending_quote = True  # "Here's a quote." -> the quote itself is the next sentence
                continue
            add_card({"type": "quote", "start": s0, "end": min(out_dur, s1 + 0.6), "label": "QUOTE",
                      "text": clean(text)})
            continue

        if re.search(r"\bbefore and after\b|\bsebelum dan sesudah\b", low) and room(s0, True):
            add_card({"type": "versus", "start": s0, "end": min(out_dur, s0 + 3.5), "label": "",
                      "left": "BEFORE", "right": "AFTER"})
            continue

        ords = [(ORDINALS[norm(w["w"])], w) for w in sw if norm(w["w"]) in ORDINALS]
        if ords and p.get("allow_ranking", True):
            rank, ow = ords[0]
            item = " ".join(x["w"] for x in sw if x is not ow and norm(x["w"]) not in STOP)[:22] or ow["w"]
            if ranking and rank == ranking["items"][-1]["rank"] + 1 and s0 - ranking["end"] < 6:
                ranking["items"].append({"rank": rank, "text": clean(item), "t": ow["s"]})
                ranking["end"] = end
                last_card_end = end
                if p.get("sfx"):
                    sfx.append({"t": ow["s"], "kind": "tick"})
                continue
            if rank == 1 and (room(s0) or s0 - last_card_end > 1.0):
                ranking = {"type": "ranking", "start": max(s0, ow["s"] - 0.15), "end": end, "label": "RANKED",
                           "items": [{"rank": 1, "text": clean(item), "t": ow["s"]}]}
                if add_card(ranking):
                    continue
                ranking = None

        nums = [(number_value(w["w"]), w) for w in sw if number_value(w["w"]) is not None]
        recall = re.search(r"\b(back|remember|start|again|earlier|kembali|tadi)\b", low) and "number" in low
        if recall and seen_numbers.get("_list") and p.get("callbacks", True):
            last_card_end = -99.0
            add_card({"type": "callback", "start": s0, "end": min(out_dur, s1 + 2.5), "label": "BACK TO THE START",
                      "items": [{"value": v, "label": l} for v, l in seen_numbers["_list"][:3]]})
            continue
        nums = [(v, w) for v, w in nums if norm(w["w"]) != "one"]
        prev = cards[-1] if cards else None
        if nums and prev and prev["type"] == "number" and s0 - prev["end"] < 3.5 and len(prev["items"]) < 3:
            for v, w in nums[: 3 - len(prev["items"])]:
                i = W.index(w)
                lab = next((W[k]["w"] for k in range(i + 1, min(i + 3, len(W))) if norm(W[k]["w"]) not in STOP), "")
                prev["items"].append({"value": v, "label": norm(lab), "t": w["s"]})
                seen_numbers.setdefault(v, w["s"])
                seen_numbers.setdefault("_list", []).append((v, norm(lab)))
                if p.get("sfx"):
                    sfx.append({"t": w["s"], "kind": "tick"})
            prev["end"] = max(prev["end"], end)
            last_card_end = prev["end"]
            continue
        if nums and room(s0, True):
            val, nw = nums[0]
            if seen_numbers.get(val) is not None:
                nums = []
        if nums and room(s0, True):
            items = []
            for v, w in nums[:3]:
                i = W.index(w)
                lab = next((W[k]["w"] for k in range(i + 1, min(i + 3, len(W))) if norm(W[k]["w"]) not in STOP), "")
                items.append({"value": v, "label": norm(lab), "t": w["s"]})
                seen_numbers.setdefault(v, w["s"])
            seen_numbers.setdefault("_list", [])
            for it in items:
                if it["value"] not in [x[0] for x in seen_numbers["_list"]]:
                    seen_numbers["_list"].append((it["value"], it["label"]))
            if add_card({"type": "number", "start": nums[0][1]["s"], "end": end, "label": "BY THE NUMBERS",
                         "items": items}):
                if p["zoom"]:
                    zooms.append({"start": nums[0][1]["s"], "end": min(end, nums[0][1]["s"] + 1.2),
                                  "amount": 1 + (p["zoom_amount"] - 1) * 0.6, "ease": "punch"})
                continue


        if text.strip().endswith("?") and room(s0) and len(sw) <= 9:
            add_card({"type": "question", "start": s0, "end": end, "label": "", "text": clean(text)})
            if p["zoom"]:
                zooms.append({"start": s0, "end": s1, "amount": 1 + (p["zoom_amount"] - 1) * 0.5, "ease": "in"})
            continue

        toks = set(low.split())
        if toks & VERSUS and room(s0) and 3 <= len(sw) <= 14:
            content = [w["w"] for w in sw if norm(w["w"]) not in STOP and norm(w["w"]) not in VERSUS]
            if len(content) >= 2:
                add_card({"type": "versus", "start": s0, "end": end, "label": "HEAD TO HEAD",
                          "left": clean(content[0]), "right": clean(content[-1])})
                continue

        # one-word emphasis: short sentence, or a single long content word
        content = sorted([w for w in sw if norm(w["w"]) not in STOP and len(norm(w["w"])) >= 4],
                         key=lambda w: -len(norm(w["w"])))
        phrase = re.sub(r"[^\w%' ]", "", " ".join(w["w"] for w in sw)).strip()
        if (len(sw) <= 3 and content and room(s0) and p.get("word_zoom", True)
                and norm_sentence(text).strip().replace("'", "") not in FILLER
                and not re.match(r"(here s|heres|here is|here are|ini|berikut)\b", low.strip())):
            add_card({"type": "word", "start": s0, "end": max(s1 + 0.5, s0 + 1.4), "label": "",
                      "text": (phrase if len(phrase) <= 12 else re.sub(r"[^\w%]", "", content[0]["w"])).upper()})
            if p["zoom"]:
                zooms.append({"start": s0, "end": s1 + 0.4, "amount": p["zoom_amount"], "ease": "punch"})
            continue

        # otherwise: do nothing. Captions carry it. Occasional gentle push-in for rhythm.
        if p["zoom"] and len(sw) >= 5 and si % max(2, 6 - p["level"] // 20) == 0:
            zooms.append({"start": s0, "end": s1, "amount": 1 + (p["zoom_amount"] - 1) * 0.35, "ease": "drift"})

    if p.get("drop_beats"):
        dropped = [c for c in cards if c["type"] in p["drop_beats"]]
        cards[:] = [c for c in cards if c["type"] not in p["drop_beats"]]
        for v in dropped:
            zooms[:] = [z for z in zooms if not (v["start"] <= z["start"] < v["end"])]
            sfx[:] = [x for x in sfx if not (v["start"] - 0.2 <= x["t"] < v["end"])]
    cards.sort(key=lambda c: c["start"])
    for c, nxt in zip(cards, cards[1:]):  # never let two cards share the screen
        if c["end"] > nxt["start"] - 0.1:
            c["end"] = round(max(c["start"] + 0.6, nxt["start"] - 0.1), 3)
            if c["end"] > nxt["start"] - 0.05:
                nxt["start"] = round(c["end"] + 0.1, 3)
    # keep at least 38% of the runtime card-free: drop the weakest beats first
    rank = {"word": 0, "question": 1, "versus": 2, "quote": 3, "ranking": 4, "number": 5, "callback": 6}
    while len(cards) > 2 and out_dur - sum(c["end"] - c["start"] for c in cards) < 0.38 * out_dur:
        victims = [c for c in cards if c["type"] in rank]
        if not victims:
            break
        v = min(victims, key=lambda c: (rank[c["type"]], -(c["end"] - c["start"])))
        cards.remove(v)
        zooms[:] = [z for z in zooms if not (v["start"] <= z["start"] < v["end"])]
        sfx[:] = [x for x in sfx if not (v["start"] - 0.2 <= x["t"] < v["end"])]
    flashes = [{"t": c["start"]} for c in cards if p.get("flash") and c["type"] in ("word", "versus", "hook")]
    edl = {
        "version": 1,
        "source_words": os.path.basename(words_path),
        "params": p,
        "theme": theme,
        "detected": detected,
        "keep": keep,
        "duration": round(out_dur, 3),
        "words": W,
        "cards": cards,
        "zooms": zooms,
        "sfx": sfx,
        "flashes": flashes,
    }
    write_json(out, edl)
    removed = dur - out_dur
    log(f"level {p['level']} ({p['tier']}): {len(cards)} cards, {len(zooms)} zooms, {len(sfx)} sfx, "
        f"cut {removed:.1f}s of pauses -> {out_dur:.1f}s. wrote {out}")


def norm_sentence(t):
    return re.sub(r"[^\w% ]", " ", t.lower())


def clean(t: str) -> str:
    return re.sub(r"\s+", " ", t.replace("{", "(").replace("}", ")").replace("\\", "/")).strip()


# --------------------------------------------------------------- ASS build
def ass_color(hexstr: str, alpha: int = 0) -> str:
    h = hexstr.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ass_time(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def rrect(w, h, r):
    r = min(r, w / 2, h / 2)
    k = r * 0.4477
    return (f"m {r} 0 l {w-r} 0 b {w-k} 0 {w} {k} {w} {r} l {w} {h-r} b {w} {h-k} {w-k} {h} {w-r} {h} "
            f"l {r} {h} b {k} {h} 0 {h-k} 0 {h-r} l 0 {r} b 0 {k} {k} 0 {r} 0")


def default_font():
    sysname = platform.system()
    if sysname == "Windows":
        return "Segoe UI Black", "Segoe UI Semibold"
    if sysname == "Darwin":
        return "Helvetica Neue", "Helvetica Neue"
    return "DejaVu Sans", "DejaVu Sans"


class Ass:
    def __init__(self, W, H, theme, font_bold, font_body):
        self.W, self.H, self.t = W, H, theme
        self.fb, self.fn = font_bold, font_body
        self.ev = []
        self.glass = []
        self.s = H / 1920.0  # scale factor against the 1080x1920 design grid

    def px(self, v):
        return round(v * self.s, 1)

    def add(self, start, end, text, style="Card", layer=1):
        if end - start < 0.03:
            return
        self.ev.append((layer, start, end, style, text))

    def header(self):
        t, s = self.t, self.s
        cap = int(t.get("caption_size", 74) * s)
        return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.W}
PlayResY: {self.H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{self.fb},{cap},{ass_color(t['caption_text'])},{ass_color(t['accent'], 255)},{ass_color(t['caption_stroke'])},{ass_color('#000000', 150)},0,0,0,0,100,100,0,0,1,{self.px(t.get('caption_border', 7))},{self.px(t.get('caption_shadow', 3))},5,0,0,0,1
Style: Card,{self.fb},{int(64*s)},{ass_color(t['card_text'])},{ass_color(t['accent'], 255)},{ass_color(t['card_bg'])},{ass_color('#000000', 200)},0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Body,{self.fn},{int(44*s)},{ass_color(t['card_text'])},{ass_color(t['accent'], 255)},{ass_color(t['card_bg'])},{ass_color('#000000', 200)},0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Shape,{self.fn},20,{ass_color(t['card_bg'])},{ass_color(t['card_bg'])},{ass_color('#000000', 255)},{ass_color('#000000', 170)},0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def dump(self, path):
        lines = [self.header()]
        for layer, a, b, st, txt in sorted(self.ev, key=lambda e: (e[1], e[0])):
            lines.append(f"Dialogue: {layer},{ass_time(a)},{ass_time(b)},{st},,0,0,0,,{txt}")
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")

    # --- primitives
    def panel(self, a, b, x, y, w, h, color=None, alpha=0, r=28, layer=1, shadow=True, anim="rise"):
        """Rounded panel with a soft drop shadow. x,y = top-left on the 1080x1920 grid."""
        c = ass_color(color or self.t["card_bg"], alpha)
        X, Y, Wd, Hd, R = self.px(x), self.px(y), self.px(w), self.px(h), self.px(r)
        dy = self.px(40)
        mv = (f"\\move({X},{Y+dy},{X},{Y},0,260)" if anim == "rise" else f"\\pos({X},{Y})")
        pop = "\\fscx92\\fscy92\\t(0,260,\\fscx100\\fscy100)" if anim == "rise" else ""
        if self.t.get("glass") and (color or self.t["card_bg"]) == self.t["card_bg"]:
            # Frosted glass: the renderer blurs the real video under this rect; ASS adds tint + hairline.
            self.glass.append({"a": a, "b": b, "x": int(X), "y": int(Y), "w": int(Wd), "h": int(Hd), "r": int(R)})
            tint = "&H" + ass_color(color or self.t["card_bg"])[4:] + "&"
            ta = int(self.t.get("glass_alpha", 150))
            self.add(a, b, f"{{\\an7\\pos({X},{Y})\\p1\\bord{self.px(2)}\\3c&HFFFFFF&\\3a&H70&\\shad0\\1c{tint}\\1a&H{ta:02X}&"
                           f"\\fad(200,180)}}{rrect(Wd, Hd, R)}", "Shape", layer + 1)
            return
        if shadow:
            self.add(a, b, f"{{\\an7{mv}\\p1\\bord0\\shad0\\blur{self.px(22)}\\1c&H000000&\\1a&HB4&"
                           f"\\fad(220,200){pop}}}{rrect(Wd, Hd + self.px(10), R)}", "Shape", layer)
        self.add(a, b, f"{{\\an7{mv}\\p1\\bord0\\shad0\\1c{c}\\fad(180,180){pop}}}{rrect(Wd, Hd, R)}",
                 "Shape", layer + 1)

    def text(self, a, b, x, y, txt, size=64, color=None, style="Card", an=5, layer=4, anim="rise", extra=""):
        c = ass_color(color or self.t["card_text"])
        X, Y = self.px(x), self.px(y)
        if anim == "rise":
            pos = f"\\move({X},{Y+self.px(30)},{X},{Y},40,300)\\fad(160,160)"
        elif anim == "drop":
            pos = f"\\move({X},{Y-self.px(40)},{X},{Y},0,240)\\fad(120,160)"
        elif anim == "zoom":
            pos = f"\\pos({X},{Y})\\fscx55\\fscy55\\blur6\\t(0,220,\\fscx108\\fscy108\\blur0)\\t(220,360,\\fscx100\\fscy100)\\fad(60,200)"
        else:
            pos = f"\\pos({X},{Y})\\fad(140,160)"
        self.add(a, b, f"{{\\an{an}{pos}\\fs{int(size*self.s)}\\1c{c}\\bord0\\shad0{extra}}}{txt}", style, layer)

    def label(self, a, b, x, y, txt, an=7):
        self.text(a, b, x, y, txt, 30, self.t["muted"], "Body", an, 4, "rise", "\\fsp4")


def caption_chunks(words, maxw, maxdur):
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= maxw or w["e"] - cur[0]["s"] > maxdur or w["s"] - cur[-1]["e"] > 0.45
                    or re.search(r"[.?!,]$", cur[-1]["w"])):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


CAPTION_MODES = ["plain", "clean_accent", "chunk", "highlight", "pop", "kinetic", "sweep", "boxed", "bounce", "stack"]


def is_keyword(w):
    n = norm(w)
    return (n not in STOP and len(n) >= 6) or number_value(w) is not None


def build_ass(edl: dict, W: int, H: int, path: str, font_bold: str, font_body: str):
    t, p = edl["theme"], edl["params"]
    A = Ass(W, H, t, font_bold, font_body)
    dur = edl["duration"]
    cap_y = t.get("caption_y", 1390)
    mode = p["captions"]

    # ---- captions
    chunks = caption_chunks(edl["words"], p["caption_words"], 1.6)
    acc = ass_color(t["accent"])
    base = ass_color(t["caption_text"])
    X, Y = A.px(540), A.px(cap_y)
    for ch in chunks:
        c0 = ch[0]["s"]
        c1 = max(ch[-1]["e"], c0 + 0.35)
        nxt = next((x for x in chunks if x[0]["s"] > ch[-1]["s"]), None)
        c1 = min(c1 + 0.25, nxt[0]["s"]) if nxt else c1 + 0.4
        raw = [clean(w["w"]) for w in ch]
        if t.get("caption_upper"):
            raw = [r.upper() for r in raw]
        if mode == "plain":
            A.add(c0, c1, f"{{\\pos({X},{Y})\\fad(80,80)}}{' '.join(raw)}", "Caption", 10)
            continue
        if mode == "clean_accent":  # calm, but keywords carry the accent so it is never flat
            txt = " ".join(f"{{\\1c{acc}}}{r}{{\\1c{base}}}" if is_keyword(w["w"]) else r for r, w in zip(raw, ch))
            A.add(c0, c1, f"{{\\pos({X},{Y})\\fad(90,90)\\fscx96\\fscy96\\t(0,120,\\fscx100\\fscy100)}}{txt}",
                  "Caption", 10)
            continue
        if mode == "sweep":  # karaoke fill: accent sweeps through each word as it is spoken
            ks = []
            for i, w in enumerate(ch):
                end_i = ch[i + 1]["s"] if i + 1 < len(ch) else w["e"]
                ks.append(f"{{\\kf{max(1, int(round((end_i - w['s']) * 100)))}}}{raw[i]}")
            lead = max(0, int(round((ch[0]["s"] - c0) * 100)))
            A.add(c0, c1, f"{{\\pos({X},{Y})\\1c{acc}\\2c{base}\\fad(60,80)\\k{lead}}}" + " ".join(ks), "Caption", 10)
            continue
        if mode == "boxed":  # accent pill slides under the active word
            fs = t.get("caption_size", 74)
            cw = [max(1, len(r)) * fs * 0.5 for r in raw]
            gap = fs * 0.3
            total = sum(cw) + gap * (len(cw) - 1)
            x0 = 540 - total / 2
            for i, w in enumerate(ch):
                a = w["s"] if i else c0
                b = ch[i + 1]["s"] if i + 1 < len(ch) else c1
                bx = x0 + sum(cw[:i]) + gap * i
                pw, ph = cw[i] + fs * 0.4, fs * 1.25
                A.add(a, b, f"{{\\an7\\pos({A.px(bx - fs * 0.2)},{A.px(cap_y - ph / 2)})\\p1\\bord0\\shad0\\1c{acc}"
                            f"\\fscx85\\fscy85\\t(0,80,\\fscx100\\fscy100)}}{rrect(A.px(pw), A.px(ph), A.px(fs * 0.3))}",
                      "Shape", 9)
                parts = [f"{{\\1c{ass_color(t.get('on_accent', '#FFFFFF'))}\\bord0}}{r}{{\\1c{base}\\bord{int(7 * A.s)}}}"
                         if j == i else r for j, r in enumerate(raw)]
                A.add(a, b, f"{{\\pos({X},{Y})}}" + " ".join(parts), "Caption", 10)
            continue
        if mode == "bounce":  # each word drops in from above with overshoot
            for i, w in enumerate(ch):
                a = w["s"] if i else c0
                b = ch[i + 1]["s"] if i + 1 < len(ch) else c1
                parts = []
                for j, r in enumerate(raw):
                    if j < i:
                        parts.append(r)
                    elif j == i:
                        parts.append(f"{{\\1c{acc if is_keyword(ch[j]['w']) else base}\\frz-6\\fscy70"
                                     f"\\t(0,90,\\frz3\\fscy115)\\t(90,170,\\frz0\\fscy100)}}{r}{{\\1c{base}\\frz0}}")
                    else:
                        parts.append(f"{{\\alpha&HFF&}}{r}{{\\alpha&H00&}}")
                A.add(a, b, f"{{\\move({X},{Y - A.px(30) if not i else Y},{X},{Y},0,120)}}" + " ".join(parts), "Caption", 10)
            continue
        if mode == "stack":  # small lead-in line, the keyword huge underneath
            kws = [j for j, w in enumerate(ch) if is_keyword(w["w"])]
            k = max(kws, key=lambda j: len(raw[j])) if kws else max(range(len(raw)), key=lambda j: len(raw[j]))
            small = " ".join(r for j, r in enumerate(raw) if j != k) or " "
            A.add(c0, c1, f"{{\\pos({X},{Y - A.px(70)})\\fscx70\\fscy70\\fad(80,80)}}{small}", "Caption", 10)
            ks = ch[k]["s"]
            A.add(max(c0, ks - 0.05), c1, f"{{\\pos({X},{Y + A.px(20)})\\1c{acc}\\fscx60\\fscy60"
                  f"\\t(0,120,\\fscx135\\fscy135)\\t(120,220,\\fscx125\\fscy125)}}{raw[k].upper()}", "Caption", 11)
            continue
        if mode == "chunk":
            A.add(c0, c1, f"{{\\pos({X},{Y})\\fscx88\\fscy88\\t(0,90,\\fscx100\\fscy100)}}{' '.join(raw)}",
                  "Caption", 10)
            continue
        for i, w in enumerate(ch):
            a = w["s"] if i else c0
            b = ch[i + 1]["s"] if i + 1 < len(ch) else c1
            parts = []
            for j, r in enumerate(raw):
                if mode == "highlight":
                    parts.append(f"{{\\1c{acc}}}{r}{{\\1c{base}}}" if j == i else r)
                else:  # pop / kinetic: words appear as spoken, current word pops in accent
                    if j < i:
                        parts.append(f"{{\\1c{base}\\alpha&H00&}}{r}")
                    elif j == i:
                        kw = is_keyword(ch[j]["w"])
                        big = 118 if kw else 108
                        col = acc if (kw or mode == "pop") else base
                        parts.append(f"{{\\alpha&H00&\\1c{col}\\fscx{big}\\fscy{big}"
                                     f"\\t(0,110,\\fscx100\\fscy100)}}{r}{{\\fscx100\\fscy100}}")
                    else:
                        parts.append(f"{{\\alpha&HFF&}}{r}")
            pre = "" if i else "\\fscx90\\fscy90\\t(0,90,\\fscx100\\fscy100)"
            A.add(a, b, f"{{\\pos({X},{Y}){pre}}}" + " ".join(parts), "Caption", 10)
        if mode == "kinetic":
            shown_until = -1.0
            for wi, w in enumerate(ch):
                if is_keyword(w["w"]) and len(norm(w["w"])) >= 7 and w["s"] >= shown_until:
                    nxt_s = ch[wi + 1]["s"] if wi + 1 < len(ch) else c1
                    shown_until = min(w["e"] + 0.5, dur, max(nxt_s, w["e"] + 0.2))
                    A.add(w["s"], shown_until,
                          f"{{\\pos({X},{A.px(cap_y-150)})\\fs{int(40*A.s)}\\1c{acc}\\bord0\\shad0\\fsp6"
                          f"\\fad(80,200)}}{clean(w['w']).upper()}", "Body", 9)

    # ---- progress bar
    if p.get("progress"):
        bw = A.px(1080)
        A.add(0, dur, f"{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c{acc}\\clip(0,0,0,{A.px(10)})"
                      f"\\t(0,{int(dur*1000)},\\clip(0,0,{bw},{A.px(10)}))}}{rrect(bw, A.px(10), 0)}", "Shape", 20)

    # ---- cards
    top = t.get("card_y", 230)
    for c in edl["cards"]:
        a, b = c["start"], c["end"]
        ty = c["type"]
        if ty == "hook":
            words_ = c["text"].split()
            lines, cur = [], []
            for w in words_:
                cur.append(w)
                if len(" ".join(cur)) > 18:
                    lines.append(cur)
                    cur = []
            if cur:
                lines.append(cur)
            lines = lines[:3]
            h = 60 + 112 * len(lines)
            A.panel(a, b, 70, top, 940, h, t["card_bg"], 0)
            k = 0
            for li, ln in enumerate(lines):
                txt = ""
                for wi, w in enumerate(ln):
                    d = 70 * k
                    col = acc if is_keyword(w) else ass_color(t["card_text"])
                    txt += f"{{\\alpha&HFF&\\1c{col}\\t({d},{d+140},\\alpha&H00&)}}{w} "
                    k += 1
                A.add(a, b, f"{{\\an4\\pos({A.px(120)},{A.px(top+86+li*112)})\\fs{int(84*A.s)}\\bord0\\shad0"
                            f"\\fad(0,180)}}{txt.strip()}", "Card", 5)
        elif ty in ("number", "callback"):
            items = c["items"][:3]
            n = len(items)
            A.panel(a, b, 70, top, 940, 330, t["card_bg"], 0)
            A.label(a, b, 120, top + 36, c["label"])
            for i, it in enumerate(items):
                cx = 540 if n == 1 else 250 + i * (580 / max(1, n - 1))
                st = max(a, it.get("t", a) if ty == "number" else a + 0.25 * i)
                val = it["value"]
                digits = re.match(r"\d+", val)
                if digits and int(digits.group(0)) > 3 and ty == "number":
                    target = int(digits.group(0))
                    steps = 10
                    for sidx in range(steps):
                        v = round(target * (sidx + 1) / steps)
                        s_a = st + sidx * 0.045
                        s_b = st + (sidx + 1) * 0.045 if sidx < steps - 1 else b
                        A.add(s_a, s_b, f"{{\\an5\\pos({A.px(cx)},{A.px(top+170)})\\fs{int(150*A.s)}\\1c{acc}"
                                        f"\\bord0\\shad0}}{v}{val[len(digits.group(0)):]}", "Card", 6)
                else:
                    A.text(st, b, cx, top + 170, val, 150, t["accent"], "Card", 5, 6, "zoom")
                if it.get("label"):
                    A.text(st, b, cx, top + 270, it["label"], 36, t["muted"], "Body", 5, 6, "rise")
        elif ty == "ranking":
            items = c["items"][:5]
            h = 90 + 96 * len(items)
            A.panel(a, b, 70, top, 940, h, t["card_bg"], 0)
            A.label(a, b, 120, top + 34, c["label"])
            for i, it in enumerate(items):
                st = max(a, it["t"])
                y = top + 100 + i * 96
                full = 700 - i * 150
                fade = [0, 80, 150, 190, 210][i]
                A.text(st, b, 125, y + 30, str(it["rank"]), 56, t["accent"], "Card", 4, 6, "rise")
                bar = A.px(max(160, full))
                A.add(st, b, f"{{\\an7\\pos({A.px(190)},{A.px(y)})\\p1\\bord0\\shad0\\1c{acc}\\1a&H{fade:02X}&"
                             f"\\clip(0,0,{A.px(190)},{A.H})\\t(0,420,\\clip(0,0,{A.px(190)+bar},{A.H}))}}"
                             f"{rrect(bar, A.px(62), A.px(14))}", "Shape", 5)
                A.text(st + 0.15, b, 215, y + 31, it["text"], 38, t["on_accent"] if i < 2 else t["card_text"],
                       "Body", 4, 7, "none")
        elif ty == "quote":
            words_ = c["text"].split()
            lines, cur = [], []
            for w in words_:
                cur.append(w)
                if len(" ".join(cur)) > 24:
                    lines.append(" ".join(cur))
                    cur = []
            if cur:
                lines.append(" ".join(cur))
            lines = lines[:4]
            h = 150 + 70 * len(lines)
            A.panel(a, b, 70, top, 940, h, t["card_bg"], 0)
            A.text(a, b, 120, top + 70, "\u201C", 150, t["accent"], "Card", 4, 6, "drop")
            total = max(0.6, min(b - a - 0.6, len(c["text"]) * 0.03))
            per = total / max(1, len(c["text"]))
            for li, ln in enumerate(lines):
                kt = "".join(f"{{\\kf{max(1,int(per*100))}}}{ch}" for ch in ln)
                delay = sum(len(x) for x in lines[:li]) * per
                A.add(a + 0.2 + delay, b, f"{{\\an4\\pos({A.px(125)},{A.px(top+150+li*70)})\\fs{int(50*A.s)}"
                                          f"\\bord0\\shad0\\2a&HFF&\\fad(0,160)}}{kt}", "Body", 6)
        elif ty == "question":
            A.panel(a, b, 140, top + 40, 800, 150, t["accent"], 0, 75)
            A.text(a, b, 540, top + 115, c["text"][:30], 58, t["on_accent"], "Card", 5, 6, "zoom")
        elif ty == "versus":
            y = top + 60
            A.panel(a, b, 70, y, 400, 150, t["card_bg"], 0, 36)
            A.panel(a + 0.1, b, 610, y, 400, 150, t["card_bg"], 0, 36)
            A.text(a, b, 270, y + 75, c["left"][:12], 58, t["card_text"], "Card", 5, 6, "rise")
            A.text(a + 0.1, b, 810, y + 75, c["right"][:12], 58, t["card_text"], "Card", 5, 6, "rise")
            A.add(a + 0.2, b, f"{{\\an5\\pos({A.px(540)},{A.px(y+75)})\\p1\\bord0\\shad0\\1c{acc}\\fscx0\\fscy0"
                              f"\\t(0,200,\\fscx115\\fscy115)\\t(200,300,\\fscx100\\fscy100)\\fad(0,160)}}"
                              f"{rrect(A.px(120), A.px(120), A.px(60))}", "Shape", 7)
            A.text(a + 0.25, b, 540, y + 75, "VS", 50, t["on_accent"], "Card", 5, 8, "zoom")
        elif ty == "word":
            A.add(a, b, f"{{\\an5\\pos({A.px(540)},{A.px(top+160)})\\fs{int(150*A.s)}\\1c{acc}"
                        f"\\3c{ass_color(t['caption_stroke'])}\\bord{A.px(10)}\\shad0\\fsp{A.px(4)}"
                        f"\\fscx40\\fscy40\\blur8\\t(0,200,\\fscx112\\fscy112\\blur0)\\t(200,340,\\fscx100\\fscy100)"
                        f"\\fad(40,220)}}{c['text'][:14]}", "Card", 6)
            A.add(a + 0.12, b, f"{{\\an5\\pos({A.px(540)},{A.px(top+262)})\\p1\\bord0\\shad0\\1c{acc}"
                               f"\\fscx0\\t(0,300,\\fscx100)\\fad(0,200)}}{rrect(A.px(420), A.px(10), A.px(5))}",
                  "Shape", 6)
        elif ty == "cta":
            y = top + 40  # platform UI covers the bottom ~400 px (Reels/TikTok safe zones, 2026)
            A.panel(a, b, 190, y, 700, 130, t["accent"], 0, 65)
            A.text(a + 0.1, b, 540, y + 65, t.get("cta_text", "Follow for part two"), 50, t["on_accent"],
                   "Card", 5, 6, "rise")

    # ---- flashes
    for f in edl.get("flashes", []):
        A.add(f["t"], f["t"] + 0.18, f"{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\1c&HFFFFFF&\\1a&H60&"
                                     f"\\t(0,180,\\1a&HFF&)}}{rrect(W, H, 0)}", "Shape", 30)
    A.dump(path)
    return len(A.ev), A.glass


# ------------------------------------------------------------------ audio
def synth_sfx(edl: dict, path: str, sr: int = 48000):
    n = int((edl["duration"] + 1) * sr)
    buf = array("f", bytes(4 * n))
    for ev in edl.get("sfx", []):
        start = int(ev["t"] * sr)
        kind = ev["kind"]
        if kind == "pop":
            L = int(0.09 * sr)
            for i in range(L):
                tt = i / sr
                env = math.exp(-tt * 55)
                f = 900 - 5000 * tt
                v = 0.55 * env * math.sin(2 * math.pi * f * tt)
                if start + i < n:
                    buf[start + i] += v
        elif kind == "tick":
            L = int(0.04 * sr)
            for i in range(L):
                tt = i / sr
                v = 0.4 * math.exp(-tt * 120) * math.sin(2 * math.pi * 1800 * tt)
                if start + i < n:
                    buf[start + i] += v
        else:  # whoosh: filtered noise swell
            L = int(0.32 * sr)
            seed, lp = 12345, 0.0
            s0 = max(0, start - int(0.18 * sr))
            for i in range(L):
                seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
                x = seed / 0x7FFFFFFF * 2 - 1
                ph = i / L
                a = 0.02 + 0.3 * ph
                lp += a * (x - lp)
                env = math.sin(math.pi * ph) ** 2
                if s0 + i < n:
                    buf[s0 + i] += 0.5 * env * lp
    pcm = array("h", (int(clamp(v, -1, 1) * 32000) for v in buf))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def synth_music(out: str, seconds: float, bpm: int = 96, mood: str = "bright"):
    """License-free bed: soft chord pad + sub pulse + hat ticks, rendered by ffmpeg aevalsrc."""
    need("ffmpeg")
    beat = 60.0 / bpm
    bar = beat * 4
    prog = {"bright": [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)],
            "moody": [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 311.13, 392.0), (196.0, 233.08, 293.66)]}[mood]
    idx = f"mod(floor(t/{bar*2:.4f}),4)"

    def pick(k):
        return "+".join(f"eq({idx},{i})*{c[k]}" for i, c in enumerate(prog))

    pad = "+".join(f"0.045*sin(2*PI*({pick(k)})*t)" for k in range(3))
    kick = f"0.22*sin(2*PI*52*t)*exp(-9*mod(t,{beat:.4f}))"
    hat = f"0.018*(random(0)*2-1)*exp(-60*mod(t+{beat/2:.4f},{beat:.4f}))"
    swell = f"(0.75+0.25*sin(2*PI*t/{bar*2:.4f}))"
    expr = f"({pad})*{swell}+{kick}+{hat}"
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
         f"aevalsrc='{expr}':s=44100:d={seconds+2:.2f}",
         "-af", f"lowpass=f=7000,afade=t=in:d=1.5,afade=t=out:st={max(0, seconds-1.5):.2f}:d=1.5,aformat=channel_layouts=stereo",
         out])
    log(f"wrote {out}")


def music_templates(genre: str | None = None):
    """Every template id, optionally only those that match a genre."""
    m = read_json(PRESETS / "music.json")
    g = m["genre_match"].get(genre) if genre else None
    moods = g["moods"] if g else list(m["moods"])
    drums = g["drums"] if g else list(m["drums"])
    timbres = g["timbres"] if g else list(m["timbres"])
    energy = g["energy"] if g else list(m["energy"])
    return [f"{mo}.{k}.{d}.{t}.{e}" for mo in moods for k in m["keys"] for d in drums for t in timbres for e in energy]


def pick_music(words, genre: str | None, style: str, seed: int) -> dict:
    """Choose a template that fits the genre and the speaker's pace (words per minute)."""
    m = read_json(PRESETS / "music.json")
    dur = max(1.0, words[-1]["e"] - words[0]["s"]) if words else 60.0
    wpm = len(words) * 60.0 / dur
    energy = "low" if wpm < 130 else "mid" if wpm < 170 else "high"
    g = m["genre_match"].get(genre)
    if g:
        moods, drums, timbres = g["moods"], g["drums"], g["timbres"]
        if energy not in g["energy"]:
            energy = g["energy"][0] if energy == "low" else g["energy"][-1]
    else:
        moods, drums, timbres = [m["style_default"].get(style, "bright_pop")], ["soft_pulse", "lofi"], ["warm"]
    tid = ".".join([moods[seed % len(moods)], m["keys"][(seed // 3) % 12], drums[(seed // 7) % len(drums)],
                    timbres[(seed // 11) % len(timbres)], energy])
    return {"template": tid, "wpm": round(wpm), "reason": f"genre {genre or 'none'}, style {style}, "
            f"{round(wpm)} words/min -> {energy} energy"}


def synth_template(out: str, seconds: float, tid: str):
    """Render one music template (mood.key.drums.timbre.energy) with ffmpeg aevalsrc. License-free."""
    need("ffmpeg")
    m = read_json(PRESETS / "music.json")
    try:
        mood, key, drums, timbre, energy = tid.split(".")
        md, dr, en = m["moods"][mood], m["drums"][drums], m["energy"][energy]
        ki = m["keys"].index(key)
        assert timbre in m["timbres"]
    except (ValueError, KeyError, AssertionError):
        die(f"bad music template {tid}; list them with: splicecraft.py music list")
    bpm = md["bpm"] * en
    beat = 60.0 / bpm
    step = beat / 4
    bar = beat * 4
    root = 196.0 * 2 ** (ki / 12.0)
    chords = md["chords"]
    idx = f"mod(floor(t/{bar * 2:.4f}),{len(chords)})"

    def freq(n):
        return "(" + "+".join(f"eq({idx},{i})*{root * 2 ** (c[n] / 12.0):.3f}" for i, c in enumerate(chords)) + ")"

    def voice(f):
        if timbre == "sine":
            return f"sin(2*PI*{f}*t)"
        if timbre == "warm":
            return f"(sin(2*PI*{f}*t)+0.45*sin(4*PI*{f}*t)+0.2*sin(6*PI*{f}*t))/1.4"
        if timbre == "organ":
            return f"(sin(2*PI*{f}*t)+0.4*sin(4*PI*{f}*t)+0.3*sin(8*PI*{f}*t))/1.5"
        return f"(sin(2*PI*{f}*t)+0.3*sin(4*PI*{f}*t))*(0.35+exp(-4*mod(t,{beat:.4f})))"

    pad = "+".join(f"0.04*{voice(freq(n))}" for n in range(3))
    bass = f"0.07*sin(2*PI*{freq(0)}/2*t)*(0.5+0.5*exp(-3*mod(t,{beat * 2:.4f})))"
    st = f"mod(floor(t/{step:.5f}),16)"

    def gate(pattern):
        hits = [i for i, ch in enumerate(pattern) if ch == "x"]
        return "(" + "+".join(f"eq({st},{i})" for i in hits) + ")" if hits else "0"

    env = f"mod(t,{step:.5f})"
    kick = f"0.24*{gate(dr['kick'])}*sin(2*PI*(48+60*exp(-30*{env}))*t)*exp(-11*{env})"
    hat = f"0.02*{gate(dr['hat'])}*(random(0)*2-1)*exp(-70*{env})"
    clap = f"0.05*{gate(dr['clap'])}*(random(1)*2-1)*exp(-22*{env})"
    swell = f"(0.8+0.2*sin(2*PI*t/{bar * 2:.4f}))"
    expr = f"({pad})*{swell}+{bass}+{kick}+{hat}+{clap}"
    # synthesize one full chord cycle once (per-sample expressions are slow), then loop it to length
    cycle = bar * 2 * len(chords)
    loop = str(Path(out).with_suffix("")) + ".cycle.wav"
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=32000:d={min(cycle, seconds + 2):.4f}",
         "-c:a", "pcm_s16le", loop])
    run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", loop, "-t", f"{seconds + 1:.2f}",
         "-af", f"aresample=44100,highpass=f=30,lowpass=f=9000,afade=t=in:d=1.2,"
                f"afade=t=out:st={max(0, seconds - 1.5):.2f}:d=1.5,aformat=channel_layouts=stereo,loudnorm=I=-20:TP=-2",
         out])
    os.remove(loop)
    log(f"wrote {out} ({tid}, {bpm:.0f} bpm)")


BEAT_SHARE = {"hook": 0.09, "cta": 0.07, "closing": 0.06, "verdict": 0.1, "solution_demo": 0.18, "proof": 0.12}
TITLE_PATTERNS = ["I tried {topic} so you don't have to", "{topic}: what nobody tells you",
                  "{topic} in {seconds} seconds", "Stop doing this with {topic}", "The {topic} mistake costing you {cost}",
                  "{a} vs {b}: which one actually wins", "How I {result} with {topic}"]
TITLE_PATTERNS_ID = ["Aku coba {topic} biar kamu nggak perlu", "{topic}: yang jarang orang bilang", "{topic} dalam {seconds} detik",
                     "Stop lakukan ini soal {topic}", "Kesalahan {topic} yang bikin rugi {cost}", "{a} vs {b}: mana yang menang"]


def script(topic: str, genre: str, seconds: int, framework: str | None, hook: str | None, audience: str,
           language: str, out: str | None, brief: str | None = None):
    """Write a timed script skeleton: hooks, beats with word budgets, titles, description, hashtags, edit plan."""
    c = read_json(PRESETS / "content.json")
    gp = read_json(PRESETS / "genres.json")["genres"]
    if genre not in c["genre_scripts"]:
        die(f"unknown genre {genre}; choose from {', '.join(c['genre_scripts'])}")
    gs = c["genre_scripts"][genre]
    fw_by = {f["name"].lower(): f for f in c["frameworks"]}
    hk_by = {h["name"].lower(): h for h in c["hooks"]}
    bf = load_brief(brief)
    eff = brief_effects(bf) if bf else None
    if eff and eff["frameworks"] and not framework:
        framework = eff["frameworks"][0]
    beats_extra = []
    if bf.get("market") in ("investor", "hackathon", "b2b") and bf.get("tam"):
        beats_extra = ["market_size"]
    fw = fw_by.get((framework or gs["frameworks"][0]).lower()) or die(f"unknown framework {framework}")
    hook_names = [hook] if hook else gs["hooks"][:3]
    hooks = [hk_by.get(h.lower()) or die(f"unknown hook {h}") for h in hook_names]
    beats = list(gs["beats"])
    if beats_extra:
        beats.insert(max(1, len(beats) - 3), "market_size")
    wps = 2.6 if language.startswith("en") else 2.3
    rest = [b for b in beats if b not in BEAT_SHARE]
    fixed = sum(BEAT_SHARE.get(b, 0) for b in beats)
    each = max(0.05, (1 - fixed) / max(1, len(rest)))
    t, rows = 0.0, []
    for b in beats:
        d = seconds * BEAT_SHARE.get(b, each)
        rows.append((b, t, t + d, max(3, int(d * wps))))
        t += d
    g = gp[genre]
    L = [f"# Script: {topic}", "",
         f"- Genre: **{genre}** ({g['label']}) · length {seconds} s · audience: {audience} · language: {language}",
         f"- Structure: **{fw['name']}** ({' > '.join(fw['steps'])})",
         f"- Edit plan: `--genre {genre} --style auto` -> style {g['style']}, captions {', '.join(g.get('caption_modes', []))}",
         f"- Speak about {wps} words per second: {int(seconds * wps)} words total. Every line below has its budget.", "",
         ]
    if eff:
        r = brief_report(bf)
        L += ["", "## Brief", ""] + [f"- {w}" for w in eff["why"]] + [f"- {c}" for c in r["checks"]]
        if r.get("revenue_math"):
            m = r["revenue_math"]
            L.append(f"- Revenue math: {m['buyers_needed']} buyers -> about {m['views_needed']:,} views with "
                     f"assumptions {m['assumptions']} ({m['warning']})")
        L += [f"- Compliance: {c}" for c in eff["compliance"]]
        if bf.get("tam"):
            L.append(f"- Market beat: say TAM {bf['tam']:,}, SAM {bf.get('sam', 0):,}, SOM {bf.get('som', 0):,} "
                     f"({bf.get('market_unit', 'units')}); each number becomes a count-up card")
    L += ["", "## Hook options (pick one, film all three if you can and keep the best)", ""]
    for h in hooks:
        warn = " **risky: only with a claim you can prove**" if h["risky"] else ""
        tpl = h.get("template") or "(write one line using this technique)"
        L.append(f"- **{h['name']}** ({h['category']}){warn}: `{tpl}`")
    L += ["", "## Beats", "", "| # | Time | Beat | Words | What to say | Your line |", "|---|---|---|---|---|---|"]
    for i, (b, a, e, n) in enumerate(rows, 1):
        L.append(f"| {i} | {a:.0f}-{e:.0f} s | {b} | ~{n} | {c['beat_guide'].get(b, '')} | |")
    L += ["", "## Retention rules for this script", "",
          "- The hook is the first words spoken. Cut any greeting.",
          "- Say a number, name, or visual every 3 to 5 seconds (the planner turns them into cards).",
          "- Put one open loop in the first 5 seconds and close it before the CTA.",
          "- Short sentences. One idea per sentence. A 1-3 word sentence becomes a giant word hit.",
          "- The closing line calls back to the hook, so a replay feels like a loop.",
          "- One CTA only. Say it, and the planner shows it.", "",
          "## Title options", ""]
    patterns = TITLE_PATTERNS_ID if language.startswith("id") else TITLE_PATTERNS
    fill = {"topic": topic, "seconds": seconds, "cost": "jam" if language.startswith("id") else "hours", "a": "Option A", "b": "Option B", "result": "got results"}
    L += [f"- {pt.format(**fill)}" for pt in patterns[:6]]
    tag = re.sub(r"[^\w]", "", topic.title())[:28]
    L += ["", "## Description", "",
          f"Line 1 (shows before 'more'): the hook as a sentence plus the payoff.",
          "Line 2: what the viewer gets, one concrete detail.",
          f"Line 3: the CTA ({g['cta_text']}).",
          f"Line 4: 3 to 5 hashtags: one broad, two niche, one branded. Example: #{tag} #{genre.split('_')[0]} #fyp", "",
          "## After filming", "",
          "```bash",
          "python splicecraft.py auto take.mp4 -d work --level 60 --style auto --genre " + genre + " --size 1080x1920",
          "```"]
    text = "\n".join(L) + "\n"
    if out:
        Path(out).write_text(text, encoding="utf-8")
        log(f"wrote {out}")
    else:
        print(text)


PITCH_REASONS = {
    "fix_wrong_sample_rate": 2.0,   # source was recorded/played at the wrong rate; semitones set from the measured ratio
    "anonymize_speaker": 5.0,       # the user asked to disguise a voice (whistleblower, minor, privacy)
    "character_effect": 12.0,       # an explicit comedic or character voice the user asked for, on purpose
    "match_music_key": 1.0,         # a sung or hummed line that must sit in the music's key
}


def voice_pitch_filter(edl: dict) -> str:
    """Voice pitch is never changed unless params.voice names an allowed reason. See references/audio.md."""
    v = edl.get("params", {}).get("voice") or {}
    st = float(v.get("pitch_semitones", 0) or 0)
    if st == 0:
        return ""
    reason = v.get("reason")
    if reason not in PITCH_REASONS:
        die(f"voice pitch change of {st} semitones refused: params.voice.reason must be one of "
            f"{', '.join(PITCH_REASONS)} (see references/audio.md, 'Voice pitch')")
    if abs(st) > PITCH_REASONS[reason]:
        die(f"voice pitch {st} semitones exceeds the {PITCH_REASONS[reason]} limit for {reason}")
    r = 2 ** (st / 12.0)
    log(f"voice pitch {st:+.2f} semitones ({reason}); tempo kept")
    return f"asetrate={48000 * r:.1f},aresample=48000,atempo={1 / r:.5f},"


# ------------------------------------------------------------------ render
GRADES = {
    "clean": "eq=contrast={c}:saturation={s}:gamma=1.0",
    "cinematic": "eq=contrast={c}:saturation={s2},colorbalance=rs={rs}:bs={bs}:rh={rh}:bh={bh},"
                 "curves=all='0/0.03 0.25/0.22 0.75/0.8 1/0.97',vignette=angle=PI/5",
    "punchy": "eq=contrast={c2}:saturation={s3}:brightness=0.01,unsharp=5:5:0.6",
    "warm": "eq=contrast={c}:saturation={s},colortemperature=temperature={temp}",
    "mono": "hue=s=0,eq=contrast={c2},vignette=angle=PI/5",
    "none": "null",
}


def grade_filter(name: str, k: float) -> str:
    g = GRADES.get(name, GRADES["clean"])
    return g.format(c=1 + 0.08 * k, c2=1 + 0.18 * k, s=1 + 0.1 * k, s2=1 - 0.05 * k, s3=1 + 0.3 * k,
                    rs=0.06 * k, bs=-0.06 * k, rh=-0.04 * k, bh=0.06 * k, temp=int(6500 - 1200 * k))


def zoom_expr(zooms, fps):
    if not zooms:
        return "1"
    terms = []
    for z in zooms:
        a, b, amt = z["start"], z["end"], z["amount"] - 1
        if b - a < 0.2 or amt <= 0.001:
            continue
        if z["ease"] == "punch":
            terms.append(f"between(t,{a:.3f},{b:.3f})*{amt:.4f}*min(1,(t-{a:.3f})/0.12)*min(1,({b:.3f}-t)/0.18)")
        elif z["ease"] == "drift":
            terms.append(f"between(t,{a:.3f},{b:.3f})*{amt:.4f}*sin(PI*(t-{a:.3f})/{b-a:.3f})")
        else:
            terms.append(f"between(t,{a:.3f},{b:.3f})*{amt:.4f}*(1-pow(1-min(1,(t-{a:.3f})/{max(0.3,b-a):.3f}),3))")
    return "1+" + "+".join(terms) if terms else "1"


def ffpath(p: str) -> str:
    """Escape a path for use inside an ffmpeg filter argument."""
    p = str(Path(p).resolve()).replace("\\", "/")
    return p.replace(":", "\\:").replace("'", "\\'")


def render(src: str, edl_path: str, out: str, size: str | None, fps: int | None, music: str | None,
           music_db: float, key: str | None, bg: str | None, lut: str | None, grade: str | None,
           font_bold: str | None, font_body: str | None, fontsdir: str | None, crf: int, preset: str):
    need("ffmpeg")
    edl = read_json(edl_path)
    info = probe(src)
    p, theme = edl["params"], edl["theme"]
    if size:
        W, H = (int(x) for x in size.lower().split("x"))
    else:
        W, H = (1080, 1920) if info["orientation"] == "vertical" else (1920, 1080)
    fps = fps or int(min(60, round(info["fps"])))
    work = Path(tempfile.mkdtemp(prefix="splicecraft_"))
    fb, fn = default_font()
    ass_path = work / "overlay.ass"
    n_ev, glass = build_ass(edl, W, H, str(ass_path), font_bold or fb, font_body or fn)
    log(f"overlay: {n_ev} subtitle/graphic events")

    inputs = ["-i", src]
    keep = edl["keep"]
    sel = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in keep)
    fc = []
    fc.append(f"[0:v]select='{sel}',setpts=N/FRAME_RATE/TB,fps={fps},"
              f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[base]")
    vlabel = "base"
    idx = 1
    if key:
        color = {"green": "0x00FF00", "blue": "0x0000FF"}.get(key, key)
        if bg and Path(bg).exists():
            if bg.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                inputs += ["-loop", "1", "-i", bg]
            else:
                inputs += ["-stream_loop", "-1", "-i", bg]
            fc.append(f"[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},setsar=1[bgv]")
            idx += 1
        else:
            c1, c2 = theme.get("bg_a", "#0f1b2d"), theme.get("bg_b", "#274060")
            inputs += ["-f", "lavfi", "-i",
                       f"gradients=s={W}x{H}:c0={c1.replace('#','0x')}:c1={c2.replace('#','0x')}:"
                       f"x0=0:y0=0:x1={W}:y1={H}:speed=0.008:r={fps}"]
            fc.append(f"[{idx}:v]format=yuv420p,setsar=1[bgv]")
            idx += 1
        fc.append(f"[{vlabel}]format=yuva420p,chromakey={color}:0.16:0.08,despill=type={'green' if key!='blue' else 'blue'}[fg]")
        fc.append("[bgv][fg]overlay=shortest=1:format=auto[keyed]")
        vlabel = "keyed"
    k = p["grade_strength"]
    gname = grade or theme.get("grade", "clean")
    chain = grade_filter(gname, k)
    if lut:
        chain += f",lut3d=file='{ffpath(lut)}'"
    if gname in ("cinematic", "mono") and p["level"] >= 61:
        chain += ",noise=alls=6:allf=t"
    pulses = [c for c in edl["cards"] if c["type"] in ("word", "question") and p["level"] >= 41]
    for c in pulses:  # warm color pulse on payoff beats
        chain += (f",colortemperature=temperature={int(6500 - 1500 * k)}:mix=1:"
                  f"enable='between(t,{c['start']:.3f},{min(c['end'], c['start'] + 1.2):.3f})'")
    fc.append(f"[{vlabel}]{chain}[graded]")
    z = zoom_expr(edl["zooms"], fps)
    fc.append(f"[graded]scale=w='trunc({W}*({z})/2)*2':h=-2:eval=frame,crop={W}:{H},setsar=1[zoomed]")
    sub = f"subtitles=filename='{ffpath(str(ass_path))}'"
    if fontsdir:
        sub += f":fontsdir='{ffpath(fontsdir)}'"
    last = "zoomed"
    if glass:
        fc.append(f"[zoomed]split=2[zmain][zblur0]")
        fc.append(f"[zblur0]gblur=sigma={max(8, int(34 * H / 1920))},eq=brightness=0.05:saturation=1.15,"
                  f"split={len(glass)}" + "".join(f"[gb{i}]" for i in range(len(glass))))
        last = "zmain"
        for i, g in enumerate(glass):
            x, y, w, h, r = g["x"], g["y"], max(4, g["w"]), max(4, g["h"]), g["r"]
            a, b = g["a"], g["b"]
            mask = (f"255*lte(hypot(max(0,abs(X-{w/2})-{w/2-r}),max(0,abs(Y-{h/2})-{h/2-r})),{r})")
            fc.append(f"[gb{i}]trim=start={a:.3f}:end={b:.3f},crop={w}:{h}:{x}:{y},format=yuva420p,"
                      f"geq=lum='p(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{mask}',"
                      f"fade=t=in:st={a:.3f}:d=0.2:alpha=1,fade=t=out:st={max(a, b-0.18):.3f}:d=0.18:alpha=1[g{i}]")
            fc.append(f"[{last}][g{i}]overlay={x}:{y}:eof_action=pass:format=auto[go{i}]")
            last = f"go{i}"
    fc.append(f"[{last}]{sub},format=yuv420p[vout]")

    # audio
    dur = edl["duration"]
    if info["has_audio"]:
        asel = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in keep)
        fc.append(f"[0:a]aselect='{asel}',asetpts=N/SR/TB,aresample=48000,{voice_pitch_filter(edl)}"
                  f"highpass=f=75,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                  f"equalizer=f=3200:t=q:w=1.2:g=2.5,asplit=2[voice][vkey]")
    else:
        inputs += ["-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc.append(f"[{idx}:a]asplit=2[voice][vkey]")
        idx += 1
    mixes = ["[voice]"]
    if p.get("music") or music:
        mpath = music
        if not mpath:
            mpath = str(work / "bed.wav")
            if theme.get("music_template"):
                synth_template(mpath, dur, theme["music_template"])
            else:
                synth_music(mpath, dur, theme.get("bpm", 96), theme.get("music_mood", "bright"))
        inputs += ["-stream_loop", "-1", "-i", mpath]
        fc.append(f"[{idx}:a]aresample=48000,atrim=0:{dur:.3f},volume={music_db}dB[mraw]")
        fc.append("[mraw][vkey]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[music]")
        mixes.append("[music]")
        idx += 1
    else:
        fc.append("[vkey]anullsink")
    if edl.get("sfx"):
        spath = str(work / "sfx.wav")
        synth_sfx(edl, spath)
        inputs += ["-i", spath]
        fc.append(f"[{idx}:a]aresample=48000,volume=-9dB[sfx]")
        mixes.append("[sfx]")
        idx += 1
    fc.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:duration=first:normalize=0,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    script = work / "graph.txt"
    script.write_text(";\n".join(fc), encoding="utf-8")
    shutil.copy(ass_path, Path(out).with_suffix(".ass"))
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", *inputs, "-filter_complex_script", str(script),
           "-map", "[vout]", "-map", "[aout]", "-t", f"{dur:.3f}",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", out]
    log("rendering (this is the slow part)")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-4000:], file=sys.stderr)
        log(f"filter graph kept at {script} for debugging")
        die("render failed")
    log(f"wrote {out}")


# --------------------------------------------------------------------- qa
def qa(video: str, edl_path: str | None, out: str | None) -> bool:
    info = probe(video)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    b = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf", "blackdetect=d=0.3:pix_th=0.08", "-an",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    blacks = len(re.findall(r"black_start", b.stderr))
    checks = []

    def gate(name, ok, detail):
        checks.append({"gate": name, "pass": bool(ok), "detail": detail})

    I = float(lufs[-1]) if lufs else None
    pk = float(peak[-1]) if peak else None
    gate("loudness", I is not None and -16.5 <= I <= -12.5, f"integrated {I} LUFS (target -14 +/- 2)")
    gate("true_peak", pk is not None and pk <= -0.5, f"peak {pk} dBFS (must be <= -0.5)")
    gate("no_black_gaps", blacks == 0, f"{blacks} black segments over 0.3s")
    gate("resolution", min(info["width"], info["height"]) >= 720, f"{info['width']}x{info['height']}")
    if edl_path:
        e = read_json(edl_path)
        d = e["duration"]
        gate("duration_match", abs(info["duration"] - d) < 0.35, f"render {info['duration']:.2f}s vs plan {d:.2f}s")
        spoken = sum(w["e"] - w["s"] for w in e["words"])
        cpm = len([c for c in e["cards"] if c["type"] not in ("hook", "cta")]) / max(d / 60, 0.1)
        gate("card_density", cpm <= e["params"]["cards_per_min"] + 1, f"{cpm:.1f} cards/min, ceiling {e['params']['cards_per_min']}")
        overlaps = 0
        cs = sorted(e["cards"], key=lambda c: c["start"])
        for x, y in zip(cs, cs[1:]):
            if y["start"] < x["end"] - 0.05:
                overlaps += 1
        gate("no_card_overlap", overlaps == 0, f"{overlaps} overlapping cards")
        quiet = d - sum(c["end"] - c["start"] for c in e["cards"])
        gate("breathing_room", quiet / d >= 0.35, f"{quiet/d:.0%} of runtime has no card (min 35%)")
        gate("captions_present", len(e["words"]) > 0 and spoken > 0, f"{len(e['words'])} captioned words")
    ok = all(c["pass"] for c in checks)
    res = {"video": os.path.basename(video), "pass": ok, "checks": checks, "probe": info}
    if out:
        write_json(out, res)
    for c in checks:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['gate']}: {c['detail']}")
    print("QA", "PASSED" if ok else "FAILED")
    return ok


def sheet(video: str, out: str, cols: int = 6, rows: int = 3):
    info = probe(video)
    n = cols * rows
    step = max(0.5, info["duration"] / n)
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf",
         f"fps=1/{step:.3f},scale=320:-1,tile={cols}x{rows}:padding=6:color=white", "-frames:v", "1", out])
    log(f"wrote {out}")


def compare(before: str, after: str, out: str):
    run(["ffmpeg", "-y", "-v", "error", "-i", before, "-i", after, "-filter_complex",
         "[0:v]scale=540:960:force_original_aspect_ratio=increase,crop=540:960,setsar=1,"
         "drawtext=text='BEFORE':x=30:y=30:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=12[a];"
         "[1:v]scale=540:960:force_original_aspect_ratio=increase,crop=540:960,setsar=1,"
         "drawtext=text='AFTER':x=30:y=30:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=12[b];"
         "[a][b]hstack=inputs=2[v]", "-map", "[v]", "-map", "1:a?", "-shortest", "-c:v", "libx264", "-crf", "22",
         "-pix_fmt", "yuv420p", "-c:a", "aac", out])
    log(f"wrote {out}")


# -------------------------------------------------------------------- cli

def _autolog(topic, **fields):
    """Every script and render is written to the content ledger automatically,
    so the user never has to remember. SPLICECRAFT_NO_LOG=1 turns it off."""
    if os.environ.get("SPLICECRAFT_NO_LOG"):
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ledger
        eid = ledger.auto_log(topic, **fields)
        print(f"[splicecraft] logged to content ledger: {eid[:8]} ({topic[:60]})", file=sys.stderr)
    except Exception as e:  # logging must never break an edit
        print(f"[splicecraft] ledger auto-log skipped: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(prog="splicecraft", description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("probe"); s.add_argument("src")
    s = sub.add_parser("transcribe"); s.add_argument("src"); s.add_argument("-o", "--out", default="words.json")
    s.add_argument("--language"); s.add_argument("--key-file"); s.add_argument("--engine", default="auto", choices=["auto", "groq", "local"])

    def plan_args(s):
        s.add_argument("--level", type=int, default=60)
        s.add_argument("--style", default="studio", help="a look from presets/styles.json, or auto (from the genre)")
        s.add_argument("--genre", default="none", help="auto (detect from transcript), none, or a name in presets/genres.json")
        s.add_argument("--brief", help="brief.json: platform, market, age, stage, funnel, niche, tam/sam/som, revenue_target")
        s.add_argument("--captions", choices=CAPTION_MODES, help="force a caption style")
        s.add_argument("--variant", type=int, help="0-359 picks one per-genre look; default hashes the transcript")
        s.add_argument("--brand", help="json file overriding theme colors")
        s.add_argument("--no-cut", action="store_true", help="keep every pause")

    s = sub.add_parser("plan"); s.add_argument("words"); s.add_argument("-o", "--out", default="edl.json"); plan_args(s)
    s.add_argument("--duration", type=float)

    def render_args(s):
        s.add_argument("--size"); s.add_argument("--fps", type=int)
        s.add_argument("--music"); s.add_argument("--music-db", type=float, default=-20)
        s.add_argument("--key", help="green | blue | 0xRRGGBB  (chroma key the source)")
        s.add_argument("--bg", help="background image/video for --key; default animated gradient")
        s.add_argument("--lut", help=".cube file applied after the grade")
        s.add_argument("--grade", choices=list(GRADES))
        s.add_argument("--font-bold"); s.add_argument("--font-body"); s.add_argument("--fontsdir")
        s.add_argument("--crf", type=int, default=19); s.add_argument("--preset", default="medium")

    s = sub.add_parser("music"); s.add_argument("action", choices=["list", "count", "pick", "render"])
    s.add_argument("target", nargs="?", help="pick: words.json   render: template id")
    s.add_argument("--genre"); s.add_argument("--style", default="studio"); s.add_argument("--limit", type=int, default=20)
    s.add_argument("--seconds", type=float, default=20); s.add_argument("-o", "--out", default="music.wav")
    s.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("script"); s.add_argument("topic")
    s.add_argument("--genre", default="education_explainer"); s.add_argument("--seconds", type=int, default=45)
    s.add_argument("--framework"); s.add_argument("--hook"); s.add_argument("--audience", default="general")
    s.add_argument("--language", default="en"); s.add_argument("-o", "--out"); s.add_argument("--brief")
    s = sub.add_parser("brief"); s.add_argument("brief")
    s = sub.add_parser("library"); s.add_argument("kind", choices=["frameworks", "hooks"]); s.add_argument("--category")
    s = sub.add_parser("detect"); s.add_argument("words"); s.add_argument("-o", "--out")
    sub.add_parser("options")
    s = sub.add_parser("render"); s.add_argument("src"); s.add_argument("edl"); s.add_argument("-o", "--out", default="edited.mp4"); render_args(s)
    s = sub.add_parser("qa"); s.add_argument("video"); s.add_argument("--edl"); s.add_argument("-o", "--out")
    s = sub.add_parser("sheet"); s.add_argument("video"); s.add_argument("-o", "--out", default="sheet.jpg")
    s = sub.add_parser("compare"); s.add_argument("before"); s.add_argument("after"); s.add_argument("-o", "--out", default="compare.mp4")
    s = sub.add_parser("synth-music"); s.add_argument("-o", "--out", default="bed.wav"); s.add_argument("--seconds", type=float, default=60)
    s.add_argument("--bpm", type=int, default=96); s.add_argument("--mood", default="bright", choices=["bright", "moody"])
    s = sub.add_parser("auto"); s.add_argument("src"); s.add_argument("-d", "--dir", default="splicecraft_out")
    s.add_argument("--language"); s.add_argument("--key-file"); s.add_argument("--engine", default="auto", choices=["auto", "groq", "local"])
    plan_args(s); render_args(s)

    a = ap.parse_args()
    if a.cmd == "probe":
        print(json.dumps(probe(a.src), indent=2))
    elif a.cmd == "transcribe":
        transcribe(a.src, a.out, a.language, a.key_file, a.engine)
    elif a.cmd == "plan":
        plan(a.words, a.out, a.level, a.style, a.duration, a.brand, a.no_cut, a.genre, a.variant, a.captions, a.brief)
    elif a.cmd == "detect":
        res = detect_genre(read_json(a.words)["words"])
        if a.out:
            write_json(a.out, res)
        res["ranking"] = res["ranking"][:4]
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif a.cmd == "script":
        script(a.topic, a.genre, a.seconds, a.framework, a.hook, a.audience, a.language, a.out, a.brief)
        _autolog(a.topic, status="scripted", seconds=a.seconds, script_path=str(Path(a.out).resolve()) if a.out else "")
    elif a.cmd == "brief":
        print(json.dumps(brief_report(load_brief(a.brief)), indent=2, ensure_ascii=False))
    elif a.cmd == "library":
        items = read_json(PRESETS / "content.json")[a.kind]
        for it in items:
            if not a.category or it["category"] == a.category:
                extra = " > ".join(it["steps"]) if a.kind == "frameworks" else ("RISKY" if it["risky"] else "")
                print(f"{it['category']:<13} {it['name']:<32} {extra}")
        print(f"... {len(items)} {a.kind}")
    elif a.cmd == "music":
        if a.action == "count":
            print(json.dumps({"all": len(music_templates()), **{g: len(music_templates(g)) for g in
                              read_json(PRESETS / "music.json")["genre_match"]}}, indent=2))
        elif a.action == "list":
            ids = music_templates(a.genre)
            print("\n".join(ids[:: max(1, len(ids) // a.limit)][:a.limit]))
            print(f"... {len(ids)} templates" + (f" for {a.genre}" if a.genre else ""))
        elif a.action == "pick":
            w = read_json(a.target)["words"]
            g = a.genre or detect_genre(w)["genre"]
            print(json.dumps(pick_music(w, g, a.style, a.seed), indent=2))
        else:
            synth_template(a.out, a.seconds, a.target)
    elif a.cmd == "options":
        print(json.dumps(option_count(), indent=2))
    elif a.cmd == "render":
        render(a.src, a.edl, a.out, a.size, a.fps, a.music, a.music_db, a.key, a.bg, a.lut, a.grade,
               a.font_bold, a.font_body, a.fontsdir, a.crf, a.preset)
        _autolog(getattr(a, "topic", None) or Path(a.src).stem, status="produced", video_path=str(Path(a.out).resolve()))
    elif a.cmd == "qa":
        sys.exit(0 if qa(a.video, a.edl, a.out) else 2)
    elif a.cmd == "sheet":
        sheet(a.video, a.out)
    elif a.cmd == "compare":
        compare(a.before, a.after, a.out)
    elif a.cmd == "synth-music":
        synth_music(a.out, a.seconds, a.bpm, a.mood)
    elif a.cmd == "auto":
        d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
        words = d / "words.json"
        if not words.exists():
            transcribe(a.src, str(words), a.language, a.key_file, a.engine)
        info = probe(a.src)
        plan(str(words), str(d / "edl.json"), a.level, a.style, info["duration"], a.brand, a.no_cut, a.genre, a.variant, a.captions, a.brief)
        out = str(d / "edited.mp4")
        render(a.src, str(d / "edl.json"), out, a.size, a.fps, a.music, a.music_db, a.key, a.bg, a.lut, a.grade,
               a.font_bold, a.font_body, a.fontsdir, a.crf, a.preset)
        _autolog(Path(a.src).stem, status="produced", video_path=str(Path(out).resolve()))
        ok = qa(out, str(d / "edl.json"), str(d / "qa.json"))
        sheet(out, str(d / "sheet.jpg"))
        sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
