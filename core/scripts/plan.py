"""Script -> edit plan. Reads the pack's script(s) and the transcript and writes every card the
script asks for, each timed to the word it names:

  - the on-screen text column (Teks layar) of the MONOLOG table,
  - the props the Visual column puts in shot (Sisipan: kertas SID, kunci, bola, peluit, buku),
    drawn as icons because the footage has no insert shots,
  - "Overlay: ..." notes in the read-aloud version (BACA-*),
  - the line the script says must stick, a term being named ("namanya X"), a spoken number,
  - the closing card (theme + event) and the brand colours of the pack.

Mechanical on purpose: a weak model writing cards by hand forgets props, invents text and puts
cards on the wrong second. Here every text comes from the script and every time from words.json.
The model runs `plan`, then lint and render; it edits the edl only when lint says so.
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

import studio as S

# word (prefix of the normalised token) -> icon. Order matters: the first hit names the icon.
ICON_WORDS = [("amplop", "envelope"), ("kunci", "key"), ("pintu", "door"), ("rumah", "house"), ("alamat", "house"),
              ("sid", "sid"), ("ktp", "sid"), ("bola", "ball"), ("futsal", "ball"), ("lapangan", "ball"),
              ("peluit", "whistle"), ("wasit", "whistle"), ("buku", "book"), ("nyatet", "book"), ("nyatat", "book"),
              ("skor", "book"), ("pencatat", "book"), ("ojk", "shield"), ("awasi", "shield"), ("diawasi", "shield"),
              ("ngawasin", "shield")]
ICON_NAMES = {"ball", "whistle", "book", "shield", "door", "house", "key", "phone", "check", "sid", "envelope"}
# filler a label never needs ("Yang nyatet skor" -> "Nyatet skor")
FILLER = {"yang", "itu", "ini", "dan", "semuanya", "biar", "jadi", "nah", "terus", "tuh", "kan", "sih", "dong",
          "udah", "sudah", "lagi", "juga", "oleh", "atau", "gini", "gampang", "gampangnya"}
NUMWORD = {"dua": 2, "tiga": 3, "empat": 4, "lima": 5}


def icons_in(text: str) -> list[str]:
    out = []
    for tok in re.split(r"[\s,.;:/·()+\-→]+", text.lower()):
        t = S.norm(tok)
        for key, icon in ICON_WORDS:
            if t.startswith(key) or (len(key) >= 5 and key in t):
                if icon not in out:
                    out.append(icon)
                break
    return out


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", s)).strip()


# ------------------------------------------------------------------ reading the pack
def table_rows(path: str) -> list[dict]:
    """Rows of the MONOLOG table: detik, ucapan (spoken, quotes only), visual, teks (on-screen text)."""
    rows, head = [], None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            head = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if head is None:
            low = [c.lower() for c in cells]
            head = low if any("ucapan" in c for c in low) and any("layar" in c for c in low) else None
            continue
        cell = dict(zip(head, cells))
        get = lambda k: next((v for h, v in cell.items() if k in h), "")
        spoken = " ".join(q.strip() for q in re.findall(r"[\"“]([^\"”]+)[\"”]", get("ucapan")))
        teks = get("layar")
        rows.append({"detik": get("detik"), "spoken": spoken, "visual": get("visual"),
                     "teks_raw": teks, "teks": "" if clean(teks) in ("", "—", "-", "–") else clean(teks)})
    return rows


def pack_facts(paths: list[str]) -> dict:
    """Title, theme, event, the line that must stick, explicit overlay notes, brand, limits."""
    f = {"title": None, "theme": None, "theme_no": None, "must": None, "notes": [], "brand": None, "limits": {}}
    for p in paths:
        raw = Path(p).read_text(encoding="utf-8")
        if f["title"] is None:
            m = re.search(r"^#?\s*VIDEO\s*\d+\s*[—-]+\s*[\"“]([^\"”]+)[\"”]", raw, re.M)
            if m:
                f["title"] = m.group(1).strip()
        m = re.search(r"Tema\s*(\d+)\s*:\s*\*?([^*\n]+?)\*?\s*$", raw, re.M)
        if m and not f["theme"]:
            f["theme_no"], f["theme"] = "Tema " + m.group(1), m.group(2).strip()
        m = re.search(r"harus nempel:?\**\s*\*?[\"“]([^\"”]+)[\"”]", raw, re.I)
        if m and not f["must"]:
            f["must"] = m.group(1).strip()
        # read-aloud version: "KAMU (..., Overlay: ikon pintu + rumah):" then the line
        for dm in re.finditer(r"\(([^)]*overlay[^)]*)\)\s*:?\s*\n(.+)", raw, re.I):
            f["notes"].append({"icons": icons_in(dm.group(1)), "line": dm.group(2).strip()})
    pack = Path(paths[0]).parent
    for d in (pack, pack.parent):
        b = d / "brand.json"
        if b.exists() and f["brand"] is None:
            f["brand"] = S.read_json(str(b))
    # competition rules written in the pack's guide: duration window, share of animation
    for md in sorted(pack.glob("*.md")):
        if md.stat().st_size > 60000:
            continue
        txt = md.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"[Ww]ajib antara\s*(\d+)\s*[–-]\s*(\d+)", txt)
        if m and "duration" not in f["limits"]:
            f["limits"]["duration"] = [int(m.group(1)), int(m.group(2))]
        m = re.search(r"menutup lebih dari\s*(\d+)\s*%", txt)
        if m and "cover_share" not in f["limits"]:
            f["limits"]["cover_share"] = int(m.group(1)) / 100
    return f


def table_script(paths: list[str]) -> str | None:
    best = None
    for p in paths:
        n = len([r for r in table_rows(p) if r["spoken"] or r["teks"]])
        if n and (best is None or n > best[0]):
            best = (n, p)
    return best[1] if best else None


# ------------------------------------------------------------------ speech <-> script
class Speech:
    """The words that stay in the cut (retakes and off-script talk removed, names fixed by
    align), and a map from script token positions to them."""

    def __init__(self, words_path: str, scripts: list[str], table: str):
        al = S.best_align(words_path, scripts)
        words = [dict(w) for w in S.read_json(words_path)["words"]]
        drops = al["drop"] if al["ok"] else []
        fix = {round(x["t"], 2): x["w"] for x in (al["fix_at"] if al["ok"] else [])}
        kept = []
        for w in words:
            if any(a <= w["s"] < b for a, b in drops):
                continue
            w["w"] = fix.get(round(w["s"], 2), w["w"]).strip()
            if w["w"]:
                kept.append(w)
        self.words, self.align = kept, al
        self.T = [S.norm(w["w"]) for w in kept]
        self.end = kept[-1]["e"] if kept else 0.0

    def map_tokens(self, S_tok: list[str]) -> dict[int, int]:
        sm = SequenceMatcher(None, self.T, S_tok, autojunk=False)
        m = {}
        for b in sm.get_matching_blocks():
            for d in range(b.size):
                # a lone common word is not an anchor ("itu" matches anywhere)
                if b.size >= 2 or S_tok[b.b + d] not in S._sc().STOP and len(S_tok[b.b + d]) > 3:
                    m[b.b + d] = b.a + d
        return m


def plan(words_path: str, scripts: list[str], edl_path: str | None = None) -> dict:
    scripts = [str(Path(p).resolve()) for p in scripts]
    tbl = table_script(scripts)
    if not tbl:
        S.die("no script with a MONOLOG table (Ucapan | Visual | Teks layar) among "
              f"{[Path(p).name for p in scripts]}: plan needs it. Write the cards by hand (SKILL step 3).")
    facts = pack_facts([tbl] + [p for p in scripts if p != tbl])
    sp = Speech(words_path, scripts, tbl)
    rows = table_rows(tbl)
    # one token list for the whole table, each token knowing its row
    toks, row_of = [], []
    for r_i, r in enumerate(rows):
        for t in r["spoken"].split():
            if S.norm(t):
                toks.append(t)
                row_of.append(r_i)
    N = [S.norm(t) for t in toks]
    m = sp.map_tokens(N)

    def t_at(j: int) -> float | None:
        """Source time the script token j was said, or None when the speaker skipped it."""
        if j in m:
            return sp.words[m[j]]["s"]
        for d in (1, -1, 2, -2, 3, -3):
            if j + d in m and 0 <= m[j + d] - d < len(sp.words):
                return sp.words[m[j + d] - d]["s"]
        return None

    for r_i, r in enumerate(rows):
        js = [j for j in range(len(toks)) if row_of[j] == r_i]
        r["js"] = js
        said = [m[j] for j in js if j in m]
        r["span"] = (sp.words[min(said)]["s"], sp.words[max(said)]["e"]) if len(said) >= 2 else None
        r["icons_note"] = []
        for note in facts["notes"]:                  # BACA "Overlay:" note -> the row that says its line
            nt = {S.norm(x) for x in note["line"].split()} - S._sc().STOP
            if nt and len(nt & {N[j] for j in js}) >= max(2, len(nt) // 2):
                r["icons_note"] += [i for i in note["icons"] if i not in r["icons_note"]]

    def find(word: str, js: list[int], prefer_colon: bool = False, after: int = -1) -> int | None:
        w = S.norm(word)
        hits = [j for j in js if j > after and (N[j] == w or (len(w) >= 5 and N[j].startswith(w[:5])))]
        if prefer_colon:
            colon = [j for j in hits if toks[j].endswith(":")]
            if colon:
                return colon[0]
        return hits[0] if hits else None

    cards, endcard, holds, unplaced = [], None, [], []
    for r_i, r in enumerate(rows):
        vis, teks, js = r["visual"], r["teks"], r["js"]
        insert = bool(re.search(r"sisipan|insert|b-?roll", vis, re.I))
        # the props of this moment: an explicit "Overlay:" note, else what the insert shot shows,
        # plus what the on-screen text names (SID)
        shown = icons_in(vis) if insert else []
        icons = list(dict.fromkeys(r["icons_note"] + shown + icons_in(teks)))
        objects = [i for i in (r["icons_note"] or shown or icons) if i != "envelope"]
        if re.search(r"card penutup|end ?card|kartu penutup", vis, re.I):
            parts = [clean(p) for p in teks.split("·") if clean(p)]
            endcard = {"parts": parts}
            continue
        if r["span"] and re.search(r"jangan dipotong|diam \d", vis, re.I):
            holds.append([round(r["span"][0], 2), round(r["span"][1] + 0.4, 2)])
        start = r["span"][0] if r["span"] else None
        sentence = toks_text = " ".join(toks[j] for j in js)
        if teks:
            pairs = re.findall(r"\*\*([^*:]+):\*\*\s*([^·]+)", r["teks_raw"])
            bits = [clean(b) for b in teks.split("·") if clean(b)]
            if pairs:                                # **Kliring:** hitung ... · **Penjaminan:** ...
                items, prev = [], -1
                for name, sub in pairs:
                    j = find(name, js, prefer_colon=True, after=prev)
                    prev = j if j is not None else prev
                    items.append({"text": clean(name), "sub": clean(sub), "at": t_at(j) if j is not None else None})
                title = re.search(r"(\w+nya\s+(?:dua|tiga|empat|lima))\b", sentence, re.I)
                cards.append({"type": "list", "items": items, **({"title": title.group(1).capitalize()} if title else {}),
                              "_row": r_i})
            elif " = " in teks:                      # SID = Single Investor Identification · dari KSEI
                title, body = [clean(x) for x in teks.split(" = ", 1)]
                j = find(title, js)
                cards.append({"type": "term", "title": title, "body": body, "at": t_at(j) if j is not None else start,
                              "icons": [{"icon": i} for i in icons[:1]], "_row": r_i})
            elif len(bits) >= 2:                     # BEI · IDClear · KSEI · diawasi OJK   /  Diawasi · Tercatat · ...
                named = [b for b in bits if any(sum(c.isupper() for c in w) >= 2 for w in b.split())]
                items, prev = [], -1
                for b in bits:
                    name = next((w for w in b.split() if sum(c.isupper() for c in w) >= 2), b.split()[0])
                    j = find(name, js, after=prev)
                    it = {"text": name if len(named) * 2 >= len(bits) else b}
                    if j is not None:
                        # the words since the previous item, in the same sentence: "Lapangannya itu" -> ball, Lapangan
                        k0 = max([prev + 1] + [k + 1 for k in range(prev + 1, j) if re.search(r"[.?!]$", toks[k])])
                        ctx = [toks[k].strip(".,?!:") for k in range(k0, j)]
                        role = [c for c in ctx if S.norm(c) not in FILLER and S.norm(c) not in S._sc().STOP]
                        role += [w for w in b.split() if w != name and S.norm(w) not in FILLER]
                        role = list({S.norm(x): x for x in reversed(role)}.values())[::-1]   # "diawasi" once
                        ic = icons_in(" ".join(ctx + [b]))
                        if ic:
                            it["icon"] = ic[0]
                        if len(named) * 2 >= len(bits) and role:
                            sub = " ".join(re.sub(r"nya$", "", x) for x in role[:2])
                            it["sub"] = sub[:1].upper() + sub[1:]
                        first_role = next((k for k in range(k0, j) if S.norm(toks[k]) not in FILLER
                                           and S.norm(toks[k]) not in S._sc().STOP), j)
                        it["at"] = t_at(first_role) or t_at(j)
                        prev = j
                    else:
                        it["at"] = None
                    items.append(it)
                if len(named) * 2 >= len(bits) and sum(1 for it in items if it.get("icon")) >= 2:
                    cards.append({"type": "props", "items": items, "_row": r_i})
                else:
                    for it in items:
                        it.pop("icon", None)
                        it.pop("sub", None)
                    title = re.search(r"(\w+\s+(?:dua|tiga|empat|lima)\s+hal)\b", sentence, re.I)
                    counted = bool(re.search(r"hitung|1-2-3|jari", vis, re.I))
                    c = {"type": "list", "items": items, "_row": r_i}
                    if title:
                        c["title"] = title.group(1).capitalize()
                    if not counted:
                        c["marker"] = "check"
                    cards.append(c)
            elif ":" in teks and len(teks.split(":")[0].split()) <= 3:   # Langkah kecil: main di tempat ...
                eb, title = [clean(x) for x in teks.split(":", 1)]
                j = find(eb.split()[0], js)
                cards.append({"type": "term", "eyebrow": eb, "title": title[:1].upper() + title[1:],
                              "at": t_at(j) if j is not None else start,
                              "icons": [{"icon": i} for i in icons_in(title)[:1]], "_row": r_i})
            else:                                    # a sentence: a held prop, or a quote
                j = find(teks.split()[0], js)
                at = t_at(j) if j is not None else start
                if (insert or r["icons_note"]) and len(objects) == 1 and len(teks.split()) <= 6:
                    # one object held up while the line is said: the SID card out of its envelope
                    c = {"type": "prop", "icon": objects[0], "text": teks.strip("*"),
                         "at": start if r_i == 0 else at, "_row": r_i}
                    if "envelope" in icons:
                        c["from"] = "envelope"
                    cards.append(c)
                else:
                    ic = []
                    for i in (objects or icons)[:2]:
                        jj = next((k for k in js if icons_in(toks[k]) == [i]), None)
                        ic.append({"icon": i, "at": t_at(jj) if jj is not None else None})
                    first = min([x["at"] for x in ic if x["at"]] or [at or 0])
                    cards.append({"type": "quote", "text": teks, "icons": ic, "at": min(first, at or first) - 0.15,
                                  "_row": r_i})
        elif insert and objects:
            # a prop the script shows with no text: a sticker while the row is said
            cards.append({"type": "prop", "icon": objects[0], "at": start, "_row": r_i, "_sticker": True})
        # a term being named: "namanya IDClear, atau KPEI. Kliring Penjaminan Efek Indonesia."
        nm = re.search(r"[Nn]amanya\s+([A-Z][\w-]+)[,.]\s*((?:atau\s+)?[A-Z][\w-]+[.,])?\s*((?:[A-Z][\w-]*\s*){3,6}\.)?", sentence)
        if nm and not any(c.get("title") == nm.group(1) for c in cards):
            body = " · ".join(clean(x).strip(".,").replace("atau ", "") for x in nm.groups()[1:] if x)
            j = find(nm.group(1), js)
            cards.append({"type": "term", "title": nm.group(1), **({"body": body} if body else {}),
                          "at": t_at(j) if j is not None else start, "_row": r_i, "_named": True})
        # a number said out loud: "Pasar modal kita udah 49 tahun"
        for k, j in enumerate(js):
            if re.fullmatch(r"\d{2,4}", toks[j].strip(".,")) and t_at(j) is not None:
                unit = toks[j + 1].strip(".,") if j + 1 < len(toks) and row_of[j + 1] == r_i else ""
                before = [toks[x].strip(".,") for x in js[max(0, k - 5):k]]
                cut = max([i + 1 for i, w in enumerate(before) if re.search(r"[.?!]$", toks[js[max(0, k - 5)] + i])] + [0])
                label = [w for w in before[cut:] if S.norm(w) not in FILLER]
                cards.append({"type": "stat", "value": toks[j].strip(".,"), "suffix": unit,
                              **({"label": " ".join(label)[:1].upper() + " ".join(label)[1:]} if label else {}),
                              "at": t_at(j), "_row": r_i})
    # the line that must stick, when its row has no card yet
    if facts["must"]:
        mt = [S.norm(x) for x in facts["must"].split() if S.norm(x)]
        sm = SequenceMatcher(None, sp.T, mt, autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size]
        if blocks and sum(b.size for b in blocks) >= len(mt) * 0.6:
            at = sp.words[blocks[0].a]["s"]
            end = sp.words[blocks[-1].a + blocks[-1].size - 1]["e"]
            covered = any(c.get("at") is not None and abs(c["at"] - at) < 6 for c in cards if not c.get("_sticker"))
            if not covered:
                cards.append({"type": "quote", "text": facts["must"], "at": at - 0.1, "_end": end,
                              "icons": [{"icon": i} for i in icons_in(facts["must"])[:1]], "_row": -1})

    # ---- times: on the word, long enough to read, one card at a time
    out = []
    for c in cards:
        row = rows[c["_row"]] if c["_row"] >= 0 else None
        items = c.get("items")
        if items:
            ats = [it["at"] for it in items if it.get("at") is not None]
            if not ats:
                unplaced.append(c)
                continue
            for it in items:                         # an item the speaker skipped shows with its neighbour
                if it.get("at") is None:
                    it["at"] = ats[0]
            c["at"] = min(ats) - (0.5 if c.get("title") else 0.25)
            c["until"] = max(ats) + 2.6
        else:
            if c.get("at") is None:
                if c.get("_sticker") and c["_row"] == len(rows) - 1 or (row and not row["span"]):
                    unplaced.append(c)
                    continue
                c["at"] = row["span"][0] if row and row["span"] else None
                if c["at"] is None:
                    unplaced.append(c)
                    continue
            span_end = c.get("_end") or (row["span"][1] if row and row["span"] else c["at"] + 3)
            short = c["type"] in ("prop", "stat")     # a number or a held object is read in a glance
            want = 3.0 if short else 4.0
            c["until"] = min(max(span_end + 0.4, c["at"] + want), c["at"] + (4.5 if short else 7.0))
        out.append(c)
    out.sort(key=lambda c: c["at"])
    # a named term and a card from the on-screen text on the same moment: keep the script's card
    out = [c for k, c in enumerate(out) if not (c.get("_named") and any(
        abs(o["at"] - c["at"]) < 1.0 for o in out if o is not c and not o.get("_named")))]
    for a, b in zip(out, out[1:]):
        if b["at"] < a["until"] + 0.15:
            a["until"] = max(a["at"] + 2.2, b["at"] - 0.15)
    for c in out:
        c["until"] = min(c["until"], sp.end + 0.3)
        for it in c.get("icons", []):
            if it.get("at") is None:
                it.pop("at", None)
    # ---- the edl
    brand = facts["brand"] or {}
    colors = {k: v for k, v in {"bg": brand.get("card_bg"), "ink": brand.get("card_text"), "accent": brand.get("accent"),
                                "on-accent": brand.get("on_accent"), "muted": brand.get("muted")}.items() if v}
    used = [i for c in out for i in ([c.get("icon")] + [x.get("icon") for x in c.get("items", []) + c.get("icons", [])]) if i]
    edl = S.read_json(edl_path) if edl_path and Path(edl_path).exists() else {}
    edl.update({
        "title": facts["title"] or edl.get("title") or "",
        "subtitle": " · ".join(x for x in [facts["theme_no"], endcard["parts"][-1] if endcard and len(endcard["parts"]) > 1 else None] if x) or edl.get("subtitle"),
        "theme": "paper",
        "overlays": [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in c.items() if not k.startswith("_")}
                     for c in out],
        "script": sp.align["scripts"] if sp.align["ok"] else scripts,
    })
    for c in edl["overlays"]:
        for it in c.get("items", []) + c.get("icons", []):
            if isinstance(it.get("at"), float):
                it["at"] = round(it["at"], 2)
    if colors:
        edl["colors"] = colors
    if holds:
        edl["hold"] = holds
    if facts["limits"]:
        edl["limits"] = facts["limits"]
    if endcard:
        parts = endcard["parts"]
        lines = ([facts["theme"]] if facts["theme"] and parts and parts[0].startswith("Tema") else []) + \
                [p for p in parts if not p.startswith("Tema")]
        edl["endcard"] = {"eyebrow": parts[0] if parts and parts[0].startswith("Tema") else None, "lines": lines or parts,
                          "hold": 2.6, **({"icon": max(set(used), key=used.count)} if used else {})}
        if not edl["endcard"]["eyebrow"]:
            edl["endcard"].pop("eyebrow")
    edl.pop("fix_at", None)
    edl.pop("drop", None)
    if edl_path:
        S.write_json(edl_path, edl)
    return {"edl": edl, "table": tbl, "unplaced": [{k: v for k, v in c.items() if not k.startswith("_")} | {"row": c["_row"]}
                                                    for c in unplaced]}


def required(scripts) -> list[tuple[str, str]]:
    """(row, on-screen text) the script asks for: lint checks that a card shows each one."""
    tbl = table_script(S.scripts_of(scripts))
    if not tbl:
        return []
    return [(r["detik"], r["teks"]) for r in table_rows(tbl)
            if r["teks"] and not re.search(r"card penutup|end ?card|kartu penutup", r["visual"], re.I)]


def show(res: dict) -> str:
    e = res["edl"]
    lines = [f"script table: {Path(res['table']).name}", f"title: {e['title']}", f"subtitle: {e.get('subtitle')}"]
    for o in e["overlays"]:
        txt = o.get("title") or o.get("text") or o.get("value") or " · ".join(
            f"{it.get('text')}{'[' + it['icon'] + ']' if it.get('icon') else ''}" for it in o.get("items", []))
        ic = [i["icon"] for i in o.get("icons", [])] + ([o["icon"]] if o.get("icon") else [])
        lines.append(f"  {o['at']:6.2f}-{o['until']:6.2f}  {o['type']:6} {txt}  {('icons ' + ','.join(ic)) if ic else ''}")
    if e.get("endcard"):
        lines.append(f"  endcard: {e['endcard']}")
    for u in res["unplaced"]:
        lines.append(f"  NOT PLACED (row {u['row']} not said): {u}")
    return "\n".join(lines)
