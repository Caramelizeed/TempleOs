#!/usr/bin/python3
"""
TempleOS Simulator in Python (No Curses Version)
A tribute to Terry A. Davis and TempleOS

This program simulates a TempleOS-like environment with:
- Simple text-based interface
- Bible verse generator
- Command-line interface
- Simple file system
"""

import os
import random
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

# ======== System Constants ========
VERSION = "1.0"
COLORS_ENABLED = True  # Set to False if ANSI colors cause issues

# ======== Terminal Colors (ANSI) ========
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    @staticmethod
    def color_text(text, color):
        if COLORS_ENABLED:
            return color + text + Colors.RESET
        return text

# ======== Bible Verses ========
BIBLE_VERSES = [
    "Genesis 1:1 - In the beginning God created the heaven and the earth.",
    "John 1:1 - In the beginning was the Word, and the Word was with God, and the Word was God.",
    "Psalm 23:1 - The LORD is my shepherd; I shall not want.",
    "Matthew 5:3 - Blessed are the poor in spirit: for theirs is the kingdom of heaven.",
    "Romans 3:23 - For all have sinned, and come short of the glory of God.",
    "Romans 6:23 - For the wages of sin is death; but the gift of God is eternal life through Jesus Christ our Lord.",
    "John 3:16 - For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
    "Philippians 4:13 - I can do all things through Christ which strengtheneth me.",
    "Jeremiah 29:11 - For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.",
    "Proverbs 3:5-6 - Trust in the LORD with all thine heart; and lean not unto thine own understanding. In all thy ways acknowledge him, and he shall direct thy paths."
]

# ======== Data Structures ========
@dataclass
class File:
    name: str
    content: str
    creation_time: float

@dataclass
class Directory:
    name: str
    files: Dict[str, File]
    subdirs: Dict[str, 'Directory']

# ======== File System ========
class FileSystem:
    def __init__(self):
        self.root = Directory("Root", {}, {})
        self.current_dir = self.root
        self.path = ["Root"]
        
        # Create initial files
        self.create_file("README.TXT", "Welcome to TempleOS Python Simulator\nVersion " + VERSION)
        self.create_file("BIBLE.TXT", "\n".join(BIBLE_VERSES))
    
    def create_file(self, name: str, content: str) -> bool:
        if name in self.current_dir.files:
            return False
        
        self.current_dir.files[name] = File(name, content, time.time())
        return True
    
    def read_file(self, name: str) -> Optional[str]:
        if name in self.current_dir.files:
            return self.current_dir.files[name].content
        return None
    
    def write_file(self, name: str, content: str) -> bool:
        if name in self.current_dir.files:
            self.current_dir.files[name].content = content
            return True
        return False
    
    def list_files(self) -> List[str]:
        return list(self.current_dir.files.keys())
    
    def create_dir(self, name: str) -> bool:
        if name in self.current_dir.subdirs:
            return False
        
        self.current_dir.subdirs[name] = Directory(name, {}, {})
        return True
    
    def change_dir(self, name: str) -> bool:
        if name == "..":
            if len(self.path) > 1:
                self.path.pop()
                parent_path = self.path.copy()
                self.current_dir = self.root
                for dir_name in parent_path[1:]:
                    self.current_dir = self.current_dir.subdirs[dir_name]
                return True
            return False
        
        if name in self.current_dir.subdirs:
            self.current_dir = self.current_dir.subdirs[name]
            self.path.append(name)
            return True
        return False
    
    def get_path(self) -> str:
        return "/".join(self.path)

# ======== Terminal ========
class SimpleTerminal:
    def __init__(self):
        self.fs = FileSystem()
        self.running = True
    
    def clear_screen(self):
        if os.name == 'nt':  # For Windows
            os.system('cls')
        else:  # For Unix/Linux/MacOS
            os.system('clear')
    
    def print_colored(self, text, color=Colors.WHITE):
        print(Colors.color_text(text, color))
    
    def run(self):
        self.show_welcome()
        
        while self.running:
            path_prompt = f"{self.fs.get_path()}> "
            print(Colors.color_text(path_prompt, Colors.CYAN), end='')
            
            try:
                command = input()
                self.process_command(command)
            except KeyboardInterrupt:
                print("\nExiting...")
                self.running = False
            except EOFError:
                print("\nExiting...")
                self.running = False
    
    def process_command(self, command: str):
        if not command:
            return
            
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Process commands
        if cmd == "exit" or cmd == "quit":
            self.running = False
        
        elif cmd == "help":
            self.show_help()
        
        elif cmd == "cls" or cmd == "clear":
            self.clear_screen()
        
        elif cmd == "dir" or cmd == "ls":
            self.list_directory()
        
        elif cmd == "cd":
            if not args:
                self.print_colored("Usage: cd <directory>", Colors.YELLOW)
            else:
                if not self.fs.change_dir(args[0]):
                    self.print_colored(f"Directory not found: {args[0]}", Colors.RED)
        
        elif cmd == "mkdir":
            if not args:
                self.print_colored("Usage: mkdir <directory>", Colors.YELLOW)
            else:
                if not self.fs.create_dir(args[0]):
                    self.print_colored(f"Could not create directory: {args[0]}", Colors.RED)
        
        elif cmd == "type" or cmd == "cat":
            if not args:
                self.print_colored("Usage: type <filename>", Colors.YELLOW)
            else:
                content = self.fs.read_file(args[0])
                if content is not None:
                    self.show_file_content(args[0], content)
                else:
                    self.print_colored(f"File not found: {args[0]}", Colors.RED)
        
        elif cmd == "edit":
            if not args:
                self.print_colored("Usage: edit <filename>", Colors.YELLOW)
            else:
                self.edit_file(args[0])
        
        elif cmd == "random" or cmd == "verse":
            self.show_random_verse()
        
        elif cmd == "mandelbrot":
            self.draw_mandelbrot()
        
        elif cmd == "create":
            if len(args) < 1:
                self.print_colored("Usage: create <filename>", Colors.YELLOW)
            else:
                if not self.fs.create_file(args[0], ""):
                    self.print_colored(f"File already exists: {args[0]}", Colors.RED)
                else:
                    self.print_colored(f"Created file: {args[0]}", Colors.GREEN)
        
        else:
            self.print_colored(f"Unknown command: {cmd}", Colors.RED)
    
    def show_welcome(self):
        self.clear_screen()
        self.print_colored("╔════════════════════════════════════════════════════════════════════════════╗", Colors.CYAN)
        self.print_colored("║                    TempleOS Python Simulator v" + VERSION + "                       ║", Colors.CYAN)
        self.print_colored("║                     A Tribute to Terry A. Davis                            ║", Colors.CYAN)
        self.print_colored("║                                                                            ║", Colors.CYAN)
        self.print_colored("║  \"God said, 'Let there be light.' And there was light.\" - Genesis 1:3      ║", Colors.YELLOW)
        self.print_colored("║                                                                            ║", Colors.CYAN)
        self.print_colored("║  Type 'help' for a list of commands                                        ║", Colors.GREEN)
        self.print_colored("╚════════════════════════════════════════════════════════════════════════════╝", Colors.CYAN)
        
        # Random verse
        verse = random.choice(BIBLE_VERSES)
        self.print_colored("\n" + verse, Colors.MAGENTA)
        print()
    
    def show_help(self):
        self.clear_screen()
        self.print_colored("TempleOS Python Simulator - Help", Colors.CYAN)
        print("\nCommands:")
        self.print_colored("  help        - Show this help", Colors.WHITE)
        self.print_colored("  cls, clear  - Clear screen", Colors.WHITE)
        self.print_colored("  dir, ls     - List files and directories", Colors.WHITE)
        self.print_colored("  cd <dir>    - Change directory", Colors.WHITE)
        self.print_colored("  mkdir <dir> - Create directory", Colors.WHITE)
        self.print_colored("  type <file> - Show file contents", Colors.WHITE)
        self.print_colored("  edit <file> - Edit file", Colors.WHITE)
        self.print_colored("  create <file> - Create a new file", Colors.WHITE)
        self.print_colored("  random, verse - Show random Bible verse", Colors.WHITE)
        self.print_colored("  mandelbrot   - Draw Mandelbrot fractal", Colors.WHITE)
        self.print_colored("  exit, quit   - Exit the simulator", Colors.WHITE)
        print("\nPress Enter to continue...")
        input()
        self.clear_screen()
    
    def list_directory(self):
        self.clear_screen()
        self.print_colored(f"Directory of {self.fs.get_path()}", Colors.CYAN)
        self.print_colored("=======================================================", Colors.CYAN)
        print()
        
        # List directories
        for dir_name in sorted(self.fs.current_dir.subdirs.keys()):
            self.print_colored(f"<DIR>    {dir_name}", Colors.BLUE)
        
        # List files
        for file_name in sorted(self.fs.current_dir.files.keys()):
            file = self.fs.current_dir.files[file_name]
            file_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(file.creation_time))
            self.print_colored(f"{file_time}    {file_name}", Colors.GREEN)
        
        print()
        self.print_colored(f"{len(self.fs.current_dir.files)} file(s), {len(self.fs.current_dir.subdirs)} directory(ies)", Colors.WHITE)
    
    def show_file_content(self, filename: str, content: str):
        self.clear_screen()
        self.print_colored(f"File: {filename}", Colors.CYAN)
        self.print_colored("=======================================================", Colors.CYAN)
        print()
        
        # Print the content
        print(content)
        
        print("\nPress Enter to continue...")
        input()
        self.clear_screen()
    
    def edit_file(self, filename: str):
        # Check if file exists, if not, create it
        content = self.fs.read_file(filename)
        if content is None:
            self.fs.create_file(filename, "")
            content = ""
        
        # Simple multiline editor
        self.clear_screen()
        self.print_colored(f"Editing: {filename}", Colors.CYAN)
        self.print_colored("Enter your text below. Type END on a single line when finished.", Colors.YELLOW)
        self.print_colored("Current content:", Colors.GREEN)
        print(content)
        
        print("\n--- Start editing (type END on a single line to finish) ---")
        
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        
        new_content = "\n".join(lines)
        self.fs.write_file(filename, new_content)
        self.print_colored(f"File {filename} saved.", Colors.GREEN)
    
    def show_random_verse(self):
        self.clear_screen()
        verse = random.choice(BIBLE_VERSES)
        self.print_colored("Random Bible Verse", Colors.CYAN)
        self.print_colored("=======================================================", Colors.CYAN)
        print()
        self.print_colored(verse, Colors.YELLOW)
        print("\nPress Enter to continue...")
        input()
        self.clear_screen()
    
    def draw_mandelbrot(self):
        self.clear_screen()
        self.print_colored("Mandelbrot Set", Colors.CYAN)
        self.print_colored("=======================================================", Colors.CYAN)
        print()
        
        # ASCII Mandelbrot renderer
        width, height = 70, 25
        x_min, x_max = -2.0, 1.0
        y_min, y_max = -1.0, 1.0
        max_iter = 30
        
        chars = " .,;!*#@"  # Different density characters
        
        for y in range(height):
            line = ""
            for x in range(width):
                # Map screen coordinates to complex plane
                c_real = x_min + (x_max - x_min) * x / (width - 1)
                c_imag = y_min + (y_max - y_min) * y / (height - 1)
                c = complex(c_real, c_imag)
                
                # Iterate
                z = 0
                for i in range(max_iter):
                    z = z * z + c
                    if abs(z) > 2:
                        break
                
                # Choose character based on iteration count
                if i == max_iter - 1:
                    char = chars[-1]
                else:
                    idx = i * len(chars) // max_iter
                    char = chars[idx]
                
                line += char
            
            # Print each line with a random color for a "rainbow" effect
            colors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
            color = random.choice(colors)
            self.print_colored(line, color)
        
        print("\nPress Enter to continue...")
        input()
        self.clear_screen()

# ======== Main Entry ========
if __name__ == "__main__":
    try:
        # Check if ANSI colors work in this terminal
        if os.name == 'nt':
            # Try to enable ANSI colors on Windows
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                COLORS_ENABLED = False
        
        terminal = SimpleTerminal()
        terminal.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")