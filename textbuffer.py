import os
import readline 
import sys
import tty
import termios
import fcntl
import signal
import utils

# Register signal handler (for OS-level interrupts)
signal.signal(signal.SIGINT, utils.handle_sigint)

class TextBuffer:
    def __init__(self):
        self.lines = []
        self.filename = None
        self.dirty = False
        self.current_line = 0
        self.current_col = 0
        self.display_start = 0
        self.display_lines = 40
        self.edit_history = {}

    def load_file(self, filename):
        # Load file contents into buffer
        try:
            with open(filename, 'r') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
            self.filename = filename
            self.dirty = False
            self.current_line = 0
            self.current_col = 0
            return True
        except IOError:
            return False

    def save(self):
        # Save buffer contents to file
        if not self.filename:
            return False
            
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))
            self.dirty = False
            return True
        except IOError:
            return False

    def display(self):
        # Display visible portion of buffer with line numbers
        os.system('clear')
        print(f"Editing: {self.filename or 'New file'}")
        print("Commands: ↑/↓, PgUp/PgDn - Navigate, Enter - Edit, S - Save, Q - Quit")
        print("-" * 80)
        
        end_line = min(self.display_start + self.display_lines, len(self.lines))
        for i in range(self.display_start, end_line):
            line_num = i + 1
            prefix = ">" if i == self.current_line else " "
            print(f"{prefix}{line_num:4d}: {self.lines[i]}")

    def navigate(self, direction):
        # Move cursor up/down
        if direction == 'up' and self.current_line > 0:
            self.current_line -= 1
        elif direction == 'down' and self.current_line < len(self.lines) - 1:
            self.current_line += 1
        
        # Adjust scroll position if needed
        if self.current_line < self.display_start:
            self.display_start = self.current_line
        elif self.current_line >= self.display_start + self.display_lines:
            self.display_start = self.current_line - self.display_lines + 1

    def edit_current_line(self):
        # Edit the current line with previous text available
        if not self.lines:  # If buffer is completely empty
            self.lines.append("")
            self.current_line = 0
            
        # Ensure current_line is within bounds
        if self.current_line >= len(self.lines):
            self.current_line = len(self.lines) - 1
        
        # Store original line in history if not already there
        if self.current_line not in self.edit_history:
            self.edit_history[self.current_line] = self.lines[self.current_line]
            
        # Set up readline with existing line content
        readline.set_startup_hook(lambda: readline.insert_text(self.lines[self.current_line]))
        
        try:
            # Show prompt with line number and previous text
            prompt = f"{self.current_line+1:4d} [edit]: "
            new_line = input(prompt).rstrip('\n')
            
            if new_line != self.lines[self.current_line]:
                self.lines[self.current_line] = new_line
                self.dirty = True
        finally:
            # Clean up readline hook
            readline.set_startup_hook(None)

    def insert_line(self):
        # Insert a new line after current position
        self.lines.insert(self.current_line + 1, "")
        self.current_line += 1
        # Ensure we don't go out of bounds
        if self.current_line >= len(self.lines):
            self.current_line = len(self.lines) - 1
        self.dirty = True

    def delete_line(self):
        # Delete current line
        if self.lines:
            del self.lines[self.current_line]
            if self.current_line >= len(self.lines) and self.current_line > 0:
                self.current_line -= 1
            self.dirty = True

            
    def get_key_input(self):
        # Read a single key press, including arrow keys
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # Possible arrow key or other special key
                # Set non-blocking mode temporarily
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
                try:
                    ch2 = sys.stdin.read(2)  # Try to read 2 more characters
                    if len(ch2) == 2:
                        if ch2[0] == '[':
                            if ch2[1] in 'AB':  # Arrow keys
                                return ch + ch2
                            elif ch2[1] == '5':  # PgUp
                                ch3 = sys.stdin.read(1)
                                if ch3 == '~':
                                    return '\x1b[5~'
                            elif ch2[1] == '6':  # PgDn
                                ch3 = sys.stdin.read(1)
                                if ch3 == '~':
                                    return '\x1b[6~'
                except:
                    pass
                finally:
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                return ch  # Return just ESC if not special key
            return ch.lower() if ch else ''  # Return regular key as lowercase or empty string if no input
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def edit_interactive(self):
        # Main editing interface with proper key handling
        while True:
            self.display()
            try:
                sys.stdout.write("Command [↑↓, PgUp/PgDn, E(dit), I(nsert), D(el), S(ave), Q(uit)]: ")
                sys.stdout.flush()
                
                cmd = self.get_key_input()
                if not cmd:  # Skip if no command received
                    continue
                
                # Handle arrow keys
                if cmd in ('\x1b[A', '\x1b[B'):
                    sys.stdout.write('\n')
                    if cmd == '\x1b[A':
                        self.navigate('up')
                    elif cmd == '\x1b[B':
                        self.navigate('down')
                    continue
            
                # Handle PgUp/PgDn
                if cmd in ('\x1b[5~', '\x1b[6~'):
                    sys.stdout.write('\n')
                    if cmd == '\x1b[5~':  # PgUp
                        self.display_start = max(0, self.display_start - self.display_lines)
                        self.current_line = max(0, self.current_line - self.display_lines)
                    elif cmd == '\x1b[6~':  # PgDn
                        self.display_start = min(len(self.lines) - self.display_lines, 
                                                 self.display_start + self.display_lines)
                        self.current_line = min(len(self.lines) - 1, 
                                                self.current_line + self.display_lines)
                    continue
                
                # Handle Ctrl+D (EOF) and Ctrl+C first before other commands
                if cmd in ('\x04', '\x03'):
                    if cmd == '\x04': 
                        if self.lines:
                            self.current_line = len(self.lines) - 1
                            self.display_start = max(0, len(self.lines) - self.display_lines)
                        continue

                    elif cmd == '\x03':  # ASCII code for Ctrl+C
                        # Show a message and continue editing
                        print()
                        print("^C - Use 'Q' to quit or continue editing")
                        os.system('read -p "Press enter to continue..."')
                        continue
                    
                
                # Echo and process other commands
                sys.stdout.write(cmd + '\n')
                
                if cmd in ('', 'e', '\r', '\n'):
                    self.edit_current_line()
                elif cmd == 'i':
                    self.insert_line()
                elif cmd == 'd':
                    self.delete_line()
                elif cmd == 's':
                    if self.save():
                        print("File saved.")
                        self.edit_history.clear()
                    else:
                        print("Error saving file!")
                    os.system('read -p "Press enter to continue..."')
                elif cmd == 'q':
                    if self.dirty:
                        while True:
                            save = input("Save changes? (y/n): ").lower()
                            if save == 'y':
                                if self.save():
                                    print("Changes saved.")
                                    self.edit_history.clear()
                                    self.dirty = False
                                    return True  # Indicate save was performed
                                else:
                                    print("Error saving file!")
                                    continue
                            elif save == 'n':
                                print("Changes not saved.")
                                return False  # Indicate no save was performed
                            else:
                                print("Only Y/N!")
                    return None  # Indicate no changes needed saving
                else:
                    # Handle invalid key press
                    print("Invalid key. Please use: ↑, ↓, PgUp, PgDn, E, Enter, I, D, S, Q")
                    os.system('read -p "Press enter to continue..."')
                
            except EOFError:
                # Secondary handling of Ctrl+D if it wasn't caught as '\x04'
                if self.lines:
                    self.current_line = len(self.lines) - 1
                    self.display_start = max(0, len(self.lines) - self.display_lines)
                continue

            except KeyboardInterrupt:
                pass # Passing the interupt signal
