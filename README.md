# tiny-chess-01 entry

A chess engine in one Python file, `main.py`, built for make.fun's
tiny-chess-01: the strongest engine that fits in 4,096 bytes.

`main.py` is an lzma-packed payload with a small unpacker; the unpacked
program is a self-contained engine (Python standard library only)
that plays the house gauntlet through the env at `MAKEFUN_ENV_URL`.

Engine, briefly: 0x88 board; negamax alpha-beta with principal
variation search, quiescence over captures, promotions and check
evasions, and check extensions; a Zobrist transposition table;
MVV-LVA move ordering with the transposition-table move first;
repetition and 50-move scores taken from the game history;
evaluation is material plus piece-square tables (all seven packed
into one string) with a bishop-pair bonus and a phase-switched
king table. Search runs by iterative deepening under a fixed node
budget — it never reads a clock and uses no unseeded randomness,
so every replay makes the same moves.

License: MIT (see LICENSE).
