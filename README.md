<div align="center">
  <img src="https://www.bohd4n.dev/assets/projects/StickersDownloader.svg" alt="EmojiSaver" width="96" height="96" style="border-radius: 20px;"><br><br>

# EmojiSaver

[![Stars](https://img.shields.io/github/stars/bohd4nx/EmojiSaver?style=flat&color=blue&label=Stars)](https://github.com/bohd4nx/EmojiSaver/stargazers)
[![Forks](https://img.shields.io/github/forks/bohd4nx/EmojiSaver?style=flat&color=blue&label=Forks)](https://github.com/bohd4nx/EmojiSaver/forks)
[![Demo](https://img.shields.io/badge/Demo-@EmojiSaverBot-blue?style=flat&label=Demo)](https://t.me/EmojiSaverBot)

Telegram bot that downloads and converts **custom emoji**, **stickers**, and full packs to TGS, JSON, Lottie, and PNG.

**[@EmojiSaverBot](https://t.me/EmojiSaverBot)** · **[Report Bug](https://github.com/bohd4nx/EmojiSaver/issues)**

</div>

---

## Features

- Extract custom (premium) emoji from messages
- Download full sticker and emoji packs via `t.me` links
- Convert to TGS, JSON, Lottie, and PNG formats
- Auto-split large archives into 45 MB parts
- Russian and English, auto-detected from Telegram locale

---

## Installation

```bash
git clone https://github.com/bohd4nx/EmojiSaver.git
cd EmojiSaver
pip install -e .
cp .env.example .env # Edit .env with your bot token and other settings
```

Edit `.env`, then:

```bash
python main.py
```

---

## Output Formats

| Format | Extension | Notes                                  |
| ------ | --------- | -------------------------------------- |
| TGS    | `.tgs`    | Original Telegram animated format      |
| JSON   | `.json`   | Uncompressed Lottie animation          |
| Lottie | `.lottie` | Compressed Lottie (LottieFiles format) |
| PNG    | `.png`    | First frame, 512×512 px                |

Non-TGS formats (WebM, WebP, MP4, GIF, etc.) are passed through as-is.

---

## Docker

```bash
cp .env.example .env
docker compose up -d
```

```bash
docker compose logs -f     # live logs
docker compose restart     # restart
docker compose down        # stop
docker compose down -v     # stop + wipe database
```
