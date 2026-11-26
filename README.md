# Arrow Rush

![tests](https://github.com/jonathanmlanger/arrow-rush/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/MicroPython-Firia%20Labs%20CodeX-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A fast reaction game for the [Firia Labs CodeX](https://firialabs.com) handheld, written in Python for my 8th grade computer science class. A direction word flashes on the screen and you press the matching button before time runs out. Every hit makes the next round faster. After 10 points, red **DON'T PRESS!** rounds start showing up to catch you off guard.

<!-- Add a photo or short GIF of the game running on a CodeX here:
![Arrow Rush on a CodeX](docs/arrow-rush.gif) -->

## How to play

| Control | Action |
|---|---|
| **A** | Start / play again |
| **Up / Down / Left / Right** | Press the direction shown on screen |
| *(nothing)* | On a red DON'T PRESS round, wait it out |

You start with 3 lives, shown on the four LEDs above the screen. A wrong button, a slow press, or pressing during a DON'T PRESS round costs a life. Every 5 hits in a row flashes the LEDs yellow. Your best score is shown on the title screen.

## Run it on a CodeX

1. Open Firia Labs **CodeSpace** and connect your CodeX by USB.
2. Create a new file and paste in the contents of [`arrow_rush.py`](arrow_rush.py).
3. Click **Run**.

## Tweak Zone

The top of the file has a block of settings that students change one at a time to see what happens. That "change one number, run it, explain what changed" loop is the main way the class explores the code.

| Setting | Default | What it does |
|---|---|---|
| `START_TIME` | `1500` | Milliseconds to react in the first round |
| `SPEED_UP` | `0.95` | Each hit multiplies the time limit by this |
| `FASTEST` | `400` | The time limit never drops below this |
| `LIVES` | `3` | Misses allowed (max 4, one per LED) |
| `TRICK_START` | `10` | Score when DON'T PRESS rounds begin |
| `TRICK_CHANCE` | `20` | Percent chance of a DON'T PRESS round |

## What students learn from it

The game is small enough to read in one sitting, and each part maps to a concept from the CodeX Python missions: **parallel lists** (`WORDS`, `BUTTONS`, and `COLORS` line up by index), **random choice**, a **timed while loop** that polls buttons until a deadline, **functions that return True or False**, and **if/else** deciding which kind of round to play. Comments in the code point these out by name.

## Testing

The `codex` library only exists on the device, so the tests swap in fake hardware ([`tests/fake_codex.py`](tests/fake_codex.py)) that records what the game draws, scripts button presses at exact moments, and replaces the clock so a full game runs in milliseconds. The endless main loop is skipped, and each function is tested on its own.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

The 19 tests cover the rules a player would notice: the right button scores, the wrong one or a late one doesn't, a press left over from the last round is ignored, DON'T PRESS rounds never appear before the trick score, and the game speeds up without ever going past `FASTEST`.

To check that the tests actually catch mistakes, I broke the game on purpose three ways (removed the speed floor, let any button count as correct, and skipped clearing old presses). Each change made a test fail. GitHub Actions runs the suite on every push.

## How this was built

I designed this game with an AI assistant (Claude) as a pair programmer. I set the requirements (classroom-friendly code, a tweakable settings block, concepts matching the CodeX curriculum), reviewed and tested every version on real devices with students, and fixed issues that came up on the hardware. The test suite and fake hardware layer were also written with AI help, then checked by deliberately breaking the game to confirm the tests fail when they should.

## License

[MIT](LICENSE) © 2026 Jonathan Langer
