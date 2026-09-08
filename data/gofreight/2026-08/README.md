# GoFreight AEO Monthly Report — August 2026 · raw data & scripts

Backing data and reproducibility scripts for [`gofreight_august_2026_report.html`](../../../gofreight_august_2026_report.html)
(August 2026 vs July 2026). Generated 2026-09-09.

## `json/` — pulled datasets
| File | Source | Contents |
|---|---|---|
| `gofreight-aug-data.json` | GSC (sc-domain:gofreight.com, main-domain filtered) | August vs July totals, query segments, subfolders, top-30 pages, weekly clicks |
| `gf-page-clicks-aug.json` | GSC | Per-page July/August click map (for most-cited clicks) |
| `gf_core17_aug.json` | GSC, country=usa, per target page | Core 17-keyword US position by best-ranking target page (June/July/August) |
| `wd_aug.json` | WorkDuo `/responses` (occurrence-count) | Per-page citations, subfolder rollup, totals, weekly + monthly non-brand visibility |
| `ga4_ai_traffic.json` | GA4 property 373075091 | Weekly + monthly AI-referral sessions |
| `ga4-ai-drop.json` | GA4 | AI-session July→August deltas by source and by landing page |
| `ga4-chatgpt-lp.json` | GA4 (ChatGPT sources only) | ChatGPT landing-page July→August deltas |

### Builder-input copies (key convention)
The report builder reuses the prior-month script keys `jun`/`jul`, where **`jun` = July (prior)** and **`jul` = August (current)**. These pre-converted inputs are committed so the build reruns as-is:
`gofreight-july-data.json`, `gf-page-clicks-july.json`, `gf-core-page-us-july.json`, `wd_july.json` — each contains **August** data under the `jul` keys and **July** data under the `jun` keys. The `-aug`-named files above are the honest, un-remapped pulls.

## `scripts/` — pull + build
- **GSC / WorkDuo / GA4 (Python):** `gofreight_aug_data.py`, `gf_page_clicks_aug.py`, `gf_core17_aug.py`, `wd_aug.py`, `ga4_aug.py`. On macOS the GSC pulls use the Python client `gsc_client.GSC('novastacks')` (no `googleapis` node module on this machine).
- **Report builders (Python):** `build_aug_report.py` → `frag_aug.pkl`, then `write_aug_report.py` → the HTML, then `apply_core17_aug.py` replaces the Core-Keyword section with the full canonical 11 + emerging 6 two-table panel (July→August).

## Credentials
No secrets are committed. The WorkDuo scripts load keys from the environment
(`WORKDUO_PUBLIC_KEY` / `WORKDUO_SECRET_KEY`); the GSC/GA4 scripts read the OAuth
profile / token files from `input/credentials/` (not included here). Set the
env vars before running the WorkDuo scripts.
