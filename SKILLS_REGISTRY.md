# ARIA Skills Registry — Available Tools & Agents

> This file is auto-loaded into the system prompt so the LLM knows what tools are available.
> Genesis appends new entries when it creates skill wrappers.

## Pre-Built Agents (~/aria/skills/)

- `python3 ~/aria/skills/memory_agent.py store|recall <key> [value]` — Store/recall facts from long-term memory
- `python3 ~/aria/skills/email_agent.py --send|--read|--search` — Gmail send/read/search via Google API
- `python3 ~/aria/skills/social_agent.py --tweet|--dm|--timeline` — Twitter/X automation via tweepy
- `python3 ~/aria/skills/browser_agent.py "task instructions"` — Autonomous web browsing + DOM interaction
- `python3 ~/aria/skills/movies4u_downloader.py <movie_name>` — Stealthy Scrapling-based web scraper to bypass ads/captchas on movies4u.direct and extract download links (New!)
- `python3 ~/aria/skills/deep_research_v3.py <topic> --level 1-4 --type <tech/science>` — Ultra-deep autonomous research generating PDF dossiers with year filters and auto-resume.
- `python3 ~/aria/skills/self_improve_agent.py --full` — Full self-improvement sweep (research → evaluate → install)
- `python3 ~/aria/skills/genesis_agent.py --tool-name X --category Y` — Auto-install tool + generate skill wrapper
- `python3 ~/aria/skills/desktop_agent.py <move X Y | click [btn] | type "text" | key <keycode>>` — Native Wayland GUI automation using ydotool. Make sure to capture a screenshot with `grim` first to find coordinates.
- `python3 ~/aria/skills/voice_agent.py <whatsapp|telegram> "Contact Name"` — Makes a voice call over Web WhatsApp or Telegram using Playwright.

## Media & Content Tools (installed)

- `ffmpeg` — Video/audio transcoding, AMD GPU accel (VAAPI). Example: `ffmpeg -i input.mkv -c:v libx264 output.mp4`
- `vips` / `python3 -c "import pyvips"` — Fast image processing. CLI: `vipsthumbnail input.jpg -s 800 -o thumb.jpg`
- `wf-recorder` — Wayland screen recording. Example: `wf-recorder -f output.mp4 -g "$(slurp)"`
- `python3 -m easyocr` — OCR text extraction (80+ languages). Python: `import easyocr; reader = easyocr.Reader(['en'])`
- `python3 -m ocrmypdf input.pdf output.pdf` — OCR PDFs, add searchable text layer
- `python3 -c "from smart_open import open"` — Universal file I/O (S3, GCS, HDFS, HTTP, local)

## AI & Intelligence Tools (installed)

- `python3 -m whisper audio.wav --model tiny` — Speech-to-text transcription (local, CPU/GPU)
- `python3 -c "from transformers import pipeline"` — HuggingFace models, embeddings, RAG
- `python3 -m scrapy` — Web scraping framework. Create spiders for structured data extraction

## System & Utility Tools (installed)

- `nnn` — Ultra-fast terminal file manager with plugins
- `glances` — System monitoring TUI. JSON mode: `glances --export json --export-json-file /tmp/stats.json`
- `copyq` — Clipboard manager. CLI: `copyq read 0` (read latest), `copyq copy "text"` (set clipboard)
- `rg "pattern" path/` — ripgrep ultra-fast recursive file search
- `borg create /backup::archive ~/Documents` — Encrypted dedup backup. `borg list /backup` to list
- `pass show github` — GPG-encrypted password manager. `pass insert site` to add, `pass generate site 20`

## Communications Tools (installed)

- `tweepy` — Python library for Twitter API (used by social_agent.py)
- `python3 -c "from googleapiclient.discovery import build"` — Google API client (Gmail, Drive, Calendar)
- `scrcpy` — Mirror/control Android phone. `scrcpy --no-audio` for display only

## Security Tools (installed)

- `pass` — Unix password manager (GPG-encrypted, git-synced)
