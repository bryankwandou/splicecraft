// splicecraft prop icons: flat vector drawings made in code (no generative images), so a
// competition that bans AI-generated pictures still accepts them. Colours come from the
// page's CSS variables, so every theme recolours them. window.SC_ICON(name) -> <svg> string.
(function () {
  let uid = 0;
  const pent = (cx, cy, r, rot = 0) => Array.from({ length: 5 }, (_, k) => {
    const a = rot + k * 2 * Math.PI / 5;
    return `${(cx + r * Math.sin(a)).toFixed(1)},${(cy - r * Math.cos(a)).toFixed(1)}`;
  }).join(" ");

  const ICONS = {
    ball() {
      const id = "cb" + (++uid);
      let edge = "", spokes = "";
      for (let k = 0; k < 5; k++) {
        const a = k * 2 * Math.PI / 5;
        edge += `<polygon points="${pent(60 + 47 * Math.sin(a), 60 - 47 * Math.cos(a), 15, a + Math.PI)}"/>`;
        spokes += `<line x1="${(60 + 15 * Math.sin(a)).toFixed(1)}" y1="${(60 - 15 * Math.cos(a)).toFixed(1)}" x2="${(60 + 34 * Math.sin(a)).toFixed(1)}" y2="${(60 - 34 * Math.cos(a)).toFixed(1)}"/>`;
      }
      return `<svg viewBox="0 0 120 120"><defs><clipPath id="${id}"><circle cx="60" cy="60" r="46"/></clipPath></defs>
        <circle cx="60" cy="60" r="46" fill="#fff"/>
        <g clip-path="url(#${id})" class="ic-ink"><polygon points="${pent(60, 60, 16)}"/>${edge}</g>
        <g class="ic-line" style="stroke-width:3">${spokes}</g>
        <circle cx="60" cy="60" r="46" class="ic-line"/></svg>`;
    },
    whistle: () => `<svg viewBox="0 0 120 120">
        <path class="ic-line" d="M88 44 C 98 26 112 24 112 12" style="stroke:var(--accent);stroke-width:3"/>
        <rect x="10" y="40" width="64" height="24" rx="8" class="ic-acc"/>
        <circle cx="74" cy="70" r="30" class="ic-acc"/>
        <circle cx="74" cy="70" r="11" class="ic-hole"/>
        <rect x="14" y="44" width="26" height="6" rx="3" fill="#fff" opacity=".45"/>
        <circle cx="90" cy="46" r="7" class="ic-line" style="stroke-width:3.5"/></svg>`,
    book: () => `<svg viewBox="0 0 120 120">
        <rect x="22" y="14" width="72" height="94" rx="8" class="ic-acc"/>
        <rect x="22" y="14" width="16" height="94" rx="6" fill="#000" opacity=".22"/>
        <rect x="90" y="20" width="6" height="82" rx="2" fill="#fff" opacity=".85"/>
        <rect x="48" y="34" width="36" height="13" rx="3" fill="#fff" opacity=".92"/>
        <rect x="48" y="54" width="26" height="6" rx="3" fill="#fff" opacity=".55"/>
        <g transform="rotate(32 88 74)"><rect x="82" y="34" width="13" height="58" rx="2" fill="#f2b544"/>
        <rect x="82" y="34" width="13" height="8" rx="2" fill="#e07a7a"/>
        <polygon points="82,92 95,92 88.5,106" fill="#ead6b4"/><polygon points="86,101 91,101 88.5,106" class="ic-ink"/></g></svg>`,
    shield: () => `<svg viewBox="0 0 120 120">
        <path class="ic-acc" d="M60 10 L98 24 V56 C98 82 82 98 60 110 C38 98 22 82 22 56 V24 Z"/>
        <path d="M60 10 L98 24 V56 C98 82 82 98 60 110 Z" fill="#000" opacity=".12"/>
        <path d="M42 60 L55 73 L80 46" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    door: () => `<svg viewBox="0 0 120 120">
        <rect x="28" y="10" width="64" height="100" rx="5" class="ic-ink"/>
        <rect x="34" y="16" width="52" height="94" rx="3" class="ic-acc"/>
        <rect x="41" y="24" width="38" height="30" rx="3" fill="#fff" opacity=".2"/>
        <rect x="41" y="62" width="38" height="40" rx="3" fill="#fff" opacity=".2"/>
        <circle cx="76" cy="60" r="4.5" fill="#fff"/></svg>`,
    house: () => `<svg viewBox="0 0 120 120">
        <path class="ic-acc" d="M60 12 L108 54 H96 V106 H24 V54 H12 Z"/>
        <path d="M60 12 L108 54 H96 V106 H60 Z" fill="#000" opacity=".1"/>
        <rect x="50" y="70" width="20" height="36" rx="3" fill="#fff"/>
        <rect x="31" y="62" width="14" height="14" rx="2" fill="#fff" opacity=".85"/>
        <rect x="75" y="62" width="14" height="14" rx="2" fill="#fff" opacity=".85"/></svg>`,
    key: () => `<svg viewBox="0 0 120 120">
        <circle cx="36" cy="60" r="19" fill="none" style="stroke:var(--accent);stroke-width:11"/>
        <rect x="52" y="54" width="58" height="12" rx="4" class="ic-acc"/>
        <rect x="86" y="62" width="9" height="18" rx="2" class="ic-acc"/><rect x="100" y="62" width="9" height="13" rx="2" class="ic-acc"/></svg>`,
    phone: () => `<svg viewBox="0 0 120 120">
        <rect x="32" y="8" width="56" height="104" rx="12" class="ic-ink"/>
        <rect x="37" y="18" width="46" height="80" rx="5" class="ic-soft"/>
        <rect x="52" y="102" width="16" height="4" rx="2" fill="#fff" opacity=".6"/></svg>`,
    check: () => `<svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="48" class="ic-acc"/>
        <path d="M38 61 L53 76 L83 44" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    // an investor card: name and number are bars and dots on purpose (nothing real to blur)
    sid: () => `<svg viewBox="0 0 200 126" class="wide">
        <rect x="1" y="1" width="198" height="124" rx="12" fill="#fff" stroke="rgba(0,0,0,.14)" stroke-width="2"/>
        <path d="M1 13 a12 12 0 0 1 12 -12 H187 a12 12 0 0 1 12 12 V30 H1 Z" class="ic-acc"/>
        <text x="12" y="21" font-size="10.5" font-weight="800" fill="#fff" letter-spacing="1.2" font-family="SC Inter, sans-serif">SINGLE INVESTOR IDENTIFICATION</text>
        <rect x="12" y="40" width="40" height="50" rx="5" class="ic-soft"/>
        <circle cx="32" cy="58" r="9" class="ic-acc" opacity=".55"/><path d="M17 90 C 18 74 46 74 47 90 Z" class="ic-acc" opacity=".55"/>
        <text x="62" y="60" font-size="25" font-weight="800" class="ic-ink" font-family="SC Sans, sans-serif" letter-spacing="-0.5">SID</text>
        <rect x="62" y="68" width="92" height="7" rx="3.5" fill="#000" opacity=".13"/>
        <rect x="62" y="80" width="62" height="7" rx="3.5" fill="#000" opacity=".13"/>
        <text x="12" y="112" font-size="14" font-weight="700" fill="#3a3a3a" letter-spacing="2.4" font-family="SC Inter, sans-serif">•••• •••• •••• ••••</text>
        <rect x="150" y="98" width="38" height="18" rx="4" class="ic-soft"/></svg>`,
    envelope_back: () => `<svg viewBox="0 0 220 150" class="wide"><rect x="0" y="0" width="220" height="150" rx="12" fill="#c4945a"/>
        <path d="M0 12 a12 12 0 0 1 12 -12 H208 a12 12 0 0 1 12 12 L110 70 Z" fill="#000" opacity=".12"/></svg>`,
    envelope_front: () => `<svg viewBox="0 0 220 150" class="wide">
        <path d="M0 50 L110 108 L220 50 V138 a12 12 0 0 1 -12 12 H12 a12 12 0 0 1 -12 -12 Z" fill="#d8ac70"/>
        <path d="M0 50 L110 108 L220 50" fill="none" stroke="#000" stroke-opacity=".12" stroke-width="2"/></svg>`,
  };
  ICONS.envelope = () => `<div class="env">${ICONS.envelope_back()}<div class="env-front">${ICONS.envelope_front()}</div></div>`;
  window.SC_ICON_NAMES = Object.keys(ICONS).filter(k => !k.includes("_"));
  window.SC_ICON = name => {
    const f = ICONS[name];
    if (!f) throw new Error("unknown icon " + name + " (have: " + window.SC_ICON_NAMES.join(", ") + ")");
    return f();
  };
})();
