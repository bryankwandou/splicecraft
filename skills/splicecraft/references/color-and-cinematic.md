# Color, cinematic looks, and chroma key

The grade runs before zooms and captions, so graphics keep their exact colors.

## 1. Built-in grades (`--grade`)

`k` is the grade strength from the level (0.25 to 1.0).

| Grade | ffmpeg chain | Use for |
|---|---|---|
| clean | `eq=contrast=1+0.08k:saturation=1+0.1k` | anything; safest on skin |
| punchy | `eq=contrast=1+0.18k:saturation=1+0.3k:brightness=0.01,unsharp=5:5:0.6` | bright creator content, flat webcam footage |
| cinematic | `eq` slight desaturation + `colorbalance` (warm shadows-to-red, cool highlights-to-blue) + S-curve + `vignette` | stories, documentaries, dark rooms |
| warm | `eq` + `colortemperature` down to about 5300 K | interviews, lifestyle, editorial |
| mono | `hue=s=0`, contrast lift, vignette | drama, quotes, noir look |
| none | passthrough | footage that is already graded |

Each look in `presets/styles.json` has a default grade. `--grade` overrides it.

## 2. Reading the source before grading

Take three frames and look at them:

```bash
ffmpeg -i input.mp4 -vf "select='eq(n\,30)+eq(n\,300)+eq(n\,900)',scale=360:-1,tile=3x1" -frames:v 1 frames.jpg
```

| You see | Do this |
|---|---|
| Face darker than the wall | `--grade punchy`, and add `,eq=gamma=1.12` in a custom chain (section 5) |
| Orange or green skin already | `--grade clean` or `none`; strong grades make it worse |
| Blown-out window behind | `curves=all='0/0 0.7/0.62 1/0.9'` to pull highlights down |
| Noisy dark footage | add `hqdn3d=3:3:6:6` before the grade; skip grain |
| Blue daylight cast | `colortemperature=temperature=5600` (lower = warmer) |
| Tungsten orange cast | `colortemperature=temperature=7500` |

## 3. LUTs

```bash
$SC render input.mp4 work/edl.json -o out.mp4 --lut looks/teal_orange.cube --grade clean
```

- Only `.cube` 3D LUTs. The LUT is applied after the built-in grade, so use `--grade clean` or `none` to avoid stacking.
- Log footage (S-Log, C-Log, V-Log) needs its manufacturer's conversion LUT first, then a creative LUT. With `--lut` you can apply one; chain the second by hand (section 5).
- Only use LUTs the user supplies or that come with a license allowing use.

## 4. Cinematic checklist

A "cinematic" request usually means these, in this order of impact:

1. **Motion restraint.** Level 40 to 65. Drift zooms, fewer punch zooms, no flashes.
2. **Contrast curve.** S-curve with lifted blacks: `curves=all='0/0.03 0.25/0.22 0.75/0.8 1/0.97'`.
3. **Split tone.** Warm skin, cool shadows: `colorbalance=rs=0.05:bs=-0.05:rh=-0.03:bh=0.05`.
4. **Vignette.** `vignette=angle=PI/5`.
5. **Grain.** `noise=alls=6:allf=t` (automatic at level 61+ for cinema and noir).
6. **24 fps.** `--fps 24` for a film cadence. Not for fast-talking social clips.
7. **Letterbox** on 16:9 output only: add `drawbox=x=0:y=0:w=iw:h=ih*0.06:color=black:t=fill,drawbox=x=0:y=ih*0.94:w=iw:h=ih*0.06:color=black:t=fill` and raise `card_y` in `brand.json` so cards clear the bar. Never letterbox 9:16.
8. **Look:** `--style cinema`.

## 5. Custom chains

Edit `GRADES` in `scripts/splicecraft.py` or add an entry:

```python
GRADES["daylight_fix"] = "colortemperature=temperature=5600,eq=contrast={c}:gamma=1.08:saturation={s}"
```

Placeholders available: `{c}` `{c2}` `{s}` `{s2}` `{s3}` `{rs}` `{bs}` `{rh}` `{bh}` `{temp}`. Then pass `--grade daylight_fix`.

## 6. Chroma key (green or blue screen)

```bash
$SC render input.mp4 work/edl.json -o out.mp4 --key green --bg backgrounds/office.jpg
```

- `--key green`, `--key blue`, or an exact color `--key 0x3BB54A`.
- `--bg` can be an image (looped) or a video (looped). Without `--bg`, an animated gradient in the look's `bg_a` and `bg_b` colors is used.
- The chain is `chromakey=color:0.16:0.08` then `despill`, then overlay on the background.

Tuning when the edge looks wrong:

| Problem | Fix in `render()` chromakey values |
|---|---|
| Green halo around hair | raise similarity from 0.16 to 0.20 |
| Parts of the person disappear (green shirt, reflections) | lower similarity to 0.10; ask the user to avoid green clothes |
| Hard jagged edge | raise blend from 0.08 to 0.15 |
| Uneven screen lighting (dark corners) | sample the actual screen color: `ffmpeg -i in.mp4 -vf "crop=40:40:20:20,scale=1:1" -frames:v 1 -f rawvideo -pix_fmt rgb24 - \| xxd` and pass it as `--key 0xRRGGBB` |

Match the background to the subject: same light direction, similar brightness, slightly blurred (`boxblur=8`) so the speaker stays the sharpest thing in frame.

## 7. Reframing to vertical

The render scales to cover the target and center-crops. For an off-center speaker, crop first:

```bash
# speaker on the left third of a 1920x1080 clip
ffmpeg -i wide.mp4 -vf "crop=608:1080:260:0" -c:a copy left.mp4
```

Width for a 9:16 crop of 1080 px tall footage is 608 px. Change the third number to move the window.
