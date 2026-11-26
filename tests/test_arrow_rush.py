"""Tests for Arrow Rush. Run with: pytest -v"""
import pytest


def always_pick(ns, index):
    """Make the game's random word choice predictable."""
    ns["random"].randint = lambda a, b: index


# ---------- helpers ----------

def test_center_text_centers_the_word(game):
    ns, _ = game
    ns["center_text"]("RUSH", 90, ns["YELLOW"], 4)
    _, text, x, y, color, scale = ns["display"].last_text()
    # 4 letters x 8 px x scale 4 = 128 px wide, so it starts at (240 - 128) / 2
    assert x == 56


def test_center_text_never_starts_off_the_left_edge(game):
    ns, _ = game
    ns["center_text"]("THIS MESSAGE IS FAR TOO LONG", 0, ns["WHITE"], 4)
    assert ns["display"].last_text()[2] == 0


@pytest.mark.parametrize("lives", [0, 1, 2, 3, 4])
def test_show_lives_lights_one_green_led_per_life(game, lives):
    ns, _ = game
    ns["show_lives"](lives)
    assert ns["pixels"].leds.count(ns["GREEN"]) == lives


# ---------- arrow rounds ----------

def test_correct_button_scores(game):
    ns, clock = game
    always_pick(ns, 2)                          # the word is LEFT
    ns["buttons"].press("L", at=0.2)
    assert ns["arrow_round"](1500, 0) is True


def test_wrong_button_is_a_miss(game):
    ns, _ = game
    always_pick(ns, 2)                          # the word is LEFT
    ns["buttons"].press("R", at=0.2)
    assert ns["arrow_round"](1500, 0) is False


def test_no_press_times_out_after_the_time_limit(game):
    ns, clock = game
    always_pick(ns, 0)
    assert ns["arrow_round"](1500, 0) is False
    assert clock.now >= 1.5


def test_press_after_time_runs_out_does_not_count(game):
    ns, _ = game
    always_pick(ns, 0)                          # the word is UP
    ns["buttons"].press("U", at=2.0)
    assert ns["arrow_round"](1500, 0) is False


def test_old_press_from_before_the_round_is_ignored(game):
    ns, _ = game
    always_pick(ns, 0)                          # the word is UP
    ns["buttons"].press("U", at=0)              # pressed before the word appeared
    assert ns["arrow_round"](1500, 0) is False


def test_each_word_shows_its_own_color(game):
    ns, _ = game
    for i in range(4):
        always_pick(ns, i)
        ns["arrow_round"](10, 0)
        fills = [c for c in ns["display"].calls if c[0] == "fill"]
        assert fills[-1][1] == ns["COLORS"][i]


# ---------- DON'T PRESS rounds ----------

def test_waiting_out_a_trick_round_scores(game):
    ns, _ = game
    assert ns["trick_round"](1000, 10) is True


def test_pressing_during_a_trick_round_is_a_miss(game):
    ns, _ = game
    ns["buttons"].press("D", at=0.3)
    assert ns["trick_round"](1000, 10) is False


# ---------- whole game ----------

def scripted_rounds(ns, results):
    """Replace both round types with a script, and log what the game asked for."""
    results = iter(results)
    log = []

    def arrow(limit, score):
        log.append(("arrow", score, limit))
        return next(results)

    def trick(limit, score):
        log.append(("trick", score, limit))
        return next(results)

    ns["arrow_round"] = arrow
    ns["trick_round"] = trick
    return log


def test_game_counts_hits_and_ends_after_all_lives_are_used(game):
    ns, _ = game
    scripted_rounds(ns, [True] * 12 + [False] * 3)
    assert ns["play_game"]() == 12
    assert ns["GREEN"] not in ns["pixels"].leds     # all life lights are off


def test_a_player_who_never_presses_scores_zero(game):
    ns, _ = game
    assert ns["play_game"]() == 0


def test_game_speeds_up_but_never_past_the_fastest_setting(game):
    ns, _ = game
    log = scripted_rounds(ns, [True] * 100 + [False] * 3)
    ns["play_game"]()
    limits = [limit for _, _, limit in log]
    assert limits[0] == ns["START_TIME"]
    assert limits[1] == int(ns["START_TIME"] * ns["SPEED_UP"])
    assert all(a >= b for a, b in zip(limits, limits[1:]))   # never slows down
    assert min(limits) == ns["FASTEST"]


def test_trick_rounds_only_start_at_the_trick_score(game):
    ns, _ = game
    log = scripted_rounds(ns, [True] * 100 + [False] * 3)
    ns["play_game"]()
    trick_scores = [score for kind, score, _ in log if kind == "trick"]
    assert trick_scores, "expected at least one DON'T PRESS round in 100 rounds"
    assert min(trick_scores) >= ns["TRICK_START"]
