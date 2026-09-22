# Faux Amis image exports

Place these files in `/assets/faux-amis/`. Keep each PNG and WebP pair at the same pixel dimensions.

| File | Dimensions | What it should show |
| --- | ---: | --- |
| `app-icon.png`, `app-icon.webp` | 1024×1024 | Final Faux Amis app icon, without rounded-corner padding added by the export. |
| `favicon.ico` | 32×32 | App-icon mark simplified for a browser tab. |
| `favicon-16x16.png` | 16×16 | App-icon mark simplified for a browser tab. |
| `favicon-32x32.png` | 32×32 | App-icon mark simplified for a browser tab. |
| `apple-touch-icon.png` | 180×180 | App icon prepared as an Apple touch icon. |
| `og.png` | 1200×630 | Social card with the app icon, “Faux Amis” and “Words that lie to you.” |
| `language-pairs.png`, `language-pairs.webp` | 1179×2556 | Language-pair and direction picker showing English↔French, English↔Spanish and English↔Italian. |
| `word-card.png`, `word-card.webp` | 1179×2556 | Answer state showing the real meaning, trap meaning, example sentence and translation. |
| `difficulty-tiers.png`, `difficulty-tiers.webp` | 1179×2556 | Tier picker showing Common, Medium, Advanced, Partial and All. |
| `pronunciation.png`, `pronunciation.webp` | 1179×2556 | Word card with the pronunciation control visible. |
| `progress.png`, `progress.webp` | 1179×2556 | Progress view showing accuracy, tier progress, session history and daily streak. |

The site uses the supplied app tint `rgb(255, 56, 60)` as `--tint`. Its darker light-mode text and button shade is derived from that tint to maintain WCAG AA contrast.
