import time, os, random

FONT = {
    'A': [" ██ ", "█  █", "████", "█  █", "█  █"],
    'B': ["███ ", "█  █", "███ ", "█  █", "███ "],
    'C': [" ██ ", "█  █", "█   ", "█  █", " ██ "],
    'D': ["███ ", "█  █", "█  █", "█  █", "███ "],
    'E': ["████", "█   ", "███ ", "█   ", "████"],
    'F': ["████", "█   ", "███ ", "█   ", "█   "],
    'G': [" ██ ", "█   ", "█ ██", "█  █", " ██ "],
    'H': ["█  █", "█  █", "████", "█  █", "█  █"],
    'I': ["███", " █ ", " █ ", " █ ", "███"],
    'J': ["  ██", "   █", "   █", "█  █", " ██ "],
    'K': ["█  █", "█ █ ", "██  ", "█ █ ", "█  █"],
    'L': ["█   ", "█   ", "█   ", "█   ", "████"],
    'M': ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
    'N': ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
    'O': [" ██ ", "█  █", "█  █", "█  █", " ██ "],
    'P': ["███ ", "█  █", "███ ", "█   ", "█   "],
    'Q': [" ██ ", "█  █", "█  █", "█ ██", " ███"],
    'R': ["███ ", "█  █", "███ ", "█ █ ", "█  █"],
    'S': [" ██ ", "█   ", " ██ ", "   █", "███ "],
    'T': ["████", " █  ", " █  ", " █  ", " █  "],
    'U': ["█  █", "█  █", "█  █", "█  █", " ██ "],
    'V': ["█   █", "█   █", "█   █", " █ █ ", "  █  "],
    'W': ["█   █", "█   █", "█ █ █", "██ ██", "█   █"],
    'X': ["█   █", " █ █ ", "  █  ", " █ █ ", "█   █"],
    'Y': ["█   █", " █ █ ", "  █  ", "  █  ", "  █  "],
    'Z': ["████", "   █", "  █ ", " █  ", "████"],
    '0': [" ██ ", "█  █", "█  █", "█  █", " ██ "],
    '1': ["  █ ", " ██ ", "  █ ", "  █ ", "████"],
    '2': ["███ ", "   █", " ██ ", "█   ", "████"],
    '3': ["███ ", "   █", " ██ ", "   █", "███ "],
    '4': ["█  █", "█  █", "████", "   █", "   █"],
    '5': ["████", "█   ", "███ ", "   █", "███ "],
    '6': [" ██ ", "█   ", "███ ", "█  █", " ██ "],
    '7': ["████", "   █", "  █ ", " █  ", " █  "],
    '8': [" ██ ", "█  █", " ██ ", "█  █", " ██ "],
    '9': [" ██ ", "█  █", " ███", "   █", " ██ "],
    ' ': ["    ", "    ", "    ", "    ", "    "],
    '!': [" █ ", " █ ", " █ ", "   ", " █ "],
    '?': ["███ ", "   █", " ██ ", "    ", " █  "],
    '.': ["   ", "   ", "   ", "   ", " █ "],
    '-': ["    ", "    ", " ██ ", "    ", "    "],
}

COLORS = [
    '\033[92m',  # green
    '\033[96m',  # cyan
    '\033[95m',  # magenta
    '\033[93m',  # yellow
    '\033[91m',  # red
    '\033[94m',  # blue
]
RESET = '\033[0m'
BLINK = '\033[5m'
CLEAR = '\033[2J\033[H'

def big_message(msg):
    msg = msg.upper()
    rows = ['' for _ in range(5)]
    for c in msg:
        fc = FONT.get(c, FONT[' '])
        for i in range(5):
            rows[i] += fc[i] + "  "
    return rows

def glitchify(row):
    # Random blocks for glitch
    glitched = ''
    for ch in row:
        if ch == '█' and random.random() < 0.13:
            glitched += random.choice(['░','▒','▓'])
        else:
            glitched += ch
    return glitched

def scroll_message(rows, width=50, delay=0.07):
    msglen = len(rows[0])
    for pos in range(msglen + width):
        os.system('cls' if os.name == 'nt' else 'clear')
        color = random.choice(COLORS)
        for row in rows:
            # Glitch & blink a bit
            out = row[max(0,pos-width):pos]
            if random.random() < 0.06:
                print(f'{BLINK}{color}{glitchify(out):<{width}}{RESET}')
            else:
                print(f'{color}{out:<{width}}{RESET}')
        time.sleep(delay)

if __name__ == "__main__":
    msg = input("Type your message for the LED scroller:\n> ")
    rows = big_message(msg)
    while True:
        scroll_message(rows)