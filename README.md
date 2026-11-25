# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/xiacai520/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/xiacai520/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A 1024×1024 poster summing up six verified world-news stories from 25 November 2026 — the Houthi drone strike on Riyadh's PIF Tower, the Israeli strike that killed a senior Hamas security official in Gaza, the US proposal for tariffs on 14 trading partners, the US jury convicting Huawei, the slide in Asian stocks, and the second straight day of ground stops at Chicago O'Hare. Each story was checked against a reputable source (Reuters, Al Jazeera, Times Now / FAA) before it went on the poster.

## Run it

```sh
python3 main.py
```

That renders `entry.png` (1024×1024). Pure Python standard library — the PNG encoder, the 5×7 bitmap font and the layout engine are all hand-written in `main.py`. No third-party packages, no network access, no external assets. Running it twice produces a byte-identical `entry.png`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
