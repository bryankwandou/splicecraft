#!/usr/bin/env python3
"""
SpliceCraft content ledger — a local memory of what has already been made.

Purpose: stop the agent (and the user) from producing the same script, the same
niche angle, or the same theme twice. Every produced piece is logged on the
user's own machine; every new idea is checked against that log before writing.

Storage: a single JSON file. Default location:
    Windows  %USERPROFILE%\\.splicecraft\\ledger.json
    macOS/Linux  ~/.splicecraft/ledger.json
Override with --store PATH or the SPLICECRAFT_LEDGER environment variable.

The file is plain JSON on purpose: the user owns it, can read it, can edit it in
any text editor, and can copy it between machines. Nothing is sent anywhere.

Standard library only. Python 3.9+.

Commands
    init                     create the store
    add                      log a produced piece
    check "<topic>"          similarity check before writing (exit 2 = too close)
    list                     recent entries
    stats                    pillar balance, niche mix, cadence
    suggest                  what is under-used / due next
    show <id>                one entry in full
    edit <id> --field=value  amend an entry
    remove <id>              delete an entry
    export --format md|csv   dump for the user
    themes                   what themes have been covered, ranked

Exit codes
    0  fine
    2  `check` found a collision at or above the block threshold
    1  usage or IO error
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import os
import re
import sys
import unicodedata
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SCHEMA_VERSION = 1

# Thresholds for `check`. Tuned so that a genuinely new angle on a familiar
# topic passes, but a rewording of an existing script does not.
WARN_AT = 0.45
BLOCK_AT = 0.62

PILLARS = ("educate", "inspiration", "entertaining", "promotion")

# The formats named in the "Topik Format Winning" mentoring
# (references/kadev-live-mentoring.md §1). Free text is still accepted, with a
# warning, because new formats appear faster than this list is updated.
FORMATS = (
    "talking_head_greenscreen", "single_post", "dialog", "tunjuk_tunjuk",
    "jangan_x_tapi_y", "carousel", "10x10", "talking_head", "music_text",
    "yapping", "comparison", "storytelling_7s", "motivational",
    "day_in_my_life", "carousel_storytelling",
)
# kadev-live-mentoring.md §5: tahu -> mau -> beli/follow.
FUNNEL = ("tofu", "mofu", "bofu")

# What `edit --set` will accept. Anything else is rejected rather than written,
# so a typo cannot silently add a junk key while the real field stays stale.
EDITABLE_FIELDS = frozenset({
    "date", "topic", "niche", "pillar", "hook", "hook_template", "angle",
    "themes", "premise", "platform", "format", "seconds", "script_path",
    "video_path", "status", "notes", "funnel", "source",
})

# Indonesian + English stopwords. Deliberately broad: these words carry no
# topical signal, and leaving them in makes every script look similar because
# every script is written in the same casual register.
STOPWORDS = {
    # Indonesian function words
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada", "adalah",
    "itu", "ini", "atau", "juga", "akan", "sudah", "belum", "tidak", "gak",
    "ga", "nggak", "bukan", "bisa", "kamu", "aku", "gue", "gua", "saya",
    "kita", "mereka", "dia", "kalau", "kalo", "tapi", "karena", "biar",
    "agar", "jadi", "banget", "aja", "saja", "deh", "sih", "nih", "kok",
    "dong", "ya", "yuk", "lagi", "masih", "harus", "perlu", "mau", "pengen",
    "ingin", "punya", "ada", "apa", "siapa", "kenapa", "gimana", "bagaimana",
    "cara", "kamuu", "dalam", "oleh", "setelah", "sebelum", "sampai",
    "hingga", "seperti", "kayak", "kaya", "buat", "bikin", "pakai", "pake",
    "banyak", "sedikit", "lebih", "paling", "sangat", "terlalu", "cuma",
    "hanya", "semua", "setiap", "orang", "hal", "yg", "utk", "dgn",
    "nya", "pun", "per", "se", "the",
    # English function words
    "a", "an", "of", "to", "in", "on", "for", "with", "is", "are", "was",
    "were", "be", "been", "it", "this", "that", "and", "or", "but", "if",
    "how", "what", "why", "you", "your", "we", "our", "they", "their", "can",
    "will", "not", "no", "do", "does", "did", "have", "has", "had", "from",
    "at", "by", "as", "so", "than", "then", "more", "most", "very", "just",
    # words that appear in nearly every content brief and so carry no signal
    "konten", "content", "video", "tiktok", "reels", "shorts", "instagram",
    "script", "naskah", "tips", "trik",
}

# Light Indonesian stemming. Not linguistically complete — just enough that
# "mengedit"/"editing"/"edit" and "kebiasaan"/"biasa" collapse together.
_PREFIXES = ("meng", "meny", "mem", "men", "me", "peng", "peny", "pem", "pen",
             "pe", "ber", "ter", "di", "ke", "se")
_SUFFIXES = ("kannya", "annya", "nya", "kan", "an", "i", "ing", "s")


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def _stem(word: str) -> str:
    w = word
    for suf in _SUFFIXES:
        if len(w) > len(suf) + 3 and w.endswith(suf):
            w = w[: -len(suf)]
            break
    for pre in _PREFIXES:
        if len(w) > len(pre) + 3 and w.startswith(pre):
            w = w[len(pre):]
            break
    return w


def tokenize(text: str, stem: bool = True) -> List[str]:
    """
    Lowercase, strip punctuation, drop stopwords, optionally crude-stem.

    Stemming is on for similarity scoring, where collapsing "mengedit"/"editing"
    into one token is the point. It is off for the `themes` display, where the
    stemmer produces near-duplicate rows ("prokrastinasi" and "prokrastinas")
    that read as a bug to the user.
    """
    text = _strip_accents(str(text or "")).lower()
    raw = re.findall(r"[a-z0-9]+", text)
    out = []
    for w in raw:
        if len(w) < 3 or w in STOPWORDS:
            continue
        s = _stem(w) if stem else w
        if len(s) >= 3 and s not in STOPWORDS:
            out.append(s)
    return out


def _bigrams(toks: Sequence[str]) -> set:
    return {f"{a}_{b}" for a, b in zip(toks, toks[1:])}


def _pair_score(a_text: str, b_text: str) -> float:
    """
    Unigram overlap + bigram Jaccard.

    Unigrams use the overlap coefficient |A n B| / min(|A|,|B|) rather than
    Jaccard. Jaccard punishes the short side: a five-word topic compared against
    an entry that also carries a hook, an angle and themes scores low purely
    because the union is large, which made real repeats read as "clear".
    Overlap asks the question we actually care about: "is the smaller of these
    two already contained in the other?"

    Bigrams stay Jaccard — they measure shared *phrasing*, where union size is
    meaningful, and they are what separates "same subject, new angle" from
    "same script, reworded".
    """
    ta, tb = tokenize(a_text), tokenize(b_text)
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta), set(tb)
    uni = len(sa & sb) / min(len(sa), len(sb))
    ba, bb = _bigrams(ta), _bigrams(tb)
    bi = (len(ba & bb) / len(ba | bb)) if (ba | bb) else 0.0
    return 0.65 * uni + 0.35 * bi


def similarity(a_text: str, b_text: str,
               a_topic: str = "", b_topic: str = "") -> float:
    """
    How close are these two pieces of content?

    Scored twice and the stronger signal wins:

      * topic-level  - topic and themes only. Catches "you already covered this
        subject" even when the angle, hook and premise differ. Scaled to 0.92 so
        that a pure subject repeat lands in WARN rather than BLOCK: reusing a
        subject with a real new angle is allowed, it just has to be declared.
      * full-text    - everything, including hook, angle and premise. Catches an
        actual rewrite, which should block.

    Taking the max rather than a blend is deliberate. A blend let a strong topic
    collision be averaged away by a distinctive angle string, which is the exact
    failure this ledger exists to prevent.
    """
    full = _pair_score(a_text, b_text)
    topical = 0.0
    if a_topic and b_topic:
        topical = _pair_score(a_topic, b_topic) * 0.92
    return round(max(full, topical), 4)


def theme_coverage(probe_text: str, themes: List[str]) -> float:
    """
    How many of an entry's theme tags does the new request mention?

    Added after a cold-agent test: an entry logged as "Dokumentasi naik IPK
    pakai Pomodoro" (themes pomodoro, ipk, mahasiswa) scored 44% "clear"
    against "jadwal belajar pomodoro buat naikin IPK mahasiswa" - the same
    video - because the agent phrased the topic differently and passed no
    --theme to check. Tags are the one field chosen deliberately, so when the
    probe hits all of them it is the same subject regardless of wording.

    Scaled by how many tags exist, so an entry with a single broad tag
    ("mahasiswa") cannot block everything that mentions students:
    3+ tags all hit -> 0.90 (BLOCK), 2 of 3 -> 0.60 (WARN), 1 tag -> 0.30.
    """
    tags = [set(tokenize(t.replace("-", " "))) for t in themes if t]
    tags = [t for t in tags if t]
    if not tags:
        return 0.0
    probe = set(tokenize(probe_text))
    hits = sum(1 for t in tags if t <= probe)
    return round(0.9 * hits / len(tags) * min(1.0, len(tags) / 3), 4)


# --------------------------------------------------------------------------- store


def default_store() -> Path:
    env = os.environ.get("SPLICECRAFT_LEDGER")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".splicecraft" / "ledger.json"


def _blank() -> Dict[str, Any]:
    return {
        "schema": SCHEMA_VERSION,
        "created": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "note": (
            "SpliceCraft content ledger. Plain JSON, yours to edit. "
            "Each entry is one piece of content you produced. The agent reads "
            "this before writing anything new so it does not repeat a theme."
        ),
        "entries": [],
    }


def load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return _blank()
    try:
        raw = path.read_text(encoding="utf-8-sig")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(
            f"ledger: {path} is not valid JSON ({e}).\n"
            f"It was probably hand-edited. Fix the JSON, or move the file aside "
            f"and run `ledger init` to start fresh."
        )
    if not isinstance(data, dict) or "entries" not in data:
        raise SystemExit(f"ledger: {path} does not look like a ledger file.")
    data.setdefault("schema", SCHEMA_VERSION)
    return data


def save(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _entry_text(e: Dict[str, Any]) -> str:
    """The text fields that define what an entry is 'about'."""
    parts = [
        e.get("topic", ""),
        e.get("hook", ""),
        e.get("angle", ""),
        " ".join(e.get("themes", []) or []),
        e.get("premise", ""),
    ]
    return " ".join(p for p in parts if p)


def _entry_topic(e: Dict[str, Any]) -> str:
    """Just the subject: what it is about, ignoring how it was framed."""
    return " ".join(filter(None, [
        e.get("topic", ""),
        " ".join(e.get("themes", []) or []),
    ]))


def _short(e: Dict[str, Any]) -> str:
    return e.get("id", "")[:8]


def _find(data: Dict[str, Any], ident: str) -> Dict[str, Any]:
    hits = [e for e in data["entries"] if e.get("id", "").startswith(ident)]
    if not hits:
        raise SystemExit(f"ledger: no entry starting with {ident!r}")
    if len(hits) > 1:
        raise SystemExit(
            f"ledger: {ident!r} matches {len(hits)} entries; use more characters"
        )
    return hits[0]


def _today() -> str:
    return _dt.date.today().isoformat()


# --------------------------------------------------------------------------- commands


def cmd_init(args) -> int:
    path = Path(args.store) if args.store else default_store()
    if path.exists() and not args.force:
        data = load(path)
        print(f"ledger already exists: {path} ({len(data['entries'])} entries)")
        return 0
    save(path, _blank())
    print(f"ledger created: {path}")
    print("Nothing leaves this machine. Edit it by hand any time.")
    return 0


def cmd_add(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)

    themes = [t.strip() for t in (args.theme or []) if t.strip()]
    entry = {
        "id": uuid.uuid4().hex,
        "date": args.date or _today(),
        "topic": args.topic,
        "niche": args.niche or "",
        "pillar": (args.pillar or "").lower(),
        "hook": args.hook or "",
        "hook_template": args.hook_template or "",
        "angle": args.angle or "",
        "themes": themes,
        "premise": args.premise or "",
        "platform": args.platform or "",
        "format": (args.format or "").lower(),
        "funnel": (args.funnel or "").lower(),
        "source": args.source or "",
        "seconds": args.seconds,
        "script_path": args.script_path or "",
        "video_path": args.video_path or "",
        "status": args.status or "produced",
        "performance": {},
        "notes": args.notes or "",
    }
    if entry["pillar"] and entry["pillar"] not in PILLARS:
        print(f"warning: pillar {entry['pillar']!r} is not one of {', '.join(PILLARS)}",
              file=sys.stderr)

    if entry["format"] and entry["format"] not in FORMATS:
        print(f"warning: format {entry['format']!r} is not a named format "
              f"({', '.join(FORMATS)})", file=sys.stderr)
    if not entry["source"]:
        print("note: no --source. Where did this idea come from (a question someone "
              "asked, a complaint, a misconception, something you saw)? "
              "kadev-live-mentoring.md sec 2.3", file=sys.stderr)

    # Always report the nearest neighbour, even on add. Logging a near-duplicate
    # is allowed (the user may have decided it is fine) but it must not be silent.
    near = _nearest(data["entries"], _entry_text(entry), _entry_topic(entry), limit=1)
    data["entries"].append(entry)
    save(path, data)

    print(f"logged {_short(entry)}  {entry['date']}  {entry['topic']}")
    if near and near[0][0] >= WARN_AT:
        score, other = near[0]
        print(f"  note: {score:.0%} similar to {_short(other)} "
              f"({other.get('date','')}) {other.get('topic','')}")
    print(f"  store: {path}  ({len(data['entries'])} entries)")
    return 0


def _nearest(entries: Iterable[Dict[str, Any]], text: str, topic: str = "",
             limit: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
    scored = [
        (max(similarity(text, _entry_text(e), topic, _entry_topic(e)),
             theme_coverage(text, e.get("themes", []) or [])), e)
        for e in entries
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:limit]


def cmd_check(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    entries = data["entries"]

    probe = " ".join(filter(None, [args.topic, args.hook or "", args.angle or "",
                                   " ".join(args.theme or [])]))
    if not entries:
        print("ledger is empty - nothing to collide with. Go ahead.")
        return 0

    pool = entries
    if args.niche:
        pool = [e for e in pool if e.get("niche", "").lower() == args.niche.lower()] or entries

    probe_topic = " ".join(filter(None, [args.topic, " ".join(args.theme or [])]))
    near = _nearest(pool, probe, probe_topic, limit=args.limit)
    top = near[0][0] if near else 0.0

    if args.json:
        print(json.dumps({
            "probe": probe,
            "top_score": top,
            "verdict": ("block" if top >= BLOCK_AT
                        else "warn" if top >= WARN_AT else "clear"),
            "matches": [
                {"score": s, "id": e["id"], "date": e.get("date"),
                 "topic": e.get("topic"), "angle": e.get("angle"),
                 "pillar": e.get("pillar"), "themes": e.get("themes", [])}
                for s, e in near
            ],
        }, ensure_ascii=False, indent=2))
    else:
        print(f'checking: "{probe}"')
        print(f"against {len(pool)} entries\n")
        for s, e in near:
            flag = "BLOCK" if s >= BLOCK_AT else "warn " if s >= WARN_AT else "     "
            print(f"  {flag} {s:5.0%}  {_short(e)}  {e.get('date','')}  "
                  f"{e.get('topic','')}")
            if e.get("angle"):
                print(f"              angle: {e['angle']}")
        print()
        if top >= BLOCK_AT:
            print("VERDICT: too close. Do not write this.")
            print("Change the angle, the pillar, or the audience segment - or pick")
            print("a different problem from the Content Idea Framework tree.")
        elif top >= WARN_AT:
            print("VERDICT: adjacent to something you already made.")
            print("Fine IF the angle is genuinely different. Say out loud what is")
            print("new about it. If you cannot, it is a repeat.")
        else:
            print("VERDICT: clear.")

    return 2 if top >= BLOCK_AT else 0


def cmd_list(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    entries = sorted(data["entries"], key=lambda e: e.get("date", ""), reverse=True)
    if args.niche:
        entries = [e for e in entries if e.get("niche", "").lower() == args.niche.lower()]
    if args.pillar:
        entries = [e for e in entries if e.get("pillar", "").lower() == args.pillar.lower()]
    entries = entries[: args.limit]

    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return 0
    if not entries:
        print("no entries")
        return 0
    for e in entries:
        pil = (e.get("pillar") or "-")[:12]
        print(f"{_short(e)}  {e.get('date','')}  {pil:<12}  {e.get('topic','')}")
        if e.get("themes"):
            print(f"{'':10}themes: {', '.join(e['themes'])}")
    print(f"\n{len(entries)} shown | store: {path}")
    return 0


def cmd_show(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    e = _find(data, args.id)
    print(json.dumps(e, ensure_ascii=False, indent=2))
    return 0


def cmd_edit(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    e = _find(data, args.id)
    changed = []
    for pair in args.set or []:
        if "=" not in pair:
            raise SystemExit(f"ledger: --set expects field=value, got {pair!r}")
        k, v = pair.split("=", 1)
        k = k.strip()
        # Reject unknown fields. Without this, a typo (video-path instead of
        # video_path, or a CLI flag name instead of a field name) silently adds
        # a junk key and the real field stays stale - the edit appears to work
        # and quietly does nothing.
        if k not in EDITABLE_FIELDS:
            raise SystemExit(
                f"ledger: {k!r} is not a field.\n"
                f"Editable fields: {', '.join(sorted(EDITABLE_FIELDS))}\n"
                f"Note they use underscores, not hyphens (video_path, not video-path)."
            )
        if k == "themes":
            e[k] = [t.strip() for t in v.split(",") if t.strip()]
        elif k == "seconds":
            try:
                e[k] = float(v) if v else None
            except ValueError:
                raise SystemExit(f"ledger: seconds must be a number, got {v!r}")
        elif k == "pillar":
            v = v.lower()
            if v and v not in PILLARS:
                raise SystemExit(
                    f"ledger: pillar must be one of {', '.join(PILLARS)}, got {v!r}")
            e[k] = v
        else:
            e[k] = v
        changed.append(k)
    if not changed:
        print("nothing to change")
        return 0
    save(path, data)
    print(f"updated {_short(e)}: {', '.join(changed)}")
    return 0


def cmd_remove(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    e = _find(data, args.id)
    data["entries"] = [x for x in data["entries"] if x is not e]
    save(path, data)
    print(f"removed {_short(e)}  {e.get('topic','')}")
    return 0


def cmd_stats(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    entries = data["entries"]
    if not entries:
        print("ledger is empty")
        return 0

    n = len(entries)
    from collections import Counter
    pillars = Counter((e.get("pillar") or "unset").lower() for e in entries)
    niches = Counter((e.get("niche") or "unset") for e in entries)
    platforms = Counter((e.get("platform") or "unset") for e in entries)
    hooks = Counter(e.get("hook_template") for e in entries if e.get("hook_template"))

    print(f"{n} entries | store: {path}\n")

    print("PILLAR BALANCE")
    for p in PILLARS:
        c = pillars.get(p, 0)
        bar = "#" * int(round(24 * c / n))
        print(f"  {p:<14} {c:>3}  {c/n:>5.0%}  {bar}")
    if pillars.get("unset"):
        print(f"  {'(unset)':<14} {pillars['unset']:>3}")

    print("\nNICHE MIX  (target 80 / 15 / 5 — superniche / adjacent / personal)")
    for name, c in niches.most_common(8):
        print(f"  {name[:28]:<28} {c:>3}  {c/n:>5.0%}")

    if platforms and list(platforms) != ["unset"]:
        print("\nPLATFORM")
        for name, c in platforms.most_common():
            print(f"  {name[:20]:<20} {c:>3}")

    formats = Counter(e.get("format") for e in entries if e.get("format"))
    if formats:
        print("\nFORMAT")
        for name, c in formats.most_common():
            print(f"  {name[:26]:<26} {c:>3}")
    funnel = Counter((e.get("funnel") or "unset") for e in entries)
    if list(funnel) != ["unset"]:
        print("\nFUNNEL")
        for k in FUNNEL + ("unset",):
            if funnel.get(k):
                print(f"  {k:<8} {funnel[k]:>3}  {funnel[k]/n:>5.0%}")

    if hooks:
        print("\nHOOK TEMPLATES USED")
        for name, c in hooks.most_common(10):
            warn = "  <- leaning on this" if c >= max(3, n * 0.25) else ""
            print(f"  #{name:<6} {c:>3}{warn}")

    dates = sorted(e.get("date", "") for e in entries if e.get("date"))
    if len(dates) >= 2:
        try:
            d0 = _dt.date.fromisoformat(dates[0])
            d1 = _dt.date.fromisoformat(dates[-1])
            span = max((d1 - d0).days, 1)
            print(f"\nCADENCE  {dates[0]} -> {dates[-1]}  ({span} days)")
            print(f"  {n/span*7:.1f} pieces per week")
            gap = (_dt.date.today() - d1).days
            if gap > 7:
                print(f"  last entry was {gap} days ago")
        except ValueError:
            pass
    return 0


def cmd_themes(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    from collections import Counter
    c = Counter()
    for e in data["entries"]:
        for t in e.get("themes", []) or []:
            c[t.strip().lower()] += 1
        for tok in set(tokenize(e.get("topic", ""), stem=False)):
            c[tok] += 1
    if not c:
        print("no themes recorded")
        return 0
    print("themes covered, most to least:\n")
    for name, n in c.most_common(args.limit):
        print(f"  {n:>3}  {name}")
    print("\nThe long tail is where the un-repeated ideas are.")
    return 0


def cmd_suggest(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    entries = data["entries"]
    if not entries:
        print("ledger is empty - anything is new. Start with your premis.")
        return 0
    from collections import Counter
    n = len(entries)
    pillars = Counter((e.get("pillar") or "unset").lower() for e in entries)

    print("WHAT YOU ARE DUE\n")
    gaps = [(pillars.get(p, 0), p) for p in PILLARS]
    gaps.sort()
    least, least_name = gaps[0]
    most, most_name = gaps[-1]
    print(f"  Pillar gap: {least_name} is at {least}/{n} ({least/n:.0%}), "
          f"{most_name} at {most}/{n} ({most/n:.0%}).")
    print(f"  -> make a {least_name} piece next.")

    hooks = Counter(e.get("hook_template") for e in entries if e.get("hook_template"))
    if hooks:
        over = [h for h, c in hooks.items() if c >= max(3, n * 0.25)]
        if over:
            print(f"\n  Hook fatigue: template(s) {', '.join('#'+str(h) for h in over)} "
                  f"used heavily.")
            print("  -> pick an unused one from kadev-script-formulas.md sec 4.")

    used = {e.get("format") for e in entries if e.get("format")}
    untried = [f for f in FORMATS if f not in used]
    if untried:
        more = " ..." if len(untried) > 6 else ""
        print(f"\n  Formats never tried: {', '.join(untried[:6])}{more}")
        print("  -> no winner yet? test one of these (kadev-live-mentoring.md sec 1, 5.3).")

    last10 = sorted(entries, key=lambda e: e.get("date", ""), reverse=True)[:10]
    if len(last10) >= 5 and all(e.get("funnel") for e in last10) and \
            not any(e.get("funnel") == "tofu" for e in last10):
        print("\n  Funnel: none of the recent pieces is TOFU. Nobody new is finding you.")
        print("  -> make a light, general 'why' piece (kadev-live-mentoring.md sec 5.1).")

    recent = sorted(entries, key=lambda e: e.get("date", ""), reverse=True)[:5]
    print("\n  Last 5, so you do not circle back:")
    for e in recent:
        print(f"    {e.get('date','')}  {e.get('topic','')}")

    print("\n  Un-mined angles (Content Idea Framework): for each problem you have")
    print("  covered, the untouched angles are usually Don't, Penyebab, and QNA.")
    return 0


def cmd_export(args) -> int:
    path = Path(args.store) if args.store else default_store()
    data = load(path)
    entries = sorted(data["entries"], key=lambda e: e.get("date", ""))
    if args.format == "csv":
        buf = io.StringIO()
        cols = ["date", "topic", "niche", "pillar", "hook_template", "angle",
                "themes", "platform", "seconds", "status", "script_path", "video_path"]
        w = csv.writer(buf)
        w.writerow(cols)
        for e in entries:
            w.writerow([
                ", ".join(e.get(c, [])) if c == "themes" else (e.get(c) or "")
                for c in cols
            ])
        out = buf.getvalue()
    else:
        lines = ["# Content ledger", "",
                 f"{len(entries)} pieces | exported {_today()}", ""]
        for e in entries:
            lines.append(f"## {e.get('date','')} - {e.get('topic','')}")
            lines.append("")
            for label, key in (("Niche", "niche"), ("Pillar", "pillar"),
                               ("Hook", "hook"), ("Angle", "angle"),
                               ("Premise", "premise"), ("Platform", "platform"),
                               ("Status", "status"), ("Notes", "notes")):
                if e.get(key):
                    lines.append(f"- **{label}:** {e[key]}")
            if e.get("themes"):
                lines.append(f"- **Themes:** {', '.join(e['themes'])}")
            lines.append("")
        out = "\n".join(lines)

    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(out)
    return 0


# --------------------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ledger",
        description="SpliceCraft content ledger - local memory of what you already made.",
    )
    p.add_argument("--store", help="path to ledger.json (default: ~/.splicecraft/ledger.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create the store")
    s.add_argument("--force", action="store_true", help="overwrite an existing store")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("add", help="log a produced piece")
    s.add_argument("topic", help="what it was about, in the user's own words")
    s.add_argument("--niche", help="superniche this belongs to")
    s.add_argument("--pillar", choices=PILLARS, help="content pillar")
    s.add_argument("--hook", help="the actual hook line used")
    s.add_argument("--hook-template", dest="hook_template",
                   help="which of the 20 hook templates (1-20)")
    s.add_argument("--angle", help="what made THIS one different")
    s.add_argument("--theme", action="append", help="repeatable")
    s.add_argument("--premise", help="premis this serves")
    s.add_argument("--platform", help="tiktok / reels / shorts / linkedin")
    s.add_argument("--format", help="one of: " + ", ".join(FORMATS))
    s.add_argument("--funnel", choices=FUNNEL, help="tofu (tahu) / mofu (mau) / bofu (beli)")
    s.add_argument("--source", help="where the idea came from: question, complaint, "
                   "misconception, observation - never invented")
    s.add_argument("--seconds", type=float)
    s.add_argument("--script-path", dest="script_path")
    s.add_argument("--video-path", dest="video_path")
    s.add_argument("--status", help="idea / scripted / filmed / produced / published")
    s.add_argument("--date", help="YYYY-MM-DD (default today)")
    s.add_argument("--notes")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("check", help="similarity check BEFORE writing")
    s.add_argument("topic")
    s.add_argument("--hook")
    s.add_argument("--angle")
    s.add_argument("--theme", action="append")
    s.add_argument("--niche", help="restrict to this niche first")
    s.add_argument("--limit", type=int, default=5)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("list", help="recent entries")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--niche")
    s.add_argument("--pillar", choices=PILLARS)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="one entry in full")
    s.add_argument("id")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("edit", help="amend an entry")
    s.add_argument("id")
    s.add_argument("--set", action="append", metavar="FIELD=VALUE")
    s.set_defaults(func=cmd_edit)

    s = sub.add_parser("remove", help="delete an entry")
    s.add_argument("id")
    s.set_defaults(func=cmd_remove)

    s = sub.add_parser("stats", help="pillar balance, niche mix, cadence")
    s.set_defaults(func=cmd_stats)

    s = sub.add_parser("themes", help="themes covered, ranked")
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(func=cmd_themes)

    s = sub.add_parser("suggest", help="what is under-used / due next")
    s.set_defaults(func=cmd_suggest)

    s = sub.add_parser("export", help="dump for the user")
    s.add_argument("--format", choices=("md", "csv"), default="md")
    s.add_argument("--out")
    s.set_defaults(func=cmd_export)

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except SystemExit:
        raise
    except OSError as e:
        print(f"ledger: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
