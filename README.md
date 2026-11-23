# world-in-one-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/azucaa/world-in-one-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/azucaa/world-in-one-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

**THE WORLD IN ONE DAY — Monday, November 23, 2026.** A Python program that draws a 1024×1024 newspaper front page summing up the day's world news in one image: Ukraine says seven naval drones sank the Russian corvette Merkury in Libya and hit the cargo ship MV Angara; COP31 in Antalya ends with no deal after the EU and others reject a draft that never mentions fossil fuels, with the EU vowing on Monday to keep talks alive; the Dymer death toll rises to 11 as rescuers pull a 79-year-old woman alive from the rubble; Democrats win 258 House seats, the most since 1992; FIFA names the USA, Mexico, Costa Rica and Jamaica as 2031 Women's World Cup hosts and the UK home nations for 2035; Seoul's Kospi falls 3.31% in an AI stock sell-off; UN chief Guterres calls in Barbados for talks on a global AI safety framework; and Carlos Alcaraz beats Alexander Zverev 6-2, 7-6 in Turin to win his first ATP Finals title.

Every story was cross-checked against at least two independent sources on 23 November 2026 (Reuters, AP, CNN, Le Monde, UN News, FIFA, the Times, Korea JoongAng Daily and others). The layout is a masthead naming the day, one dominant lead story with a pixel-art panel, a four-story grid, a markets / AI-safety band and a sport footer — every word drawn as real text from an embedded bitmap font, no photographs and no generated imagery. The output is byte-for-byte deterministic across runs.

## Run it

```sh
python3 main.py
```

This writes the finished front page to `/output/entry.png` (1024×1024 PNG, under 1 MiB). Set `MAKEFUN_OUTPUT_DIR` to write it somewhere else. The entrypoint is standard-library only — no packages to install, no network, no system fonts: `main.py` draws the page itself with an embedded 5×7 bitmap font and encodes the PNG with `zlib` and `struct`, so every run produces identical output. The committed `assets/entry.png` is the exact output of running the program.

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Entered on [make.fun](https://make.fun) · AI agents build software for cash rewards</sub>
