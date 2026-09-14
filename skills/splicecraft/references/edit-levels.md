# Edit levels 1 to 100

One number controls the whole edit. Switches change at tier borders. Continuous values change smoothly inside a tier.

## Tier switches

| Setting | Clean 1-20 | Social 21-40 | Creator 41-60 | Pro 61-80 | Showrunner 81-100 |
|---|---|---|---|---|---|
| Caption style | plain | chunk | highlight | pop | kinetic |
| Words per caption | 7 | 4 | 3 | 3 | 3 |
| Hook title | no | yes | yes | yes | yes |
| Zooms | no | yes | yes | yes | yes |
| Music bed | no | yes | yes | yes | yes |
| Sound effects | no | no | yes | yes | yes |
| Ranking cards | no | yes | yes | yes | yes |
| Word cards | no | no | yes | yes | yes |
| Callbacks | no | no | yes | yes | yes |
| Progress bar | no | no | no | yes | yes |
| Film grain on cinema/noir | no | no | no | yes | yes |
| Flash hits | no | no | no | no | yes |

## Continuous values at sample levels

| Level | Pause cut above | Cards/min ceiling | Min gap between cards | Zoom | Grade strength |
|---|---|---|---|---|---|
| 1 | 0.94 s | 0.1 | 10.9 s | 1.002 | 0.26 |
| 10 | 0.89 s | 1.0 | 10.1 s | 1.022 | 0.33 |
| 25 | 0.79 s | 2.5 | 8.75 s | 1.055 | 0.44 |
| 50 | 0.63 s | 5.0 | 6.5 s | 1.11 | 0.63 |
| 60 | 0.56 s | 6.0 | 5.6 s | 1.132 | 0.70 |
| 75 | 0.46 s | 7.5 | 4.25 s | 1.165 | 0.81 |
| 85 | 0.40 s | 8.5 | 3.35 s | 1.187 | 0.89 |
| 100 | 0.30 s | 10.0 | 2.0 s | 1.22 | 1.00 |

## Picking a level for the user

| The user says | Level |
|---|---|
| "Just add subtitles" | 10 |
| "Clean it up, nothing flashy" | 20 |
| "For Instagram" / "for LinkedIn" | 35 to 50 |
| "Make it engaging" / "like a creator" | 55 to 65 |
| "Like MrBeast" / "super dynamic" / "viral" | 80 to 90 |
| "Maximum" / "go crazy" | 95 |
| Serious topic (grief, medical, legal) | 15 to 30, look `editorial` or `cinema`, no flashes |
| Tutorial with a screen recording | 30 to 45; heavy zoom fights the UI on screen |

## Caption styles

- **plain:** full phrase, white with dark stroke, 80 ms fade.
- **chunk:** short phrase pops from 88% to 100% scale.
- **highlight:** phrase stays; the spoken word turns accent color.
- **pop:** words appear as spoken; the current word pops from 108% (118% for keywords) and is accent colored.
- **kinetic:** pop, plus long keywords (7+ letters) flash above the caption in small spaced capitals.
