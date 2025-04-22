import sys
import random
import time
import threading
import os
from Crypto.Cipher import AES

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
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
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
    'async def brute_force(target, wordlist):',
    '    for i, attempt in enumerate(wordlist):',
    '        print(f"Attempt {i}: {attempt}")',
    'def decrypt_aes(ciphertext, key):',
    '    iv = os.urandom(16)',
    '    return AES.new(key, AES.MODE_CBC, iv)',
    'class NetworkScanner:',
    '    def __init__(self, subnet):',
    '        self.targets = []',
    'subprocess.run(["nmap", "-sV", target_ip])',
    'with open("/etc/shadow", "rb") as f:',
    'password_hash = "$6$salt$hashedpasswordhere"',
    'for port in range(1, 65535):',
    '    if scanner.is_open(ip, port):',
    '        vulnerabilities.append(check_vuln(ip, port))',
    'def reverse_shell(ip, port):',
    '    s = socket.socket()',
    '    s.connect((ip, port))',
    'session = requests.post("https://target.com/login", data=payload)',
    'if "CSRF token invalid" in response.text:',
    '    token = extract_csrf(response.text)',
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
    
    # Step 1: Show scanning phase
    print(f"{YELLOW}{BOLD}[+] Scanning target systems...{RESET}")
    show_progress_bar()
    
    # Step 2: Show some IP addresses being scanned
    for i in range(5):
        ip = f"192.168.1.{random.randint(1, 254)}"
        print(f"{GREEN}[+] Scanning {ip}... {random.choice(['Open ports found', 'Firewall detected', 'Vulnerable services'])}{RESET}")
        time.sleep(0.3)
    
    # Step 3: Brute force animation
    print(f"\n{MAGENTA}{BOLD}[+] Attempting password brute force...{RESET}")
    passwords = ["admin123", "password", "123456", "qwerty", "letmein", "trustno1"]
    for pwd in passwords:
        print(f"{CYAN}[-] Trying: {pwd}{RESET}")
        time.sleep(0.2)
        if random.random() < 0.2:  # 20% chance of success on each password
            print(f"{GREEN}[+] Password match found: {pwd}{RESET}")
            break
    
    # Step 4: Exploit animation
    print(f"\n{RED}{BOLD}[+] Deploying exploit...{RESET}")
    show_progress_bar()
    
    # Step 5: Show code execution
    print(f"\n{BLUE}{BOLD}[+] Executing payload...{RESET}")
    for i in range(10):
        print_matrix_line()
        time.sleep(0.1)
    
    # Final success message with fancy ASCII art
    print(CLEAR)
    print(f"{GREEN}{BOLD}") 
    print("    _    ____ ____ _____ ____ ____    ____ ____      _    _   _ _____ _____ ____  ")
    print("   / \\  / ___/ ___| ____/ ___/ ___|  / ___|  _ \\    / \\  | \\ | |_   _| ____|  _ \\ ")
    print("  / _ \\| |  | |   |  _| \\___ \\___ \\  | |  _| |_) |  / _ \\ |  \\| | | | |  _| | | | |")
    print(" / ___ \\ |__| |___| |___ ___) |__) | | |_| |  _ <  / ___ \\| |\\  | | | | |___| |_| |")
    print("/_/   \\_\\____\\____|_____|____/____/   \\____|_| \\_\\/_/   \\_\\_| \\_| |_| |_____|____/ ")
    print(f"{RESET}\n")
    
    time.sleep(1.8)
    input(f"{BOLD}Press Enter to continue...{RESET}")
    print(CLEAR)

def rainbow_text(text):
    colors = ['\033[91m', '\033[93m', '\033[92m', '\033[94m', '\033[95m', '\033[96m']
    result = ""
    for i, char in enumerate(text):
        result += f"{colors[i % len(colors)]}{char}"
    return result + RESET

def show_progress_bar():
    progress = 0
    bar_width = 40
    while progress < bar_width:
        progress += random.randint(1, 3)
        progress = min(progress, bar_width)
        bar = "█" * progress + "░" * (bar_width - progress)
        percent = int((progress / bar_width) * 100)
        print(f"\r{GREEN}[{bar}] {percent}%{RESET}", end="")
        time.sleep(0.1)
    print("\nComplete!")

def matrix_rain(duration=3):
    width = 80
    lines = []
    for _ in range(20):
        lines.append([" "] * width)
    
    end_time = time.time() + duration
    print(CLEAR)
    
    while time.time() < end_time:
        # Generate new drops
        for _ in range(3):
            col = random.randint(0, width-1)
            lines[0][col] = random.choice("01")
        
        # Move drops down
        for i in range(len(lines)-1, 0, -1):
            lines[i] = lines[i-1].copy()
        lines[0] = [" "] * width
        
        # Print matrix
        print(CLEAR)
        for line in lines:
            print(f"{GREEN}{BOLD}{''.join(line)}{RESET}")
        time.sleep(0.1)

def random_popup():
    popups = [
        ["╔══════════════════════╗", "║   ACCESS GRANTED!    ║", "╚══════════════════════╝"],
        ["╔══════════════════════╗", "║  FIREWALL BYPASSED  ║", "╚══════════════════════╝"],
        ["╔══════════════════════════╗", "║  PASSWORD CRACKED: ******  ║", "╚══════════════════════════╝"],
        ["╔═════════════════════╗", "║  BACKDOOR INSTALLED ║", "╚═════════════════════╝"],
        ["╔═════════════════════════╗", "║  ENCRYPTION KEY CAPTURED  ║", "╚═════════════════════════╝"],
        ["╔════════════════════════╗", "║  DATA EXFILTRATION 100%  ║", "╚════════════════════════╝"],
    ]
    popup = random.choice(popups)
    for line in popup:
        print(f"\033[1;32m{line}\033[0m")
    print()

def decrypt_animation(text="TOP SECRET DATA"):
    encrypted = list("*" * len(text))
    print(f"\r{BOLD}{YELLOW}Decrypting: {''.join(encrypted)}{RESET}", end="")
    
    indices = list(range(len(text)))
    random.shuffle(indices)
    
    for idx in indices:
        time.sleep(0.1)
        encrypted[idx] = text[idx]
        print(f"\r{BOLD}{YELLOW}Decrypting: {''.join(encrypted)}{RESET}", end="")
    
    print()
    time.sleep(0.5)
    print(f"{GREEN}Decryption complete!{RESET}")

def show_help():
    print(CLEAR)
    print(f"{BOLD}{CYAN}HACKER TYPER - SPECIAL COMMANDS{RESET}")
    print(f"{YELLOW}------------------------{RESET}")
    print(f"{GREEN}hack{RESET} - Start the hacking sequence")
    print(f"{GREEN}matrix{RESET} - Show Matrix-style falling digits")
    print(f"{GREEN}decrypt{RESET} - Show a decryption animation")
    print(f"{GREEN}help{RESET} - Show this help screen")
    print(f"{GREEN}exit{RESET} - Exit the program")
    print(f"\n{BOLD}Press any key to return...{RESET}")
    getch()
    print(CLEAR)

def handle_special_command(command):
    if command == "hack":
        fake_hacking_sequence()
        return True
    elif command == "matrix":
        matrix_rain()
        return True
    elif command == "decrypt":
        decrypt_animation()
        return True
    elif command == "help":
        show_help()
        return True
    elif command == "exit":
        print(RESET)
        sys.exit(0)
    return False

def main():
    print(CLEAR)
    print(f"{GREEN}{BOLD}*** HACKER TYPER ***{RESET}")
    print(f"Start mashing your keyboard. Type {YELLOW}help{RESET} for special commands. Press ESC or Ctrl+C to quit.\n")
    
    command_buffer = ""
    
    while True:
        char = getch()
        
        # ESC or Ctrl+C to exit
        if char in [b'\x1b', b'\x03']:
            print(RESET)
            break
            
        # Enter key - check for commands
        if char in [b'\r', b'\n']:
            if handle_special_command(command_buffer.lower()):
                command_buffer = ""
                continue
            command_buffer = ""
            print()  # New line after enter
            continue
            
        # Backspace
        if char in [b'\x08', b'\x7f']:
            if command_buffer:
                command_buffer = command_buffer[:-1]
                # Clear the current line and reprint
                print(f"\r{' ' * 80}\r", end="")
                continue
                
        # Add char to buffer if printable
        try:
            decoded_char = char.decode(errors='ignore')
            if decoded_char.isprintable():
                command_buffer += decoded_char
        except:
            pass
            
        # Randomly trigger popups (less frequently when typing commands)
        if len(command_buffer) <= 1 and random.random() < 0.04:
            random_popup()

        if len(command_buffer) <= 1 and random.random() < 0.05:  # 5% chance
            print(f"{BOLD}{rainbow_text('SECURITY BREACH DETECTED')}{RESET}")

        # Only print matrix lines if not actively typing a command
        if len(command_buffer) <= 3:
            print_matrix_line()
            time.sleep(0.01 + random.random()*0.06)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(RESET)
        sys.exit(0)