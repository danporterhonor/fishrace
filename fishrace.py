import curses
import random
import sys
from curses import wrapper
from dataclasses import dataclass
from time import sleep

from utils.utils import join_words, read_names_from_file

names = read_names_from_file('names.txt')

if len(sys.argv) > 1:
    speed = float(sys.argv[1])
else:
    speed = 5.0

fish_emojis = ["🐠", "🐡", "🐟", "🦈", "🐬", "🐳","🐙","🦑","🦐"]
bubble_animation = [".", "o", "O", "0", "O", "o", "."]


@dataclass
class fish:
    name: str
    position: int
    icon: str = "🐟"

def draw_names(stdscr, pad, fishies):
    rows, cols = stdscr.getmaxyx()
    pad.clear()
    pad.addstr(0,0,f"{'Fish Trophy Racer'.center(cols,' ')}", curses.color_pair(4))
    pad.addstr(0,0,f"╔{'═'*19}╗", curses.color_pair(2))
    idx = 0
    for idx, fish in enumerate(fishies):
        pad.addstr(idx+1,0,f"║ {fish.icon} {fish.name[:14].ljust(14)} ║", curses.color_pair(2))
    pad.noutrefresh(0, 0, 0, 0, rows-1, cols-1)
    pad.addstr(idx+2,0,f"╚{'═' * 19}╝", curses.color_pair(2))
    stdscr.refresh()


def draw_fish(pad, fishies):
    for idx, fish in enumerate(fishies):
        pad.addch(idx + 1,fish.position,fish.icon)

def draw_bubble(pad, bubbles, cols):
    for idx, bubble in enumerate(bubbles):
        bubble_i = bubble[0]
        position = bubble[1]
        pad.addstr(position[0], position[1], " ", curses.color_pair(3))
        if bubble_i == len(bubble_animation) - 1:
          position = (position[0] - 1, position[1])
        if position[0] < 2:
           position = (len(names)+1, random.randint(21, cols-2))
        new_bubble = ((bubble_i + 1) % len(bubble_animation), position)
        bubbles[idx] = new_bubble
    for bubble_i, position in bubbles:
        pad.addstr(position[0], position[1], bubble_animation[bubble_i], curses.color_pair(3))


def winning_fish(fishies):
    for fish in fishies:
        if fish.position <= 21:
            return fish
    return None

def get_leading_fish(fishies):
    leading_fish = []
    lowest_position = None
    for fish in fishies:
        if lowest_position is None or fish.position < lowest_position:
            lowest_position = fish.position
            leading_fish = [fish]
            continue
        if fish.position == lowest_position:
            lowest_position = fish.position
            leading_fish.append(fish)
    return leading_fish

def get_leaders(fishies):
    fishies.sort(key=lambda x: x.position)
    num_leaders = min(5, len(fishies))
    leader_board = ""
    for idx, fish in enumerate(fishies[:num_leaders]):
        leader_board += f"{idx+1}. {fish.name[:16]} {fish.icon}  "
    return leader_board


def main(stdscr):
    rows, cols = stdscr.getmaxyx()
    curses.init_pair(1, curses.COLOR_BLACK, 24)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLUE, 24)
    curses.init_pair(4, curses.COLOR_WHITE, 25)
    all_fish = [fish(name, cols-2, random.choice(fish_emojis)) for name in names]

    density = .002
    total_bubble = int(cols * len(names) * density)
    bubbles = []
    for _ in range(total_bubble):
        bubble_start = random.randrange(len(bubble_animation))
        position_x_y = (random.randint(1, len(names)+1), random.randint(21, cols-2))
        bubbles.append((bubble_start, position_x_y))


    pad = curses.newpad(max(len(names) + 4,35,rows), max(81,cols))
    stdscr.bkgd(' ', curses.color_pair(1))
    pad.bkgd(' ', curses.color_pair(1))
    draw_names(stdscr, pad, all_fish)
    draw_fish(pad, all_fish)
    pad.noutrefresh(0, 0, 0, 0, rows-1, cols-1)
    curses.doupdate()
    stdscr.getch()

    winner = None
    leading_fish = []
    while True:
        if not winning_fish(all_fish):
            moving_fish = random.choice(all_fish)
            moving_fish.position -= 1
            leading_fish = get_leading_fish(all_fish)
            draw_fish(pad, all_fish)
            if len(leading_fish) == 1:
                pad.addstr(1 + len(all_fish), 0,f" {leading_fish[0].name} is in the lead!".center(cols-1), curses.color_pair(4))
            if len(leading_fish) > 1:
                pad.addstr(1 + len(all_fish), 0,f" {join_words([fish.name for fish in leading_fish[:3]])} are tied for the lead! ".center(cols-1), curses.color_pair(4))
            pad.noutrefresh(1, 21, 1, 21, rows-1, cols-1)
            curses.doupdate()
            sleep(0.005 / speed)
        else:
            if winner is None:
                sleep(.5)
                winner = winning_fish(all_fish)
                winner_x = int(cols/2 - 12)
                winner_y = int(len(all_fish)/2 - 2)
                pad.clear()
                leaders = get_leaders(all_fish)
                pad.nodelay(True)
            draw_bubble(pad, bubbles, cols)
            width = len(winner.name) + 17
            pad.addstr(winner_y,winner_x,f"╔{'═'*width}╗", curses.color_pair(2))
            pad.addstr(winner_y + 1,winner_x, f"║{' '*width}║", curses.color_pair(2))
            pad.addstr(winner_y + 2,winner_x, f"║ 🏆 {winner.name} {winner.icon} wins! 🏆 ║", curses.color_pair(2))
            pad.addstr(winner_y + 3,winner_x, f"║{' '*width}║", curses.color_pair(2))
            pad.addstr(winner_y + 4,winner_x,f"╚{'═' * width}╝", curses.color_pair(2))
            pad.addstr(1 + len(all_fish), 0,f"{leaders}   speed:{speed} [r]ace  [q]uit".center(cols-1), curses.color_pair(4))
            c = pad.getch()
            if c == ord('q'):
                exit()
            if c == ord('r'):
                winner = None
                pad.clear()
                all_fish = [fish(name, cols-2, random.choice(fish_emojis)) for name in names]

            pad.noutrefresh(1, 21, 1, 21, rows-1, cols-1)
            curses.doupdate()
            sleep(0.001)


wrapper(main)
