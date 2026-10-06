#!/usr/bin/env python3
"""
splicecraft studio layer: canvas layouts, face-aware framing, HTML overlays.

Why this exists: the classic renderer can only put ASS text boxes on top of a
centre-cropped frame. Every reference the users held up (withpt.ai,
softgirlnocode, bahasvideo, the v1 edit) does three things it cannot:

  1. frames the speaker as an inset on a designed canvas, with a title that stays,
  2. places graphics in the empty space beside the speaker, never on the face,
  3. draws those graphics with real typography and motion.

This module does those three. It is called from splicecraft.py:

  join     clips...  -> one normalised source (rotation, fps, size) + shots.json
  track    source    -> face.json (face box per shot, source time)
  lint     edl.json  -> checks the storyboard before any frame is rendered
  studio   source edl.json -> finished MP4

Needs: ffmpeg, Python 3.9+, opencv-python (face tracking), playwright + chromium
(overlay rendering). Everything degrades loudly, never silently.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"


def log(msg: str):
    print(f"[studio] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1):
    print(f"[studio] error: {msg}", file=sys.stderr)
    sys.exit(code)


def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write_json(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def ffprobe(src: str) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", src],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        die(f"ffprobe failed on {src}")
    return json.loads(r.stdout)


def duration_of(src: str) -> float:
    return float(ffprobe(src)["format"]["duration"])


# ------------------------------------------------------------------ join
def join(clips: list[str], out: str, size: str = "1080x1920", fps: int = 30):
    """Normalise every clip (rotation metadata applied, one size, constant fps,
    48 kHz stereo) and concatenate in the order given. Writes <out> and
    <out>.shots.json with each clip's start/end on the joined timeline, which
    the tracker and the renderer use as shot boundaries."""
    if not clips:
        die("join needs at least one clip")
    W, H = (int(x) for x in size.lower().split("x"))
    work = Path(tempfile.mkdtemp(prefix="sc_join_"))
    parts, shots, t = [], [], 0.0
    for i, c in enumerate(clips):
        if not Path(c).exists():
            die(f"missing clip {c}")
        p = work / f"p{i:03d}.mp4"
        # ffmpeg applies the rotation side data by default (autorotate), so a phone
        # clip stored as 1920x1080 + rotate=90 comes out upright.
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps},format=yuv420p")
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", c, "-vf", vf,
                            "-af", "aresample=48000,aformat=channel_layouts=stereo",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", str(fps),
                            "-c:a", "pcm_s16le", "-ar", "48000", str(p).replace(".mp4", ".mov")],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(r.stderr[-2000:], file=sys.stderr)
            die(f"could not normalise {c}")
        p = Path(str(p).replace(".mp4", ".mov"))
        d = duration_of(str(p))
        shots.append({"clip": str(Path(c).resolve()), "start": round(t, 3), "end": round(t + d, 3)})
        parts.append(p)
        t += d
        log(f"clip {i + 1}/{len(clips)} {Path(c).name}: {d:.2f}s")
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        die("concat failed")
    write_json(out + ".shots.json", {"source": str(Path(out).resolve()), "size": [W, H], "fps": fps, "shots": shots})
    shutil.rmtree(work, ignore_errors=True)
    log(f"wrote {out} ({t:.2f}s, {len(shots)} shots) and {out}.shots.json")


# ------------------------------------------------------------------ track
def track(src: str, out: str, shots_path: str | None = None, sample_fps: float = 4.0):
    """Find the speaker's face per shot. Output is in source seconds and in
    normalised frame coordinates (0-1), so it survives any output size.

    Per shot we keep the MEDIAN face box, not a moving one: a crop that pans with
    every head movement is the robotic look. Editors frame a shot once and punch
    in on purpose; this does the same."""
    try:
        import cv2
    except ImportError:
        die("face tracking needs opencv 4.8+: pip install opencv-python")
    info = ffprobe(src)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    W, H = int(v["width"]), int(v["height"])
    dur = float(info["format"]["duration"])
    shots = read_json(shots_path)["shots"] if shots_path and Path(shots_path).exists() else [
        {"start": 0.0, "end": dur}]
    sw = 360
    sh = int(round(H * sw / W))
    model = ASSETS / "models" / "face_detection_yunet_2023mar.onnx"
    if not model.exists():
        die(f"missing {model}; download face_detection_yunet_2023mar.onnx from github.com/opencv/opencv_zoo")
    det = cv2.FaceDetectorYN.create(str(model), "", (sw, sh), 0.7, 0.3, 50)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={sample_fps},scale={sw}:{sh},format=bgr24",
                             "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    import numpy as np
    dets, k = [], 0
    frame_bytes = sw * sh * 3
    while True:
        buf = proc.stdout.read(frame_bytes)
        if len(buf) < frame_bytes:
            break
        img = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        t = k / sample_fps
        k += 1
        _, faces = det.detect(img)
        if faces is not None and len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])[:4]
            dets.append({"t": round(t, 3), "x": float(x) / sw, "y": float(y) / sh, "w": float(w) / sw, "h": float(h) / sh})
    proc.wait()

    def med(vals):
        s = sorted(vals)
        return s[len(s) // 2]

    res = []
    for i, s in enumerate(shots):
        ds = [d for d in dets if s["start"] <= d["t"] < s["end"]]
        if len(ds) >= 2:
            cx = med([d["x"] + d["w"] / 2 for d in ds])
            cy = med([d["y"] + d["h"] / 2 for d in ds])
            fw = med([d["w"] for d in ds])
            fh = med([d["h"] for d in ds])
            conf = len(ds) / max(1, (s["end"] - s["start"]) * sample_fps)
            # the top of the frame cuts the head when the face box starts at y~0
            cut_top = med([d["y"] for d in ds]) < 0.02
            res.append({"shot": i, "start": s["start"], "end": s["end"], "cx": round(cx, 4), "cy": round(cy, 4),
                        "w": round(fw, 4), "h": round(fh, 4), "found": round(min(1.0, conf), 2), "head_cut": cut_top})
        else:
            res.append({"shot": i, "start": s["start"], "end": s["end"], "cx": None, "cy": None, "w": None, "h": None,
                        "found": 0.0, "head_cut": False})
    # shots with no face borrow the nearest shot that has one; the fallback is centre / upper third
    known = [r for r in res if r["cx"] is not None]
    for r in res:
        if r["cx"] is None:
            if known:
                n = min(known, key=lambda q: abs(q["shot"] - r["shot"]))
                r.update({"cx": n["cx"], "cy": n["cy"], "w": n["w"], "h": n["h"], "borrowed": n["shot"]})
            else:
                r.update({"cx": 0.5, "cy": 0.36, "w": 0.3, "h": 0.17, "borrowed": None})
    write_json(out, {"source": str(Path(src).resolve()), "size": [W, H], "samples": len(dets), "shots": res})
    weak = [r["shot"] for r in res if r["found"] < 0.2]
    cut = [r["shot"] for r in res if r.get("head_cut")]
    log(f"wrote {out}: {len(res)} shots, {len(dets)} face samples")
    if weak:
        log(f"weak face detection in shots {weak}: framing uses a neighbour or the centre. Check the sheet.")
    if cut:
        log(f"PRODUCTION FAULT: the top of the frame cuts the head in shots {cut}. Tell the user; "
            "the canvas layout hides it, but it cannot be repaired.")


# ------------------------------------------------------------------ script
# The script (naskah) is the source of truth for names, terms and on-screen text.
# Whisper mishears names ("KPI" for KPEI, "BI" for BEI) and a model writing cards
# from the transcript will repeat, or explain, the mishearing. So the judgement
# calls are made here, mechanically: align() writes the caption fixes and the retake
# cuts, and lint() refuses card text that is not in the script.
NUM_WORDS = {"1": "satu", "2": "dua", "3": "tiga", "4": "empat", "5": "lima", "6": "enam", "7": "tujuh",
             "8": "delapan", "9": "sembilan", "10": "sepuluh"}


def norm(tok: str) -> str:
    return re.sub(r"[^0-9a-z]", "", tok.lower())


def script_spoken(path: str) -> list[str]:
    """Raw tokens of what the speaker is meant to say, in order. Knows the two shapes
    the script packs use: a MONOLOG table with the lines in quotes, and plain text
    with SUARA: blocks. Anything else: every quoted line, else the whole text."""
    raw = Path(path).read_text(encoding="utf-8")
    m = re.search(r"^#+\s*MONOLOG.*?$(.*?)(?=^##\s)", raw, re.S | re.M | re.I)
    # dialogue: a line "KAMU:" / "TEMAN (panik, sodorin HP):" then the spoken lines
    role = re.compile(r"^[A-Z][A-Z .]{1,20}(\([^)]*\))?:\s*$", re.M)
    if m:
        parts = re.findall(r"[\"“]([^\"”]+)[\"”]", m.group(1))
    elif re.search(r"^SUARA:", raw, re.M):
        parts = re.findall(r"^SUARA:\s*\n(.*?)(?=^\s*ADEGAN|\Z)", raw, re.S | re.M)
    elif len(role.findall(raw)) >= 2:
        parts = [re.split(r"\n\s*\n", raw[r.end():], 1)[0] for r in role.finditer(raw)]
    else:
        quoted = re.findall(r"[\"“]([^\"”]+)[\"”]", raw)
        parts = quoted if sum(len(q.split()) for q in quoted) >= 30 else \
            [ln for ln in raw.splitlines() if not ln.lstrip().startswith(("#", "|", "-", "*"))]
    text = re.sub(r"\([^)]*\)", " ", " ".join(p.strip() + "." for p in parts))   # stage directions out
    toks = [t.strip("\"“”'*_`|·•—–") for t in text.split()]           # keep . , ? for sentence starts
    return [t for t in toks if norm(t)]


def scripts_of(s) -> list[str]:
    return [] if not s else ([s] if isinstance(s, str) else list(s))


def script_vocab(paths) -> set[str]:
    """Every word anywhere in the script(s), including the on-screen text column."""
    vocab = set()
    for path in scripts_of(paths):
        for t in re.split(r"\s+", Path(path).read_text(encoding="utf-8")):
            vocab.add(norm(t))
            vocab.update(norm(p) for p in re.split(r"[-/·]", t))
    vocab.discard("")
    return vocab


def _pair(T: list[str], S: list[str]) -> list[tuple]:
    """Word-level alignment inside a small mismatched block. Moves: 1:1, 2:1 (Whisper
    split one name in two: "ID clear" -> IDClear), skip a said word, skip a script word.
    Returns (i_list, j) pairs worth fixing."""
    import difflib
    from functools import lru_cache

    def r(a, b):
        return difflib.SequenceMatcher(None, a, b).ratio()

    @lru_cache(None)
    def best(i, j):
        if i == len(T) or j == len(S):
            return (0.3 * ((len(T) - i) + (len(S) - j)), ())
        opts = [(0.3 + best(i + 1, j)[0], best(i + 1, j)[1]),
                (0.3 + best(i, j + 1)[0], best(i, j + 1)[1])]
        c = 1 - r(T[i], S[j])
        opts.append((c + best(i + 1, j + 1)[0], (((i,), j),) + best(i + 1, j + 1)[1]))
        # a merge must beat both halves, else "itu enggak" -> nggak eats a real word
        if i + 1 < len(T) and r(T[i] + T[i + 1], S[j]) > max(r(T[i], S[j]), r(T[i + 1], S[j])) + 0.1:
            c = 1 - r(T[i] + T[i + 1], S[j]) + 0.15
            opts.append((c + best(i + 2, j + 1)[0], (((i, i + 1), j),) + best(i + 2, j + 1)[1]))
        return min(opts, key=lambda o: o[0])
    return [(ii, j, r("".join(T[k] for k in ii), S[j])) for ii, j in best(0, 0)[1]]


def grounded(tok: str, vocab: set[str]) -> bool:
    t = norm(tok)
    if not t or t in vocab:
        return True
    if t.isdigit():
        return NUM_WORDS.get(t) in vocab
    return len(t) >= 5 and any(v[:5] == t[:5] for v in vocab if len(v) >= 5)


def retakes(words: list[dict], scripts: list[list[str]] | None = None, n: int = 5, window: int = 60) -> list[list]:
    """A run of n words said twice within `window` words is a retake: keep the second
    take (people redo a line because the first was wrong) and cut from the start of the
    first take to the start of the second. Repetition written into one script is kept
    (counted per script: two versions of one script share lines without repeating them)."""
    toks = [norm(w["w"]) for w in words]
    sgrams = set()
    for script_toks in scripts or []:
        st = [norm(t) for t in script_toks]
        seen = set()
        for i in range(len(st) - n + 1):
            g = tuple(st[i:i + n])
            (sgrams.add(g) if g in seen else seen.add(g))
    out, i = [], 0
    while i < len(toks) - n:
        g = tuple(toks[i:i + n])
        hit = next((j for j in range(i + n, min(len(toks) - n + 1, i + window))
                    if tuple(toks[j:j + n]) == g), None)
        if hit is None or g in sgrams or not all(g):
            i += 1
            continue
        a, b = i, hit
        while a > 0 and b - 1 > a + n and toks[a - 1] == toks[b - 1]:
            a, b = a - 1, b - 1
        out.append([round(words[a]["s"] - 0.04, 3), round(words[b]["s"] - 0.04, 3),
                    " ".join(w["w"] for w in words[a:a + n + 3])])
        i = hit + n
    return out


def _align_one(words: list[dict], script_path: str) -> dict:
    import difflib
    stoks = script_spoken(script_path)
    rt = retakes(words, [stoks])
    drops = [[a, b] for a, b, _ in rt]
    kw = [w for w in words if not any(a <= w["s"] < b for a, b in drops)]
    T = [norm(w["w"]) for w in kw]
    S = [norm(t) for t in stoks]
    sent_start = {0} | {k for k in range(1, len(stoks)) if re.search(r"[.?!:][\"”']?$", stoks[k - 1])}

    def cased(k):                                    # script spelling, minus sentence-start capitals
        t = stoks[k].rstrip(".,?!:;")
        # a sentence-start word keeps its capital only when it opens a long name
        # ("Kliring Penjaminan Efek Indonesia"), not "Di Bursa" or "Namanya IDClear"
        run = 0
        while k + run < len(stoks) and stoks[k + run][:1].isupper():
            run += 1
            if re.search(r"[.?!:,;]$", stoks[k + run - 1]):
                break
        opens_name = run >= 3 and norm(t) not in _sc().STOP
        if k in sent_start and t[:1].isupper() and t[1:] == t[1:].lower() and not opens_name:
            return t[0].lower() + t[1:]
        return t

    def is_name(k):
        t = cased(k)
        return t[:1].isupper() or sum(c.isupper() for c in t) >= 2

    fix_at, matched = [], 0

    def put(w, new):
        if re.sub(r"[.,?!]+$", "", w["w"].strip()) != new:
            fix_at.append({"t": round(w["s"], 3), "was": w["w"].strip(), "w": new})
    sm = difflib.SequenceMatcher(None, T, S, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            matched += i2 - i1
            for d in range(i2 - i1):                 # right word, wrong case: "bursa efek" -> Bursa Efek
                if is_name(j1 + d):
                    put(kw[i1 + d], cased(j1 + d))
        elif op == "replace" and i2 - i1 == j2 - j1 <= 4 and all(is_name(j) for j in range(j1, j2)) and                 any(difflib.SequenceMatcher(None, T[i1 + d], S[j1 + d]).ratio() >= 0.5 for d in range(i2 - i1)):
            # a whole name misheard: "Kustodian Center APEC" -> Kustodian Sentral Efek
            for d in range(i2 - i1):
                put(kw[i1 + d], cased(j1 + d))
        elif op == "replace" and i2 - i1 <= 6 and j2 - j1 <= 6:
            for ii, j, ratio in _pair(T[i1:i2], S[j1:j2]):
                said, meant = "".join(T[i1 + k] for k in ii), S[j1 + j]
                if not is_name(j1 + j):
                    # a plain word said differently is the speaker's choice, not a mishearing:
                    # "dan"/"yang", "teriaknya"/"teriak" stay as said
                    short = min(len(said), len(meant)) <= 3
                    if ratio < (0.75 if short else 0.5) or said.startswith(meant) or meant.startswith(said):
                        continue
                elif ratio < 0.5:
                    continue
                put(kw[i1 + ii[0]], cased(j1 + j))
                for extra in ii[1:]:
                    put(kw[i1 + extra], "")
    # speech before the first / after the last scripted word: greetings, sign-offs
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 1]
    tails = []
    if blocks and kw:
        first, last = blocks[0].a, blocks[-1].a + blocks[-1].size - 1
        if 0 < first <= 4:
            tails.append([round(max(0.0, kw[0]["s"] - 0.3), 3), round(kw[first]["s"] - 0.04, 3),
                          " ".join(w["w"] for w in kw[:first])])
        if 0 < len(kw) - 1 - last <= 6:
            tails.append([round(kw[last]["e"] + 0.05, 3), round(kw[-1]["e"] + 0.5, 3),
                          " ".join(w["w"] for w in kw[last + 1:])])
    return {"script": str(Path(script_path).resolve()), "coverage": round(matched / max(1, len(S)), 3),
            "speech_in_script": round(matched / max(1, len(T)), 3), "matched": matched,
            "fix_at": fix_at, "drop": drops + [[a, b] for a, b, _ in tails],
            "why": {"retake": [x[2] for x in rt], "off_script": [x[2] for x in tails]}}


def best_align(words_path: str, script_paths) -> dict:
    """Transcript vs script -> caption fixes (by word position, so a common word is only
    changed where it was misheard), retake cuts, and off-script head/tail cuts. Given
    several scripts (a pack often has two versions of the same video), the one the
    speaker actually followed wins; all of them count as vocabulary for the cards."""
    words = [dict(w) for w in read_json(words_path)["words"]]
    given = [str(Path(p).resolve()) for p in scripts_of(script_paths)]
    # the speaker may have read a different version than the one handed over: try every
    # script-sized text file next to the given ones and let the speech decide
    pool = list(given)
    for d in {Path(p).parent for p in given}:
        for f in sorted(d.iterdir()):
            if f.suffix.lower() in (".md", ".txt") and 200 < f.stat().st_size < 20000 and str(f) not in pool:
                pool.append(str(f))

    def f1(r):
        c, q = r["coverage"], r["speech_in_script"]
        return 2 * c * q / (c + q) if c + q else 0.0
    tries = sorted((_align_one(words, p) for p in pool), key=lambda r: -f1(r))
    best = tries[0]
    paths = [best["script"]] + [p for p in given if p != best["script"]]
    return dict(best, scripts=paths, f1=round(f1(best), 3), ok=f1(best) >= 0.4, given=given,
                match={Path(t["script"]).name: round(f1(t), 2) for t in tries[:4]})


def align(words_path: str, script_paths, edl_path: str | None = None) -> dict:
    """CLI view of best_align: shows what lint and render will apply, and records the
    script in the edl. The fixes are NOT stored in the edl: storyboard() recomputes them on
    every lint and render, so there is no step to skip and nothing to overwrite by hand."""
    res = best_align(words_path, script_paths)
    if not res["ok"]:
        die(f"no script matches this speech (best: {Path(res['script']).name}, {res['coverage']:.0%} of it "
            "spoken). Stop and ask the user for the right script; do not guess card text or fixes.")
    if res["script"] not in res["given"]:
        log(f"using {Path(res['script']).name}: it matches the speech better ({res['f1']:.2f}) than what was given")
    if edl_path:
        edl = read_json(edl_path) if Path(edl_path).exists() else {}
        edl["script"] = res["scripts"] if len(res["scripts"]) > 1 else res["scripts"][0]
        edl.pop("fix_at", None)
        edl.pop("drop", None)
        write_json(edl_path, edl)
    return res


def load_edl(path: str) -> dict:
    edl = read_json(path)
    if edl.get("script"):
        edl["script"] = [p if Path(p).is_absolute() else str((Path(path).parent / p).resolve())
                         for p in scripts_of(edl["script"])]
    return edl


# ------------------------------------------------------------------ storyboard
# One layout, measured once. Values are canvas px on 1080x1920.
LAYOUT = {"inset": {"x": 40, "y": 400, "w": 1000, "h": 1290, "r": 44}, "caption_y": 1560}
# full layout (default): the footage fills the screen and the framing changes every few seconds,
# the way a short is cut (the v1 reference changes picture every ~0.9 s; one fixed frame for 80 s
# reads as "just a frame"). Levels are digital zooms of the real footage, not animation.
FULL = {"x": 0, "y": 0, "w": 1080, "h": 1920, "r": 0}
FULL_CAPTION_Y = 1400
LEVELS = (1.0, 1.28, 1.6)            # wide, medium, tight
SHEET_LEVELS = (1.45, 1.62)          # while a card sheet covers the bottom: face pushed up
LEVEL_ORDER = (0, 1, 0, 2, 1, 2)
MAX_BEAT = 2.6                       # the picture changes at least this often (seconds)
PUSH = 1.05                          # slow push-in inside every beat (the pack allows 105%)
REACT_Z = 2.0                        # "react" beats: an extreme close-up on a reaction (v1's "holy sh*t" shot)
THEMES = {
    "paper": {"bg": "#f3f2ee", "ink": "#151515", "muted": "#6b6b6b", "accent": "#2563eb", "card": "#ffffff"},
    "night": {"bg": "#101114", "ink": "#f4f4f2", "muted": "#a3a3a3", "accent": "#ffd166", "card": "#1c1d22",
              "on-accent": "#101114"},
    "red": {"bg": "#f6f1ec", "ink": "#1a1414", "muted": "#6e6262", "accent": "#d7263d", "card": "#ffffff"},
}


def _sc():
    sys.path.insert(0, str(HERE))
    import splicecraft  # noqa: E402
    return splicecraft


def slate_of(o: dict) -> float:
    """Seconds a card opens as a full-screen slate before it becomes a sheet over the footage.
    Short on purpose: a slate replaces the footage, and the pack caps that at 30% of the video."""
    if o["type"] in ("chip", "endcard", "punch") or o.get("slate") is False:
        return 0.0
    return round(min(float(o.get("slate", 1.3)), (o["end"] - o["start"]) * 0.35), 3)


def full_beats(segs, kept, ovs, edl, reacts=(), joins=()):
    """Full layout: cut the output into beats of at most MAX_BEAT seconds and give each one a
    framing. segs: [[out_start, out_end, face]] (a face = the tracker's box for that shot);
    kept: words with output times. A beat ends at a time cut, at a card's sheet edge (the
    framing must lift the face before a sheet covers the bottom), or at the pause before a word.
    Returns beats [{s, e, z, cx, cy, anchor, face}] in output time, face in canvas px."""
    maxb = float(edl.get("beat", MAX_BEAT))
    sheets = [(o["start"] + o["slate"], o["end"]) for o in ovs if o["type"] not in ("chip", "endcard", "punch")]
    # a punch card covers the footage: the framing changes under it, so the cut back lands on a new shot
    punches = [(o["start"], o["end"]) for o in ovs if o["type"] == "punch"]
    reacts = [r for r in reacts if not any(s - 0.2 <= r <= e for s, e in sheets + punches)]
    marks = sorted({round(t, 3) for s, e in sheets + punches for t in (s, e)} |
                   {round(t, 3) for r in reacts for t in (r, r + 0.8)} | {round(j, 3) for j in joins})
    # a join with the same framing on both sides is a jump cut: every join must be a beat edge
    def at_join(t):
        return any(abs(t - j) < 0.02 for j in joins)
    lo = min(1.3, maxb * 0.6)
    starts = []                                        # (output start of a word, pause before it)
    for a, b in zip([None] + kept, kept):
        starts.append((b["o"], b["o"] - a["oe"] if a else 1.0))
    pieces = []
    for a, b, f in segs:
        pts = [a] + [m for m in marks if a + 0.3 < m < b - 0.3] + [b]
        for x, y in zip(pts, pts[1:]):
            cur = x
            while y - cur > maxb:
                cand = [(round(g, 1), s) for s, g in starts if cur + lo <= s <= cur + maxb and s < y - lo * 0.75]
                if not cand:                           # dense speech: the nearest word start, else cut mid-word
                    near = [s for s, g in starts if cur + 0.7 <= s <= cur + maxb + 0.6 and s < y - 0.7]
                    cut = max(near) if near else (cur + maxb if y - cur - maxb >= 0.7 else None)
                    if cut is None:
                        break
                    pieces.append([cur, cut, f])
                    cur = cut
                    continue
                cut = max(cand)[1]                     # the word after the longest pause
                pieces.append([cur, cut, f])
                cur = cut
            pieces.append([cur, y, f])
    merged = []                                        # a sliver (a word end, a card edge) is a flash, not a beat
    for a, b, f in pieces:
        if merged and b - a < 0.7 and not at_join(a):
            merged[-1][1] = b
        elif merged and merged[-1][1] - merged[-1][0] < 0.7 and not at_join(merged[-1][0]) and not at_join(a):
            merged[-1][1:] = [b, f]
        else:
            merged.append([a, b, f])
    beats, n, m, prev = [], 0, 0, None
    for a, b, f in merged:
        if b - a <= 0.01:
            continue
        mid = (a + b) / 2
        if any(s <= mid < e for s, e in sheets):
            z, anchor = SHEET_LEVELS[m % len(SHEET_LEVELS)], 0.27
            m += 1
            if prev and z == prev and len(set(SHEET_LEVELS)) > 1:
                z = SHEET_LEVELS[m % len(SHEET_LEVELS)]
                m += 1
        elif any(a - 0.05 <= r < a + 0.4 for r in reacts):  # a sliver merged in front can move the start a little
            z, anchor = REACT_Z, 0.45
        else:
            z, anchor = LEVELS[LEVEL_ORDER[n % len(LEVEL_ORDER)]], 0.38
            n += 1
            if prev and z == prev:
                z = LEVELS[LEVEL_ORDER[n % len(LEVEL_ORDER)]]
                n += 1
        prev = z
        beats.append({"s": round(a, 3), "e": round(b, 3), "z": z, "cx": f["cx"], "cy": f["cy"], "anchor": anchor,
                      "face": face_box(f, z, anchor)})
    return beats


def _crop(f, z, anchor):
    """Crop window (source fractions) of zoom z with the face centre at (0.5, anchor) of the frame."""
    w = 1 / z
    left = max(0.0, min(1 - w, f["cx"] - 0.5 * w))
    top = max(0.0, min(1 - w, f["cy"] - anchor * w))
    return left, top, w


def face_box(f, z, anchor):
    """Face in canvas px over the whole beat (start zoom and pushed-in end zoom together)."""
    boxes = []
    for zz in (z, z * PUSH):
        left, top, w = _crop(f, zz, anchor)
        boxes.append(((f["cx"] - f["w"] / 2 - left) / w * 1080, (f["cy"] - f["h"] / 2 - top) / w * 1920,
                      (f["cx"] + f["w"] / 2 - left) / w * 1080, (f["cy"] + f["h"] / 2 - top) / w * 1920))
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    return {"x": round(x0), "y": round(y0), "w": round(x1 - x0), "h": round(y1 - y0)}


def zoompan_of(beats, fps, size):
    """One zoompan over the cut footage (output time): each beat holds its framing and pushes
    in slowly to PUSH x its zoom. x/y keep the face where the beat put it and stay in frame."""
    def pw(val):
        return "+".join(f"gte(it,{b['s']:.3f})*lt(it,{b['e'] + (1 if k == len(beats) - 1 else 0):.3f})*({val(b)})"
                        for k, b in enumerate(beats))
    z = pw(lambda b: f"{b['z']}*(1+{PUSH - 1:.3f}*(it-{b['s']:.3f})/{max(0.1, b['e'] - b['s']):.3f})")
    # pw() is a sum of terms: wrap it in parentheses, or "*iw" multiplies only the last beat and
    # every other beat's x/y comes out as a fraction of a pixel (the crop sticks to the top-left)
    x = "clip((" + pw(lambda b: f"{b['cx']:.4f}") + ")*iw-iw/zoom*0.5,0,iw-iw/zoom)"
    y = "clip((" + pw(lambda b: f"{b['cy']:.4f}") + ")*ih-ih/zoom*(" + pw(lambda b: f"{b['anchor']}") + "),0,ih-ih/zoom)"
    return f"zoompan=z='max(1,{z})':x='{x}':y='{y}':d=1:s={size}:fps={fps}"


def storyboard(src: str, words_path: str, face_path: str, edl: dict) -> dict:
    """edl (source seconds, written by the editor) -> SC_DATA (output seconds) plus the
    per-shot crop the ffmpeg side needs. Everything that moves in time is remapped here,
    in one place, so a cut can never desync a caption or a card."""
    sc = _sc()
    words = read_json(words_path)["words"]
    fj = read_json(face_path)
    faces = fj["shots"]
    dur = duration_of(src)
    full = edl.get("layout", "full") == "full"
    I = dict(FULL) if full else dict(LAYOUT["inset"], **edl.get("inset", {}))
    capy = edl.get("caption_y", FULL_CAPTION_Y if full else LAYOUT["caption_y"])
    keep = edl.get("keep") or sc.build_keep(words, edl.get("gap", 0.5), 0.12, dur)
    # script -> caption fixes + retake/off-script cuts, recomputed every time (see align)
    auto = None
    scripts = scripts_of(edl.get("script")) if edl.get("script") not in (False, "missing") else []
    if scripts and all(Path(p).exists() for p in scripts):
        auto = best_align(words_path, scripts)
        if auto["ok"]:
            edl = dict(edl, script=auto["scripts"], fix_at=auto["fix_at"] + edl.get("fix_at", []),
                       drop=auto["drop"] + edl.get("drop", []))
    # hold spans: lines the script says not to cut ("pelan, jangan dipotong") keep their pauses
    for a, b in edl.get("hold", []):
        merged = []
        for s, e in sorted(keep + [[a, min(b, dur)]]):
            if merged and s <= merged[-1][1] + 0.02:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        keep = merged
    # drop spans: retakes found by align plus any the editor added
    for a, b in edl.get("drop", []):
        nk = []
        for s, e in keep:
            if e <= a or s >= b:
                nk.append([s, e])
            else:
                if s < a:
                    nk.append([s, a])
                if e > b:
                    nk.append([b, e])
        keep = nk
    # a drop edge can land inside a word: the kept side would carry a syllable of the retake, so
    # snap a start to that word's end and an end to that word's start
    snapped = []
    for s, e in keep:
        for w in words:
            if w["s"] + 0.01 < s < w["e"] - 0.01:
                s = w["e"]
            if w["s"] + 0.01 < e < w["e"] - 0.01:
                e = w["s"]
        snapped.append([s, e])
    keep = [[round(s, 3), round(e, 3)] for s, e in snapped if e - s > 0.08]
    remap, total = sc.remap_fn(keep)

    def inside(t):
        return any(s <= t <= e for s, e in keep)

    # speaker crop per shot: scale source to inset width, pick a vertical window with
    # headroom above the face. Fixed per shot, like an editor frames a shot once.
    SW, SH = fj["size"]
    scale = I["w"] / SW * edl.get("zoom", 1.0)
    punch = float(edl.get("punch", 1.12) or 1.0)

    def even(x):
        return int(round(x / 2) * 2)

    def frame(f, z):                                 # crop window + face box at zoom z
        vwz, vhz = even(SW * scale * z), even(SH * scale * z)
        fx, fy, fw, fh = f["cx"] * vwz, f["cy"] * vhz, f["w"] * vwz, f["h"] * vhz
        top = max(0.0, min(vhz - I["h"], fy - fh / 2 - I["h"] * 0.16))   # ~16% headroom above the forehead
        left = max(0.0, min(vwz - I["w"], fx - I["w"] / 2)) if vwz > I["w"] else 0.0
        return round(left), round(top), {"x": round(I["x"] + fx - fw / 2 - left), "y": round(I["y"] + fy - fh / 2 - top),
                                          "w": round(fw), "h": round(fh)}
    vw, vh = even(SW * scale), even(SH * scale)
    crops = []
    for f in faces:
        x1, y1, _ = frame(f, 1.0)
        xz, yz, _ = frame(f, punch)
        crops.append({"start": f["start"], "end": f["end"], "x": x1, "y": y1, "zx": xz, "zy": yz})
    # punch-in on jump cuts: inside one shot, every cut that removed a pause flips between the
    # wide and the tight frame, so the cut reads as a choice instead of a glitch
    segs = []
    for s, e in keep:
        for k, f in enumerate(faces):
            a, b = max(s, f["start"]), min(e, f["end"])
            if b - a > 0.02:
                segs.append([a, b, k])
    zoomed, prev = [], None
    z = False
    for a, b, k in segs:
        if punch > 1.0 and prev and prev[2] == k and a - prev[1] >= 0.25 and b - a >= 1.0:
            z = not z
        elif not prev or prev[2] != k:
            z = False
        zoomed.append(z)
        prev = (a, b, k)
    shots = []
    for (a, b, k), zz in zip(segs, zoomed):
        oa, ob = remap(a), remap(b)
        if ob - oa > 0.01:
            shots.append({"start": round(oa, 3), "end": round(ob, 3), "zoom": punch if zz else 1.0,
                          "face": frame(faces[k], punch if zz else 1.0)[2]})

    kept = [dict(w) for w in words if inside((w["s"] + w["e"]) / 2)]
    # fix_at (written by align from the script) corrects one word at one time; "" removes
    # the word (the second half of a name Whisper split in two)
    at = {round(f["t"], 2): f["w"] for f in edl.get("fix_at", [])}
    for w in kept:
        if round(w["s"], 2) in at:
            w["w"] = at[round(w["s"], 2)]
    kept = [w for w in kept if w["w"].strip()]
    for k in range(len(kept) - 1, 0, -1):            # Whisper splits reduplication: "kira -kira" -> kira-kira
        if kept[k]["w"].strip().startswith("-"):
            kept[k - 1] = dict(kept[k - 1], w=kept[k - 1]["w"].strip() + kept[k]["w"].strip(), e=kept[k]["e"])
            del kept[k]
    fixes = edl.get("fix", {})                       # whisper mistakes, word -> correct spelling
    caps = []
    for i, ch in enumerate(sc.caption_chunks(kept, edl.get("caption_words", 2), 1.6)):
        ws = [re.sub(r"[.,]+$", "", x["w"].strip()) for x in ch]
        ws = [fixes.get(w, fixes.get(w.lower(), w)) for w in ws]
        cand = [k for k, w in enumerate(ws) if sc.is_keyword(w)]
        key = max(cand, key=lambda k: len(ws[k])) if cand else -1
        s, e = remap(ch[0]["s"]), remap(ch[-1]["e"])
        caps.append({"i": i, "s": round(s, 3), "e": round(e, 3), "w": ws, "key": key,
                     "t": [round(remap(x["s"]), 3) for x in ch]})
    for a, b in zip(caps, caps[1:]):                 # close tiny gaps so the chip doesn't flicker
        if b["s"] - a["e"] < 0.3:
            a["e"] = b["s"]

    ovs = []
    for o in edl.get("overlays", []):
        o = json.loads(json.dumps(o))
        o["start"] = round(remap(o.pop("at")), 3)
        o["end"] = round(remap(o.pop("until")), 3) if "until" in o else round(o["start"] + o.pop("hold", 3.0), 3)
        o["end"] = min(o["end"], round(total, 3))     # nothing runs into the end card
        for it in o.get("items", []):
            if "at" in it:
                it["t"] = round(remap(it.pop("at")), 3)
        if "icons" in o:                             # "icons": ["door", {"icon": "house", "at": 42.8}]
            o["icons"] = [dict({"icon": i} if isinstance(i, str) else i) for i in o["icons"]]
            for ic in o["icons"]:
                if "at" in ic:
                    ic["t"] = round(remap(ic.pop("at")), 3)
        ovs.append(o)
    # the end card comes AFTER the last word (the speaker is never cut off by it)
    hold = float(edl["endcard"].get("hold", 2.5)) if edl.get("endcard") else 0.0
    if edl.get("endcard"):
        ovs.append({"type": "endcard", "start": round(total - 0.05, 3), "end": round(total + hold + 1, 3),
                    **{k: edl["endcard"][k] for k in ("lines", "eyebrow", "icon") if edl["endcard"].get(k)}})

    beats, hook_end = [], 0.0
    if full:
        # the title opens the video big (hook). A card that starts inside the hook skips its slate
        # and shows its sheet under the title, so the two never fight for the screen
        first = min([o["start"] for o in ovs if o["type"] not in ("chip", "endcard", "punch")] or [9.0])
        hook_end = first if 1.2 <= first < 2.4 else 2.4
        for o in ovs:
            o["slate"] = 0.0 if o["start"] < hook_end else slate_of(o)
        oseg = [[round(remap(a), 3), round(remap(b), 3), faces[k]] for a, b, k in segs]
        okept = [{"o": remap(w["s"]), "oe": remap(w["e"])} for w in kept]
        reacts = [round(remap(t), 3) for t in edl.get("react", []) if inside(t)]
        joins, acc = [], 0.0                          # where two kept pieces meet, in output time
        for s, e in keep[:-1]:
            acc += e - s
            joins.append(round(acc, 3))
        beats = full_beats([s for s in oseg if s[1] - s[0] > 0.01], okept, ovs, edl, reacts, joins)
        shots = [{"start": b["s"], "end": b["e"], "zoom": b["z"], "face": b["face"]} for b in beats]

    colors = dict(THEMES[edl.get("theme", "paper")], **edl.get("colors", {}))
    data = {"title": edl["title"], "subtitle": edl.get("subtitle"), "subtitle_html": edl.get("subtitle_html"),
            "layout": "full" if full else "inset", "hook_end": round(hook_end, 3) if full else 0,
            "inset": I, "caption_y": capy, "colors": colors, "decimal": edl.get("decimal", ","),
            "shots": shots, "captions": caps, "overlays": ovs, "duration": round(total + hold, 3),
            "safe_bottom": edl.get("safe_bottom", 1632)}
    return {"data": data, "keep": keep, "crops": crops, "scale": scale, "vw": vw, "vh": vh, "punch": punch,
            "beats": beats, "size": [SW, SH],
            "vwz": even(SW * scale * punch), "vhz": even(SH * scale * punch),
            "zoomed": [[round(a, 3), round(b, 3)] for (a, b, _), zz in zip(segs, zoomed) if zz],
            "content": round(total, 3), "hold": hold, "grade": edl.get("grade", "auto"), "limits": edl.get("limits"),
            "script": edl.get("script", "missing"),
            "align": None if not auto else {k: auto[k] for k in ("script", "f1", "ok", "match", "why")},
            "kept_words": [{"w": w["w"], "s": w["s"], "o": round(remap(w["s"]), 3)} for w in kept]}


# ------------------------------------------------------------------ overlay browser
class Overlay:
    def __init__(self, data: dict, scale: float = 1.0):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch()
        # layout stays in 1080x1920 css px; scale < 1 only rasterises smaller (draft)
        self.page = self.browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=scale)
        self.page.add_init_script("window.SC_DATA = " + json.dumps(data, ensure_ascii=False) + ";")
        self.page.on("pageerror", lambda e: log(f"overlay js error: {e}"))
        self.page.goto((ASSETS / "studio.html").as_uri())
        self.page.wait_for_function("window.scReady === true", timeout=20000)
        self.page.evaluate("document.fonts.ready.then(() => true)")

    def report(self):
        return self.page.evaluate("window.scReport()")

    def frame(self, t: float) -> str:
        return self.page.evaluate(f"window.scRender({t:.4f})")

    def shot(self) -> bytes:
        return self.page.screenshot(type="png", omit_background=True)

    def close(self):
        self.browser.close()
        self._pw.stop()


# ------------------------------------------------------------------ lint
# What each overlay type draws. A field a type does not read is a card that renders
# differently from what the editor wrote (a cta given title/body shows an empty pill).
COMMON = {"type", "at", "until", "hold", "mode", "place", "start", "end", "id", "slate"}
ICONIC = {"icons", "arrows"}                         # an icon row on top of a card (assets/icons.js)
FIELDS = {"term": {"eyebrow", "title", "body"} | ICONIC, "stat": {"eyebrow", "value", "suffix", "label", "count"} | ICONIC,
          "chip": {"text"}, "word": {"lead", "text"} | ICONIC, "quote": {"text", "by"} | ICONIC,
          "list": {"eyebrow", "title", "marker", "items"} | ICONIC, "flow": {"eyebrow", "title", "items"},
          "compare": {"left", "right", "highlight"}, "question": {"text"}, "cta": {"text"},
          "props": {"items"}, "prop": {"icon", "text", "from"}, "endcard": {"lines", "eyebrow", "icon"},
          "punch": {"lead", "text"}}
NEEDS = {"term": "title", "stat": "value", "chip": "text", "word": "text", "quote": "text", "list": "items",
         "flow": "items", "compare": "left", "question": "text", "cta": "text", "endcard": "lines",
         "props": "items", "prop": "icon", "punch": "text"}
TAKEOVER = {"term", "stat", "list", "flow", "quote", "compare"}
ICON_NAMES = {"ball", "whistle", "book", "shield", "door", "house", "key", "phone", "check", "sid", "envelope"}
# fields that are the editor's labels, checked for invented names/numbers only
LABELS = {"eyebrow", "marker", "highlight", "place", "mode", "type"}


def card_text(o: dict) -> list[tuple[str, str]]:
    """(field, text) pairs a viewer reads on this card."""
    out = []
    for k, v in o.items():
        if k in COMMON or k in {"marker", "highlight", "count", "icon", "icons", "arrows", "from"}:
            continue
        if isinstance(v, str):
            out.append((k, v))
        elif isinstance(v, list):
            for it in v:
                if isinstance(it, str):
                    out.append((k, it))
                elif isinstance(it, dict):
                    out += [(k, it[f]) for f in ("text", "sub") if isinstance(it.get(f), str)]
        elif isinstance(v, dict):
            out += [(k, v[f]) for f in ("eyebrow", "title", "body") if isinstance(v.get(f), str)]
    return out


def invented(text: str, vocab: set[str], strict: bool) -> list[str]:
    """Words on screen the script never says. strict: every content word; else only
    names (ALL-CAPS / MixedCase) and numbers, which is where a wrong card does harm."""
    stop = _sc().STOP
    bad = []
    for raw in re.split(r"[\s/·•—–]+", text):
        t = raw.strip("\"“”'()*.,:;!?%+")
        if not norm(t) or norm(t) in stop:
            continue
        is_name = bool(re.search(r"\d", t)) or sum(c.isupper() for c in t) >= 2
        if (strict or is_name) and not grounded(t, vocab):
            bad.append(t)
    return bad


def lint(sb: dict, report: list) -> list:
    """Problems a human editor would catch on the first watch. Checked before render,
    so a bad storyboard costs seconds, not a render."""
    probs, D = [], sb["data"]
    I = D["inset"]
    # -- content: the part a weak model gets wrong, so the tool decides it
    script = sb.get("script", "missing")
    stoks = None
    if script == "missing":
        probs.append('edl has no "script": set it to the naskah file (look next to the clips), '
                     'or "script": false when there truly is none. Then run align.')
    elif script:
        missing = [p for p in scripts_of(script) if not Path(p).exists()]
        al = sb.get("align")
        if missing:
            probs.append(f"script not found: {missing}")
        elif al and not al["ok"]:
            probs.append(f"no script matches the speech (best {Path(al['script']).name}, match {al['f1']:.2f}): "
                         "wrong script. Ask the user for the right one")
        else:
            vocab = script_vocab(script)
            stoks = [script_spoken(p) for p in scripts_of(script)]
            for field, txt in [("title", D["title"]), ("subtitle", D.get("subtitle") or "")]:
                bad = invented(txt, vocab, strict=False)
                if bad:
                    probs.append(f"{field} names {bad}, which the script never says")
            for o in D["overlays"]:
                for field, txt in card_text(o):
                    bad = invented(txt, vocab, strict=field not in LABELS)
                    if bad:
                        probs.append(f"overlay at {o['start']:.1f}s ({o['type']}) {field} says {bad}: not in the "
                                     "script. Take card text from the script's on-screen text / lines, do not write your own")
            # every on-screen text the script asks for is on a card (plan writes them; a model may drop one)
            import plan as P
            shown = {norm(x) for o in D["overlays"] for _, txt in card_text(o) for x in re.split(r"[\s/·:,.?-]+", txt)}
            shown.discard("")
            for row, teks in P.required(script):
                want = {norm(x) for x in re.split(r"[\s/·:,.?*-]+", teks)} - {""} - _sc().STOP
                if want and len(want & shown) < 0.6 * len(want):
                    probs.append(f"the script asks for on-screen text \"{teks}\" (row {row}) and no card shows it: "
                                 "run plan again, do not drop a card the script asks for")
    kw = sb.get("kept_words", [])
    stop = _sc().STOP
    for o in D["overlays"]:
        checks = []
        if o["type"] == "term":
            checks.append(("title", o.get("title", ""), o["start"] - 3, o["end"] + 1))
        if o["type"] == "stat":
            checks.append(("value", str(o.get("value", "")), o["start"] - 3, o["end"] + 1))
        for it in o.get("items") or []:
            if isinstance(it, dict) and it.get("t") is not None:
                checks.append(("item", it.get("text", ""), it["t"] - 3, it["t"] + 3))
        for field, txt, a, b in checks:
            toks = {norm(t) for t in re.split(r"[\s/·:,.-]+", txt) if norm(t) and norm(t) not in stop}
            toks |= {NUM_WORDS[t] for t in list(toks) if t in NUM_WORDS}
            said = [w["o"] for w in kw if norm(w["w"]) in toks]
            if said and not any(a <= t <= b for t in said):
                near = min(said, key=lambda t: abs(t - o["start"]))
                probs.append(f"overlay at {o['start']:.1f}s ({o['type']}) {field} \"{txt}\" is on screen before/after "
                             f"it is said (said at {near:.1f}s in the output). Put the card's at on the word")
    for a, b, said in retakes(kw, stoks):
        probs.append(f"retake still in the cut: \"{said}\" is said twice. Run align, or add drop [{a}, {b}]")
    for o in D["overlays"]:
        T = o["type"]
        extra = set(o) - COMMON - FIELDS.get(T, set())
        if T not in FIELDS:
            probs.append(f"overlay at {o['start']:.1f}s: unknown type {T}")
            continue
        if extra:
            probs.append(f"overlay at {o['start']:.1f}s ({T}) ignores {sorted(extra)}: a {T} shows only "
                         f"{sorted(FIELDS[T])}")
        if not o.get(NEEDS[T]):
            probs.append(f"overlay at {o['start']:.1f}s ({T}) has no {NEEDS[T]}: it renders empty")
    for o in D["overlays"]:
        names = [o.get("icon")] + [i.get("icon") if isinstance(i, dict) else i for i in o.get("icons") or []] + \
                [it.get("icon") for it in o.get("items") or [] if isinstance(it, dict)]
        bad = sorted({n for n in names if n and n not in ICON_NAMES})
        if bad:
            probs.append(f"overlay at {o['start']:.1f}s ({o['type']}) uses icons {bad}: the icons are {sorted(ICON_NAMES)}")
    for r in report:
        if r["type"] not in ("stat", "endcard", "prop", "props") and len(r.get("text", "x")) < 2:
            probs.append(f"overlay {r['id']} ({r['type']}) renders with no visible text")
        if r["type"] in ("prop", "props") and not r.get("icons", 1):
            probs.append(f"overlay {r['id']} ({r['type']}) renders with no picture")
        if r["mode"] == "takeover" or r["type"] == "endcard":
            continue
        x, y, w, h = r["box"]
        if r["off_canvas"]:
            probs.append(f"overlay {r['id']} ({r['type']}) runs off the canvas")
        if r["overflow"]:
            probs.append(f"overlay {r['id']} ({r['type']}) text overflows: shorten it")
        if y + h > r.get("safe_bottom", 1632) + 2:
            probs.append(f"overlay {r['id']} ({r['type']}) reaches y={y + h}, under the TikTok/Reels buttons "
                         f"(keep above {r.get('safe_bottom', 1632)}): shorten it or set place")
        for f in r.get("faces") or ([r["face"]] if r.get("face") else []):
            fx, fy, fw, fh = f
            ix = max(0, min(x + w, fx + fw) - max(x, fx))
            iy = max(0, min(y + h, fy + fh) - max(y, fy))
            if ix * iy > 0.08 * fw * fh:
                probs.append(f"overlay {r['id']} ({r['type']}) covers {100 * ix * iy / (fw * fh):.0f}% of the face "
                             f"(slot {r['slot']}): shorten it, set place, or use mode takeover")
                break
        if D.get("layout") != "full" and (x < I["x"] - 2 or x + w > I["x"] + I["w"] + 2):
            probs.append(f"overlay {r['id']} ({r['type']}) sticks out of the inset")
    lim = sb.get("limits") or {}
    if lim.get("duration"):
        lo, hi = lim["duration"]
        if not lo <= D["duration"] <= hi:
            probs.append(f"the video is {D['duration']:.1f}s; the rules in the pack say {lo}-{hi}s")
    if lim.get("cover_share"):
        cover = sum(o["end"] - o["start"] for o in D["overlays"] if o.get("mode") == "takeover")
        cover += sum(o.get("slate", 0) for o in D["overlays"])   # a slate replaces the footage too
        cover += sum(o["end"] - o["start"] for o in D["overlays"] if o["type"] == "punch")
        cover += sb.get("hold", 0)
        if cover > lim["cover_share"] * D["duration"]:
            probs.append(f"animation covers the footage for {cover:.1f}s of {D['duration']:.1f}s; the rules in the pack "
                         f"allow {lim['cover_share']:.0%}: fewer takeovers, or shorter slates (\"slate\": 0.8)")
    # rhythm: the v1 reference changes picture every ~0.9 s. A frame that holds longer than this
    # with nothing new on it is the "just a frame" the users rejected
    if D.get("layout") == "full":
        edges = sorted({0.0, sb["content"]} | {b["s"] for b in sb["beats"]} |
                       {t for o in D["overlays"] for t in (o["start"], o["start"] + o.get("slate", 0), o["end"])})
        gaps = [(a, b) for a, b in zip(edges, edges[1:]) if b - a > MAX_BEAT + 1.2 and a < sb["content"]]
        for a, b in gaps:
            probs.append(f"the picture does not change from {a:.1f}s to {b:.1f}s ({b - a:.1f}s): add a card or "
                         "lower \"beat\"")
    ovs = sorted([o for o in D["overlays"] if o["type"] != "chip"], key=lambda o: o["start"])
    for a, b in zip(ovs, ovs[1:]):
        if b["start"] < a["end"] - 0.05:
            probs.append(f"overlays at {a['start']:.1f}s and {b['start']:.1f}s overlap in time: one thing at a time")
    for o in D["overlays"]:
        if o["type"] == "punch" and not 0.3 <= o["end"] - o["start"] <= 1.2:
            probs.append(f"punch at {o['start']:.1f}s is {o['end'] - o['start']:.1f}s: a punch is a cut, 0.3-1.2 s")
        if o["end"] - o["start"] < 2.0 and o["type"] not in ("chip", "endcard", "punch"):
            probs.append(f"overlay at {o['start']:.1f}s is on screen {o['end'] - o['start']:.1f}s: too short to read "
                         "(min 2 s; move until later)")
        if o.get("mode") == "takeover" and o["type"] not in TAKEOVER:
            probs.append(f"overlay at {o['start']:.1f}s: a {o['type']} cannot take over the inset "
                         f"(only {sorted(TAKEOVER)})")
        for k, it in enumerate(o.get("items") or []):
            if isinstance(it, dict) and it.get("t") is not None and not (o["start"] <= it["t"] <= o["end"] - 0.8):
                probs.append(f"overlay at {o['start']:.1f}s ({o['type']}) item {k + 1} \"{it.get('text')}\" appears at "
                             f"{it['t']:.1f}s, outside the card ({o['start']:.1f}-{o['end']:.1f}s): it never shows. "
                             "Move the card's until later or the item earlier")
    for c in D["captions"]:
        if len(" ".join(c["w"])) > 30:
            probs.append(f"caption at {c['s']:.1f}s is {len(' '.join(c['w']))} chars: lower caption_words")
    if len(D["title"]) > 44:
        probs.append("title over 44 characters: it will wrap to three lines")
    return probs


# ------------------------------------------------------------------ render
# draft is for judging the edit (layout, timing, words), not the picture: a human picks
# the delivery quality afterwards and re-renders the same edl once with --quality final
QUALITY = {"draft": {"fps": 24, "w": 480, "h": 854, "crf": 30, "preset": "veryfast", "ab": "96k"},
           "final": {"fps": 30, "w": 1080, "h": 1920, "crf": 18, "preset": "medium", "ab": "192k"}}


def _lock(out: str) -> Path:
    return Path(out + ".rendering")


def render(src: str, words: str, face: str, edl_path: str, out: str, quality: str = "draft", preview=None):
    """Writes <out> only when the render is complete (a partial file is never visible),
    and refuses to start while another render of the same <out> is running."""
    lock = _lock(out)
    if lock.exists() and (__import__("time").time() - lock.stat().st_mtime) < 1800:
        die(f"a render of {out} is already running (started {lock.read_text()}). Wait for it: it is done when "
            "its log's last line starts with 'wrote'. Do not start another one.")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(__import__("time").strftime("%H:%M:%S"))
    try:
        _render(src, words, face, edl_path, out, quality, preview)
    finally:
        lock.unlink(missing_ok=True)


def grade_of(src: str, mode) -> str:
    """Light correction for phone footage: contrast +5 and a little exposure (the pack guides ask
    for exactly that), and more lift in the mid-tones when the room was dark. "none" turns it off;
    a dict is passed to ffmpeg eq as is."""
    if mode in (None, False, "none"):
        return ""
    if isinstance(mode, dict):
        return "eq=" + ":".join(f"{k}={v}" for k, v in mode.items()) + ","
    cache = Path(src + ".luma.json")
    if cache.exists():
        y = read_json(str(cache))["yavg"]
    else:
        r = subprocess.run(["ffmpeg", "-v", "info", "-i", src, "-vf",
                            "fps=0.5,scale=96:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG",
                            "-an", "-f", "null", "-"], capture_output=True, text=True, errors="replace")
        vals = [float(v) for v in re.findall(r"YAVG=([\d.]+)", r.stderr)]
        y = sum(vals) / len(vals) if vals else 110.0
        write_json(str(cache), {"yavg": round(y, 1)})
    gamma = max(1.0, min(1.25, 1 + (100 - y) / 220))
    return f"eq=contrast=1.05:brightness=0.02:saturation=1.05:gamma={gamma:.2f},"


def _render(src: str, words: str, face: str, edl_path: str, out: str, quality: str, preview):
    Q = QUALITY[quality]
    fps = Q["fps"]
    edl = load_edl(edl_path)
    sb = storyboard(src, words, face, edl)
    D = sb["data"]
    write_json(str(Path(out).with_suffix(".storyboard.json")), sb)
    ov = Overlay(D, scale=Q["w"] / 1080)
    probs = lint(sb, ov.report())
    for p in probs:
        log("LINT " + p)
    if probs and not edl.get("force"):
        ov.close()
        die(f"{len(probs)} lint problem(s): fix the edl and run lint again")
    total = D["duration"] if preview is None else min(D["duration"], preview)
    I = D["inset"]
    sel = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in sb["keep"])

    def piece(k):                                    # per-shot crop, piecewise on SOURCE time
        expr = str(sb["crops"][-1][k])
        for c in reversed(sb["crops"][:-1]):
            expr = f"if(lt(t,{c['end']:.3f}),{c[k]},{expr})"
        return expr
    bg = D["colors"]["bg"].lstrip("#")
    grade = grade_of(src, sb["grade"])
    wide = f"scale={sb['vw']}:{sb['vh']},crop={I['w']}:{I['h']}:'{piece('x')}':'{piece('y')}'"
    if sb["zoomed"]:                                 # punch-in: the tight frame replaces the wide one on its spans
        zsel = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in sb["zoomed"])
        speaker = (f"[0:v]fps={fps},{grade}split=2[w0][z0];[w0]{wide}[wide];"
                   f"[z0]scale={sb['vwz']}:{sb['vhz']},crop={I['w']}:{I['h']}:'{piece('zx')}':'{piece('zy')}'[tight];"
                   f"[wide][tight]overlay=0:0:enable='{zsel}',")
    else:
        speaker = f"[0:v]fps={fps},{grade}{wide},"
    content, hold = sb["content"], sb["hold"]
    # every kept piece gets a 30 ms fade in and out so no join clicks (a raw aselect splice pops)
    K = sb["keep"]
    afx = "".join(f"[k{i}]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,"
                  f"afade=t=out:st={max(0.0, e - s - 0.03):.3f}:d=0.03[c{i}];" for i, (s, e) in enumerate(K))
    audio = (f"[0:a]asplit={len(K)}" + "".join(f"[k{i}]" for i in range(len(K))) + ";" + afx
             + "".join(f"[c{i}]" for i in range(len(K))) + f"concat=n={len(K)}:v=0:a=1,"
             f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,"
             f"afade=t=out:st={max(0.0, content - 0.3):.3f}:d=0.3,apad=pad_dur={hold + 1:.2f}[a];")
    work = Path(tempfile.mkdtemp(prefix="sc_studio_"))
    amap = "[a]"
    if D.get("layout") == "full":
        SW, SH = sb["size"]
        if abs(SW / SH - 9 / 16) > 0.01:
            die(f"the full layout needs a 9:16 source ({SW}x{SH} given): run join first")
        # pass 1: cut + framing + audio into an intermediate file. zoompan in the same process as the
        # slow PNG pipe made ffmpeg stop at ~32 s and still exit 0, so the two never share a process
        up = "scale=2160:3840:flags=bicubic," if quality == "final" else ""   # finer zoompan steps, no jitter
        fc1 = (f"[0:v]fps={fps},{grade}select='{sel}',setpts=N/({fps}*TB),{up}"
               f"{zoompan_of(sb['beats'], fps, str(Q['w']) + 'x' + str(Q['h']))},setsar=1,"
               f"tpad=stop_mode=clone:stop_duration={hold + 1:.2f}[v];" + audio.rstrip(";"))
        extra = []
        if edl.get("music", True) is not False:
            # the pack scores "music under the voice, cut on the beat": an original bed + card sounds
            sys.path.insert(0, str(HERE))
            from soundbed import soundtrack  # noqa: E402
            bedp = str(work / "bed.wav")
            soundtrack(D, sb["kept_words"], total + 0.5, bedp)
            fc1 = fc1[:-len("[a]")] + "[vo];[1:a]aformat=sample_rates=48000:channel_layouts=stereo[bd];" \
                  "[vo]aformat=sample_rates=48000:channel_layouts=stereo[vs];" \
                  "[vs][bd]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.79," \
                  "loudnorm=I=-14:TP=-2:LRA=11,aresample=48000[a]"   # the bed + hits push the voice-only level up; re-pin the mix
            extra = ["-i", bedp]
        (work / "fc1.txt").write_text(fc1, encoding="utf-8")
        base = str(work / "base.mkv")
        log("pass 1: footage, framing, audio" + (", music" if extra else ""))
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, *extra, "-filter_complex_script", str(work / "fc1.txt"),
                            "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "ultrafast",
                            "-crf", "8" if quality == "final" else "14", "-c:a", "pcm_s16le", base],
                           capture_output=True, text=True, errors="replace")
        if r.returncode != 0 or not Path(base).exists():
            ov.close()
            shutil.rmtree(work, ignore_errors=True)
            die("ffmpeg pass 1 failed: " + r.stderr[-800:])
        src, amap = base, "0:a"
        fc = f"[1:v]format=rgba,scale={Q['w']}:{Q['h']}[ov];[0:v][ov]overlay=0:0:format=auto,format=yuv420p[v]"
    else:
        fc = (speaker + f"select='{sel}',setpts=N/({fps}*TB),setsar=1,tpad=stop_mode=clone:stop_duration={hold + 1:.2f}[sp];"
              + audio + f"color=c=0x{bg}:s=1080x1920:r={fps}[bg];"
              f"[bg][sp]overlay={I['x']}:{I['y']}:shortest=1[base];"
              f"[1:v]format=rgba,scale=1080:1920[ov];[base][ov]overlay=0:0:format=auto,"
              f"scale={Q['w']}:{Q['h']}:flags=bicubic,format=yuv420p[v]")
    (work / "fc.txt").write_text(fc, encoding="utf-8")
    part = str(Path(out).with_name(Path(out).stem + ".partial" + Path(out).suffix))
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png",
           "-i", "-", "-filter_complex_script", str(work / "fc.txt"), "-map", "[v]", "-map", amap,
           "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", Q["preset"], "-crf", str(Q["crf"]), "-r", str(fps),
           "-c:a", "aac", "-b:a", Q["ab"], "-movflags", "+faststart", part]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(math.ceil(total * fps)) + 1
    last_sig, png, uniq = None, None, 0
    try:
        for i in range(n):
            sig = ov.frame(i / fps)
            if sig != last_sig:
                png = ov.shot()
                uniq += 1
                last_sig = sig
            proc.stdin.write(png)
            if i % (fps * 10) == 0:
                log(f"frame {i}/{n} ({uniq} unique)")
        proc.stdin.close()
    except BrokenPipeError:
        log(f"ffmpeg stopped reading the overlay at frame {i} of {n}")
    rc = proc.wait()
    ov.close()
    shutil.rmtree(work, ignore_errors=True)
    if rc != 0:
        Path(part).unlink(missing_ok=True)
        die("ffmpeg compose failed")
    # a short file must never pass as finished: check every stream against the planned length
    got = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", part],
                         capture_output=True, text=True, errors="replace")
    streams = json.loads(got.stdout or "{}").get("streams", [])
    short = [f"{s['codec_type']} {float(s.get('duration', 0)):.1f}s" for s in streams
             if float(s.get("duration", 0)) < total - 0.5]
    if len(streams) < 2 or short:
        Path(part).unlink(missing_ok=True)
        die(f"render came out short ({', '.join(short) or 'a stream is missing'}; planned {total:.1f}s): "
            "the file was deleted. Render again; if it repeats, report it")
    os.replace(part, out)
    log(f"wrote {out} ({quality} {Q['w']}x{Q['h']}@{fps}, {total:.1f}s, {uniq} unique overlay frames of {n})")


def cards(video: str, out: str | None = None) -> str:
    """One image: the rendered frame in the middle of every card, labelled with what the
    edl says should be there. The editor looks at this one image before handing over;
    a frame with no card, or a card that differs from its label, is a failed render."""
    from PIL import Image, ImageDraw, ImageFont
    if _lock(video).exists():
        die(f"{video} is still rendering. Wait until the render log's last line starts with 'wrote', then run cards.")
    if not Path(video).exists():
        die(f"{video} does not exist: the render did not finish. Read the render log.")
    sb = read_json(str(Path(video).with_suffix(".storyboard.json")))
    ovs = sb["data"]["overlays"]
    total = sb["data"]["duration"]
    out = out or str(Path(video).with_name(Path(video).stem + ".cards.jpg"))
    tw, th, lab = 300, 534, 64
    cells = []
    work = Path(tempfile.mkdtemp(prefix="sc_cards_"))
    for k, o in enumerate(ovs):
        t = min((o["start"] + min(o["end"], total)) / 2, total - 0.1)
        if o["type"] in ("list", "flow") and o.get("items"):
            t = min(max(t, max(it.get("t", 0) for it in o["items"]) + 0.5), min(o["end"], total) - 0.1)
        p = work / f"c{k:02d}.png"
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                            "-vf", f"scale={tw}:{th}", str(p)], capture_output=True, text=True, errors="replace")
        if r.returncode != 0 or not p.exists():
            die(f"cannot read a frame at {t:.1f}s from {video}: the file is damaged (a render was interrupted or "
                "two ran at once). Render once more, in the foreground, and wait for 'wrote'.")
        words = " ".join(x for _, x in card_text(o))[:70]
        cells.append((Image.open(p).convert("RGB"), f"{k + 1}. {o['type']} @{t:.1f}s", words))
    cols = min(4, max(1, len(cells)))
    rows = math.ceil(len(cells) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * (th + lab)), "white")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    for k, (im, head, words) in enumerate(cells):
        x, y = (k % cols) * tw, (k // cols) * (th + lab)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + th + 4), head, fill="black", font=font)
        d.text((x + 6, y + th + 24), words[:38], fill="#444", font=font)
        d.text((x + 6, y + th + 42), words[38:], fill="#444", font=font)
    sheet.save(out, quality=88)
    shutil.rmtree(work, ignore_errors=True)
    log(f"wrote {out}: {len(cells)} cards. Look at it: every cell must show the card its label names")
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="studio", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("join")
    s.add_argument("clips", nargs="+")
    s.add_argument("-o", "--out", required=True)
    s = sub.add_parser("track")
    s.add_argument("src")
    s.add_argument("-o", "--out", required=True)
    s.add_argument("--shots")
    s = sub.add_parser("align", help="transcript vs script: writes script, fix_at and drop into the edl")
    s.add_argument("--words", required=True)
    s.add_argument("--script", required=True, nargs="+", help="every script for this video; the best match wins")
    s.add_argument("--edl")
    s = sub.add_parser("plan", help="script table -> every card and prop the script asks for, timed to the words")
    s.add_argument("--words", required=True)
    s.add_argument("--script", required=True, nargs="+", help="every script for this video (table + read-aloud)")
    s.add_argument("--edl", required=True)
    s = sub.add_parser("cards", help="one image with the rendered frame of every card")
    s.add_argument("video")
    s.add_argument("-o", "--out")
    for name in ("lint", "render"):
        s = sub.add_parser(name)
        s.add_argument("src")
        s.add_argument("--words", required=True)
        s.add_argument("--face", required=True)
        s.add_argument("--edl", required=True)
        if name == "render":
            s.add_argument("-o", "--out", required=True)
            s.add_argument("--preview", type=float)
            s.add_argument("--quality", choices=list(QUALITY), default="draft")
    a = ap.parse_args()
    if a.cmd == "join":
        join(a.clips, a.out)
    elif a.cmd == "track":
        track(a.src, a.out, a.shots or (a.src + ".shots.json"))
    elif a.cmd == "align":
        print(json.dumps(align(a.words, a.script, a.edl), indent=2, ensure_ascii=False))
    elif a.cmd == "plan":
        import plan as P
        print(P.show(P.plan(a.words, a.script, a.edl)))
    elif a.cmd == "cards":
        cards(a.video, a.out)
    elif a.cmd == "lint":
        sb = storyboard(a.src, a.words, a.face, load_edl(a.edl))
        ov = Overlay(sb["data"])
        probs = lint(sb, ov.report())
        ov.close()
        print(json.dumps({"problems": probs, "duration": sb["data"]["duration"], "captions": len(sb["data"]["captions"]),
                          "keep": sb["keep"]}, indent=2, ensure_ascii=False))
        sys.exit(1 if probs else 0)
    else:
        render(a.src, a.words, a.face, a.edl, a.out, a.quality, preview=a.preview)


if __name__ == "__main__":
    main()
