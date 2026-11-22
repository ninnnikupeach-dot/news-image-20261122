# The World in One Picture — 22 November 2026

Editorial infographic that sums up Sunday 22 November 2026 in six stories. `entry.png` is a 1024×1024 image. `main.ts` copies it into the output directory.

## The six stories

1. **Climate** — COP31 talks stall in overtime. Antalya summit deadlocked over fossil-fuel phase-out.
2. **Conflict** — Iran strikes site in Bahrain. Tankers hit in the Strait of Hormuz as tensions flare.
3. **Justice** — Mexico captures 'El Chapo Isidro'. FBI most-wanted cartel boss seized in Sinaloa; 11 killed.
4. **Diplomacy** — Trump, Xi, Putin meet in Shenzhen. Leaders agree to start nuclear risk-reduction talks.
5. **Markets** — AI sell-off sinks stocks. Dow and S&P 500 slide into correction territory.
6. **War** — Missile hits Zelensky's hometown. Kryvyi Rih strike kills two; Ukraine hits Crimean bridge.

## Run

`node main.ts` writes `/output/entry.png`. Set `MAKEFUN_OUTPUT_DIR` to copy the image somewhere else.

## Regenerate the image

`python3 gen_image.py` redraws `entry.png` next to the script. It uses Python 3 and Pillow, and a system TTF if one is installed. No network and no other assets.
