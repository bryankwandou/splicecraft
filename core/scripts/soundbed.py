"""Original music bed + sound effects for a studio render, synthesised here (no samples, no
licence needed). The pack's craft rule is "music under the voice, cut on the beat": the bed sits
well under the speech, dips further on every word, comes up in pauses and on the end card, and a
soft whoosh / pop / tick marks each card, each prop landing and each list item.

    soundtrack(data, kept_words, total, path)  -> writes a 48 kHz stereo WAV of length `total`
"""
import wave

import numpy as np

SR = 48000
BPM = 92
# Am - F - C - G, two bars each: calm, hopeful, not "luxury"
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _env(n, a, r):
    e = np.ones(n)
    a, r = min(a, n), min(r, n)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def _bed(total, rng):
    n = int(total * SR) + SR
    out = np.zeros((n, 2))
    beat = 60 / BPM
    bar = beat * 4
    t = np.arange(n) / SR
    # pad: each chord for 2 bars, detuned sines left/right, slow attack and release
    k = 0
    while k * 2 * bar < total + 2 * bar:
        s0 = int(k * 2 * bar * SR)
        if s0 >= n:
            break
        ln = int(2 * bar * SR)
        seg = np.arange(ln) / SR
        env = _env(ln, int(0.9 * SR), int(0.9 * SR))
        for m in CHORDS[k % len(CHORDS)]:
            f = _hz(m)
            for ch, det in ((0, 0.997), (1, 1.003)):
                v = np.sin(2 * np.pi * f * det * seg) + 0.25 * np.sin(2 * np.pi * 2 * f * det * seg)
                e = min(n, s0 + ln) - s0
                out[s0:s0 + e, ch] += 0.055 * (v * env)[:e]
        # bass: root an octave down, on beats 1 and 3
        root = _hz(CHORDS[k % len(CHORDS)][0] - 12)
        for b in range(8):
            if b % 2:
                continue
            p = s0 + int(b * beat * SR)
            ln2 = int(beat * 1.6 * SR)
            if p + ln2 > n:
                break
            sg = np.arange(ln2) / SR
            out[p:p + ln2] += (0.10 * np.sin(2 * np.pi * root * sg) * np.exp(-sg * 2.2))[:, None]
        # pluck arpeggio on eighth notes
        notes = list(CHORDS[k % len(CHORDS)]) + [CHORDS[k % len(CHORDS)][1] + 12]
        for e8 in range(16):
            p = s0 + int(e8 * beat / 2 * SR)
            ln3 = int(0.5 * SR)
            if p + ln3 > n:
                break
            f = _hz(notes[(e8 * 3) % len(notes)] + 12)
            sg = np.arange(ln3) / SR
            v = (np.sin(2 * np.pi * f * sg) + 0.3 * np.sin(2 * np.pi * 3 * f * sg)) * np.exp(-sg * 9)
            pan = 0.35 + 0.3 * ((e8 % 4) / 3)
            out[p:p + ln3, 0] += 0.035 * v * (1 - pan)
            out[p:p + ln3, 1] += 0.035 * v * pan
        k += 1
    # soft kick on every beat, shaker on the off-beats
    nb = int(total / beat) + 2
    for b in range(nb):
        p = int(b * beat * SR)
        ln = int(0.18 * SR)
        if p + ln > n:
            break
        sg = np.arange(ln) / SR
        kick = np.sin(2 * np.pi * (50 + 70 * np.exp(-sg * 30)) * sg) * np.exp(-sg * 18)
        out[p:p + ln] += (0.09 * kick)[:, None]
        q = int((b + 0.5) * beat * SR)
        ln = int(0.05 * SR)
        if q + ln > n:
            break
        sh = rng.standard_normal(ln) * np.exp(-np.arange(ln) / SR * 70)
        sh = np.diff(sh, prepend=0)                     # high-passed noise
        out[q:q + ln] += (0.012 * sh)[:, None]
    return out[:int(total * SR)], t


def _whoosh(rng):
    ln = int(0.42 * SR)
    sg = np.arange(ln) / SR
    noise = rng.standard_normal(ln)
    # one-pole low-pass whose cutoff sweeps up: a rising "shh"
    y, a, acc = np.zeros(ln), np.linspace(0.02, 0.35, ln), 0.0
    for i in range(ln):
        acc += a[i] * (noise[i] - acc)
        y[i] = acc
    env = np.sin(np.pi * np.clip(sg / 0.42, 0, 1)) ** 2
    return 0.22 * y * env


def _pop():
    ln = int(0.11 * SR)
    sg = np.arange(ln) / SR
    f = 620 * np.exp(-sg * 9) + 260
    return 0.20 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-sg * 34)


def _tick():
    ln = int(0.06 * SR)
    sg = np.arange(ln) / SR
    return 0.10 * np.sin(2 * np.pi * 1320 * sg) * np.exp(-sg * 70)


def _add(buf, at, snd, pan=0.5):
    p = int(at * SR)
    if p < 0 or p >= len(buf):
        return
    e = min(len(buf), p + len(snd))
    buf[p:e, 0] += snd[:e - p] * (1 - pan) * 2 * 0.7
    buf[p:e, 1] += snd[:e - p] * pan * 2 * 0.7


def soundtrack(data: dict, kept_words: list, total: float, path: str):
    rng = np.random.default_rng(49)
    bed, t = _bed(total, rng)
    n = len(bed)
    # level: under the voice always, a further dip on every spoken word, up in pauses / end card
    gain = np.full(n, 0.55)
    starts = [w["o"] for w in kept_words]
    for k, s in enumerate(starts):
        e = min(starts[k + 1] if k + 1 < len(starts) else s + 0.5, s + 0.6)
        gain[int(max(0, s - 0.05) * SR):int(min(total, e + 0.12) * SR)] = 0.28
    end = next((o["start"] for o in data["overlays"] if o["type"] == "endcard"), None)
    if end is not None:
        gain[int(end * SR):] = 1.0
    win = int(0.25 * SR)                               # smooth the dips so they never pump
    c = np.concatenate(([0.0], np.cumsum(np.pad(gain, (win // 2, win - win // 2 - 1), mode="edge"))))
    gain = (c[win:] - c[:-win]) / win               # moving average via cumsum: np.convolve here is O(n*win)
    bed *= gain[:, None]
    bed *= _env(n, int(0.6 * SR), int(1.2 * SR))[:, None]
    fx = np.zeros_like(bed)
    who, pop, tick = _whoosh(rng), _pop(), _tick()
    for o in data["overlays"]:
        if o["type"] == "chip":
            continue
        if o["type"] == "punch":                                        # a hard cut: a hit, no whoosh
            _add(fx, o["start"], pop * 1.3)
            _add(fx, o["start"], tick * 1.5)
            continue
        _add(fx, o["start"] - 0.25, who)
        if o.get("slate"):
            _add(fx, o["start"] + o["slate"] - 0.2, who * 0.6, 0.6)   # slate -> sheet
        for k, it in enumerate(o.get("items") or []):
            at = it.get("t")
            if at is None:
                continue
            if o["type"] == "props":
                _add(fx, at + 1.2, pop, 0.4 + 0.2 * (k % 2))           # the object lands in its tile
            else:
                _add(fx, at, tick)
    mix = np.clip(bed + fx, -0.98, 0.98)
    pcm = (mix * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
