import sys
import random
import time
import threading

try:
    import msvcrt  # Windows
    getch = msvcrt.getch
except ImportError:
    import tty, termios  # Unix
    def getch():
        import sys
        import select
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            [i, o, e] = select.select([sys.stdin.fileno()], [], [], 0.05)
            if i:
                ch = sys.stdin.read(1)
            else:
                ch = ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode()

# Matrix-style color
GREEN = '\033[92m'
BOLD = '\033[1m'
RESET = '\033[0m'
CLEAR = '\033[2J\033[H'

# Some example "code" lines (can add more/replace with your own)
CODE_LINES = [
    'def hack_the_gibson():',
    '    while not caught:',
    '        bypass_firewall()',
    '        print("ACCESS GRANTED")',
    'for passwd in passwords:',
    '    if crack(passwd):',
    '        print("HACKED")',
    '0x3f8a1b2c = memory_leak()',
    'system("sudo rm -rf /")',
    'class Exploit:',
    '    def __init__(self):',
    '        self.payload = []',
    'if __name__ == "__main__":',
    '    hack_the_world()',
    '#include <stdio.h>',
    'int main() {',
    'printf("PWNED\\n");',
    'curl http://example.com/secret > dump.txt',
    'ssh root@192.168.0.1',
]
RANDOM_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<>!@#$%^&*()[]{};:"

def random_code_line():
    if random.random() < 0.5:
        return ''.join(random.choice(RANDOM_CHARS) for _ in range(random.randint(30, 70)))
    else:
        return random.choice(CODE_LINES)

def print_matrix_line():
    print(f"{GREEN}{BOLD}{random_code_line()}{RESET}")

def access_granted_popup():
    popup = [
        "╔══════════════════════╗",
        "║   ACCESS GRANTED!    ║",
        "╚══════════════════════╝"
    ]
    for line in popup:
        print(f"\033[1;32m{line}\033[0m")
    print()

def fake_hacking_sequence():
    print(CLEAR)
    print(f"{GREEN}{BOLD}Initializing hack...{RESET}\n")
    time.sleep(0.5)
    for i in range(10):
        print_matrix_line()
        time.sleep(0.1)
    print(f"\n{GREEN}{BOLD}>>> HACK SUCCESSFUL! SYSTEM BREACHED!{RESET}\n")
    time.sleep(1.8)
    input(f"{BOLD}Press Enter to continue...{RESET}")
    print(CLEAR)

def main():
    print(CLEAR)
    print(f"{GREEN}{BOLD}*** HACKER TYPER ***{RESET}")
    print(f"Start mashing your keyboard. Press ESC or Ctrl+C to quit.\n")
    popup_thread = None
    hack_sequence = False
    while True:
        char = getch()
        if char in [b'\x1b', b'\x03']:  # ESC or Ctrl+C
            print(RESET)
            break

        # Secret minigame: type "hack" quickly to trigger
        if char.decode(errors='ignore').lower() == 'h':
            hack_sequence = True
            buffer = 'h'
            sys.stdout.write(f"{GREEN}{BOLD}h{RESET}")
            sys.stdout.flush()
            for _ in range(3):
                ch = getch()
                if ch in [b'\x1b', b'\x03']:
                    print(RESET)
                    return
                buffer += ch.decode(errors='ignore')
                sys.stdout.write(f"{GREEN}{BOLD}{ch.decode(errors='ignore')}{RESET}")
                sys.stdout.flush()
            if buffer.lower() == 'hack':
                fake_hacking_sequence()
            continue

        # Randomly trigger popups
        if random.random() < 0.04:
            access_granted_popup()

        print_matrix_line()
        time.sleep(0.01 + random.random()*0.06)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(RESET)
        sys.exit(0)