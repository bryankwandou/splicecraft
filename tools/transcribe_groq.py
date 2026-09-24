"""Groq Whisper (whisper-large-v3) transcription, the cloud half of the hybrid.

Usage: python tools/transcribe_groq.py <src_dir> <out_dir>
Works largest-first, so it meets the local worker (smallest-first) in the middle.
Same output format and skip rule as transcribe_local.py. Needs GROQ_API_KEY.
"""
import glob, json, os, subprocess, sys, tempfile, time, urllib.request, uuid

def ts(s):
    h, r = divmod(int(s), 3600); m, s2 = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s2:02d}"

src, outd = sys.argv[1], sys.argv[2]
KEY = os.environ["GROQ_API_KEY"]
PROMPT = ("SpliceCraft Academy, the SpliceCraft Academy founder, personal branding, konten, content creator, hook, CTA, "
          "TikTok, Instagram, Reels, LinkedIn, superniche, premis, storytelling, algoritma, followers, engagement.")
seen, uniq = set(), []
for f in sorted(glob.glob(os.path.join(src, "*.mp4"))):
    sz = os.path.getsize(f)
    if sz not in seen: seen.add(sz); uniq.append(f)
uniq.sort(key=os.path.getsize, reverse=True)

def post(path):
    b = uuid.uuid4().hex; data = open(path, "rb").read()
    parts = []
    for k, v in (("model", "whisper-large-v3"), ("language", "id"), ("response_format", "verbose_json"), ("prompt", PROMPT)):
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + data + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=b"".join(parts),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": f"multipart/form-data; boundary={b}", "User-Agent": "splicecraft"})
    return json.load(urllib.request.urlopen(req, timeout=600))

for f in uniq:
    base = os.path.splitext(os.path.basename(f))[0]
    out = os.path.join(outd, base + ".txt")
    if os.path.exists(out) or os.path.exists(out + ".groq"): continue
    open(out + ".groq", "w").close()
    t0 = time.time()
    mp3 = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + ".mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k", mp3], check=True)
    d = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-f", "segment", "-segment_time", "1200", "-c", "copy", os.path.join(d, "c%03d.mp3")], check=True)
    os.remove(mp3)
    r, ok = {"segments": [], "duration": 0}, True
    for i, c in enumerate(sorted(glob.glob(os.path.join(d, "c*.mp3")))):
        for attempt in range(8):
            try: part = post(c); break
            except urllib.error.HTTPError as e:
                wait = int(e.headers.get("retry-after", 60)) if e.code == 429 else 20
                print(f"retry {base} chunk {i}: HTTP {e.code}, waiting {wait}s", flush=True); time.sleep(wait)
        else:
            ok = False; break
        off = i * 1200
        for sg in part.get("segments", []): sg["start"] += off
        r["segments"] += part.get("segments", []); r["duration"] = off + part.get("duration", 0)
    for c in glob.glob(os.path.join(d, "*")): os.remove(c)
    os.rmdir(d)
    if not ok:
        os.remove(out + ".groq"); continue
    segs = [s for s in r.get("segments", []) if s["text"].strip()]
    if os.path.exists(out): os.remove(out + ".groq"); continue  # local finished first
    with open(out + ".part", "w", encoding="utf-8") as fh:
        fh.write(f"# {base}\n# duration {r.get('duration', 0):.0f}s · model whisper-large-v3 · Groq\n\n")
        fh.write("\n".join(f"[{ts(s['start'])}] {s['text'].strip()}" for s in segs) + "\n")
    with open(os.path.join(outd, base + ".plain.txt"), "w", encoding="utf-8") as fh:
        fh.write(" ".join(s["text"].strip() for s in segs) + "\n")
    os.replace(out + ".part", out); os.remove(out + ".groq")
    print(f"DONE[groq] {base} | {r.get('duration',0):.0f}s audio in {time.time()-t0:.0f}s", flush=True)
print("GROQ DONE", flush=True)
