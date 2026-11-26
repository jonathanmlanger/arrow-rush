# ARROW RUSH - a CodeX reaction game
# Press the button that matches the word. It keeps getting faster!
# Watch out for red DON'T PRESS rounds after you hit 10 points.

from codex import *
from time import sleep, ticks_ms, ticks_diff
import random

# ========== TWEAK ZONE (VARIABLES) ==========
# Change these numbers to change the game!
START_TIME = 1500     # milliseconds to react at the start
SPEED_UP = 0.95       # each hit multiplies the time by this (smaller = harder)
FASTEST = 400         # the game never gets faster than this
LIVES = 3             # how many misses you get (max 4)
TRICK_START = 10      # score when DON'T PRESS rounds begin
TRICK_CHANCE = 20     # percent chance of a DON'T PRESS round

# ========== LISTS ==========
# Item 0 in each list goes together, item 1 goes together, and so on.
WORDS = ["UP", "DOWN", "LEFT", "RIGHT"]
BUTTONS = [BTN_U, BTN_D, BTN_L, BTN_R]
COLORS = [BLUE, GREEN, ORANGE, PURPLE]

# ========== HELPERS ==========
def center_text(text, y, color, scale):
    # Each letter is about 8 pixels wide times the scale
    x = (240 - len(text) * 8 * scale) // 2
    if x < 0:
        x = 0
    display.draw_text(text, x=x, y=y, color=color, scale=scale)


def flush_buttons():
    # Clear old button presses so they don't count in the next round
    for b in BUTTONS:
        buttons.was_pressed(b)
    buttons.was_pressed(BTN_A)
    buttons.was_pressed(BTN_B)


def show_lives(lives):
    # FOR LOOP: one pixel per life, green = still alive
    for i in range(4):
        if i < lives:
            pixels.set(i, GREEN)
        else:
            pixels.set(i, BLACK)


def combo_flash():
    for i in range(4):
        pixels.set(i, YELLOW)
    sleep(0.2)


def wait_for_a():
    flush_buttons()
    while not buttons.was_pressed(BTN_A):
        sleep(0.05)


# ========== SCREENS ==========
def title_screen(best):
    display.fill(BLACK)
    center_text("ARROW", 45, YELLOW, 4)
    center_text("RUSH", 90, YELLOW, 4)
    center_text("Best: " + str(best), 150, WHITE, 2)
    center_text("Press A", 190, CYAN, 2)
    show_lives(LIVES)
    wait_for_a()


def countdown():
    for n in [3, 2, 1]:
        display.fill(BLACK)
        center_text(str(n), 90, WHITE, 6)
        sleep(0.5)
    display.fill(BLACK)
    center_text("GO!", 90, GREEN, 6)
    sleep(0.3)


def game_over(score, new_best):
    display.fill(BLACK)
    center_text("GAME", 30, RED, 4)
    center_text("OVER", 75, RED, 4)
    center_text("Score: " + str(score), 135, WHITE, 2)
    if new_best:
        center_text("NEW BEST!", 165, YELLOW, 2)
    center_text("A = again", 205, CYAN, 2)
    sleep(1)  # stops an accidental instant restart
    wait_for_a()


# ========== ROUNDS ==========
def arrow_round(time_limit, score):
    pick = random.randint(0, 3)          # RANDOM: choose a word
    flush_buttons()
    display.fill(COLORS[pick])
    center_text(str(score), 10, WHITE, 2)
    center_text(WORDS[pick], 100, WHITE, 5)

    start = ticks_ms()
    # WHILE LOOP: keep checking buttons until time runs out
    while ticks_diff(ticks_ms(), start) < time_limit:
        for i in range(4):
            if buttons.was_pressed(BUTTONS[i]):
                return i == pick         # True if right button, False if wrong
        sleep(0.01)
    return False                         # too slow!


def trick_round(time_limit, score):
    flush_buttons()
    display.fill(RED)
    center_text(str(score), 10, WHITE, 2)
    center_text("DON'T", 75, WHITE, 5)
    center_text("PRESS!", 130, WHITE, 5)

    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < time_limit:
        for b in BUTTONS:
            if buttons.was_pressed(b):
                return False             # you pressed, you lose a life
        sleep(0.01)
    return True                          # you waited it out


# ========== THE GAME ==========
def play_game():
    score = 0
    lives = LIVES
    streak = 0
    time_limit = START_TIME

    show_lives(lives)
    countdown()

    while lives > 0:
        # IF / ELSE: decide which kind of round to play
        trick = score >= TRICK_START and random.randint(1, 100) <= TRICK_CHANCE
        if trick:
            hit = trick_round(time_limit, score)
        else:
            hit = arrow_round(time_limit, score)

        if hit:
            score = score + 1
            streak = streak + 1
            time_limit = int(time_limit * SPEED_UP)
            if time_limit < FASTEST:
                time_limit = FASTEST
            if streak % 5 == 0:
                combo_flash()
        else:
            lives = lives - 1
            streak = 0
            display.fill(RED)
            center_text("MISS", 95, WHITE, 5)
            sleep(0.3)

        show_lives(lives)
        display.fill(BLACK)
        sleep(0.15)

    return score


# ========== MAIN LOOP ==========
best = 0
while True:
    title_screen(best)
    score = play_game()
    new_best = False
    if score > best:
        best = score
        new_best = True
    game_over(score, new_best)
