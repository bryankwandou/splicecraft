"""Offline transcription with faster-whisper (no API, runs on CPU).

Usage: python tools/transcribe_local.py <src_dir> <out_dir> [--model small] [--glob *.mp4]
Resumable: a file whose .txt already exists is skipped. Byte-identical
duplicates (same size) are transcribed once.
Writes <name>.txt (timestamped lines) and <name>.plain.txt (text only).
"""
import argparse, glob, os, sys, time
from faster_whisper import WhisperModel

def ts(s):
    h, r = divmod(int(s), 3600); m, s2 = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s2:02d}"

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--model", default="small")
ap.add_argument("--glob", default="*.mp4")
ap.add_argument("--order", default="size", choices=["size", "name"])
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
files = glob.glob(os.path.join(a.src, a.glob))
seen, uniq = set(), []
for f in sorted(files):
    sz = os.path.getsize(f)
    if sz in seen:
        print("DUP skip:", os.path.basename(f), flush=True); continue
    seen.add(sz); uniq.append(f)
if a.order == "size":
    uniq.sort(key=os.path.getsize)
PROMPT = ("Kadev Academy, Kadafi Devayana, personal branding, konten, content creator, hook, CTA, "
          "TikTok, Instagram, Reels, LinkedIn, superniche, premis, storytelling, algoritma, followers, engagement.")
model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
for f in uniq:
    base = os.path.splitext(os.path.basename(f))[0]
    out = os.path.join(a.out, base + ".txt")
    if os.path.exists(out):
        continue
    t0 = time.time()
    segs, info = model.transcribe(f, language="id", beam_size=1, vad_filter=True,
                                  condition_on_previous_text=False,
                                  no_repeat_ngram_size=4, repetition_penalty=1.1,
                                  hallucination_silence_threshold=2.0,
                                  initial_prompt=PROMPT)
    lines, plain = [], []
    budget = time.time() + max(600, 6 * info.duration)
    stalled = False
    for s in segs:
        if time.time() > budget:
            stalled = True; break
        txt = s.text.strip()
        if not txt: continue
        lines.append(f"[{ts(s.start)}] {txt}"); plain.append(txt)
    tmp = out + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(f"# {base}\n# duration {info.duration:.0f}s · model {a.model} · offline faster-whisper\n\n")
        fh.write("\n".join(lines) + "\n")
    with open(os.path.join(a.out, base + ".plain.txt"), "w", encoding="utf-8") as fh:
        fh.write(" ".join(plain) + "\n")
    if stalled:
        with open(tmp, "a", encoding="utf-8") as fh:
            fh.write("\n# STOPPED: exceeded time budget (likely music-only / repetition loop)\n")
    os.replace(tmp, out)
    el = time.time() - t0
    print(f"DONE {base} | {info.duration:.0f}s audio in {el:.0f}s ({info.duration/max(el,1):.1f}x)", flush=True)
print("ALL DONE", flush=True)
