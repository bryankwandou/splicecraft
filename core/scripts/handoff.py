"""Self-check every join of a studio render, then hand the cut to an NLE.

    python handoff.py <render.mp4> <render.storyboard.json> <source.mp4> <words.json>

Writes next to the render:
  <name>.joins.txt  one line per join: mid-word?, click ratio, covered by a framing change / card?
  <name>.edl        CMX3600 cut list (source -> record timecode) for Premiere / Resolve / FCP
  <name>.srt        2-word captions on the record timeline
Exit 1 when any join cuts inside a word, clicks, or the audio and video lengths drift apart.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000


def tc(t, fps):
    f = int(round(t * fps))
    return f"{f // (3600 * fps):02d}:{f // (60 * fps) % 60:02d}:{f // fps % 60:02d}:{f % fps:02d}"


def srt_t(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main(video, sbp, src, wordsp):
    sb = json.load(open(sbp, encoding="utf-8"))
    words = json.load(open(wordsp, encoding="utf-8"))["words"]
    keep = sb["keep"]
    fps = 30
    out = Path(video)
    # record-time position of every join
    joins, acc = [], 0.0
    for i, (s, e) in enumerate(keep):
        acc += e - s
        if i < len(keep) - 1:
            joins.append((acc, e, keep[i + 1][0]))
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(pcm, dtype="<f4")
    d = np.abs(np.diff(a))
    cuts = sorted({round(b["s"], 2) for b in sb["beats"]})
    cards = [(o["start"], o["end"]) for o in sb["data"]["overlays"] if o["type"] != "chip"]
    lines, bad = [], 0
    for t, out_src, in_src in joins:
        mid = [w["w"] for w in words if w["s"] + 0.02 < out_src < w["e"] - 0.02 or w["s"] + 0.02 < in_src < w["e"] - 0.02]
        p = int(t * SR)
        near = d[max(0, p - int(0.004 * SR)):p + int(0.004 * SR)]
        ctx = d[max(0, p - int(0.1 * SR)):p + int(0.1 * SR)]
        click = float(near.max() / (np.median(ctx) + 1e-6)) if len(near) and len(ctx) else 0.0
        reframe = any(abs(c - t) < 0.12 for c in cuts)
        covered = any(a0 - 0.05 <= t <= b0 + 0.05 for a0, b0 in cards)
        ok = not mid and click < 25
        bad += not ok
        lines.append(f"{'OK  ' if ok else 'FAIL'} join {t:6.2f}s  src {out_src:6.2f}->{in_src:6.2f}  "
                     f"mid-word={','.join(mid) or 'no'}  click={click:5.1f}  "
                     f"{'reframed' if reframe else ('under card' if covered else 'JUMP CUT (same framing)')}")
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", video],
                                   capture_output=True, text=True).stdout)
    dur = {s["codec_type"]: float(s["duration"]) for s in pr["streams"]}
    drift = abs(dur["video"] - dur["audio"])
    bad += drift > 0.1
    lines.append(f"{'OK  ' if drift <= 0.1 else 'FAIL'} A/V length drift {drift * 1000:.0f} ms")
    jumps = sum("JUMP CUT" in x for x in lines)
    lines.append(f"{len(joins)} joins, {bad} failing, {jumps} plain jump cuts")
    out.with_suffix(".joins.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # CMX3600: one event per kept piece, source timecode -> record timecode
    ev, rec = [f"TITLE: {out.stem}", "FCM: NON-DROP FRAME", ""], 0.0
    for i, (s, e) in enumerate(keep, 1):
        ev.append(f"{i:03d}  AX       AA/V  C        {tc(s, fps)} {tc(e, fps)} {tc(rec, fps)} {tc(rec + e - s, fps)}")
        ev.append(f"* FROM CLIP NAME: {Path(src).name}")
        rec += e - s
    out.with_suffix(".edl").write_text("\n".join(ev) + "\n", encoding="utf-8")
    kw = sb["kept_words"]
    srt = []
    for n, i in enumerate(range(0, len(kw), 2), 1):
        grp = kw[i:i + 2]
        st = grp[0]["o"]
        en = kw[i + 2]["o"] if i + 2 < len(kw) else st + 0.8
        srt += [str(n), f"{srt_t(st)} --> {srt_t(min(en, st + 1.6))}", " ".join(w["w"] for w in grp), ""]
    out.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")
    print("\n".join(lines[-3:]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
