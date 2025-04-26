import os
import readline 
import sys
import tty
import termios
import fcntl
import time

class EditCommand:
    #Base class for all editable commands.
    def execute(self, buffer):
        raise NotImplementedError
    
    def undo(self, buffer):
        raise NotImplementedError

class LineEditCommand(EditCommand):
    #Tracks changes to a single line.
    def __init__(self, line_num, old_text, new_text):
        self.line_num = line_num
        self.old_text = old_text
        self.new_text = new_text
    
    def execute(self, buffer):
        if self.line_num < len(buffer.lines):
            buffer.lines[self.line_num] = self.new_text
    
    def undo(self, buffer):
        if self.line_num < len(buffer.lines):
            buffer.lines[self.line_num] = self.old_text

class InsertLineCommand(EditCommand):
    #Tracks line insertion.
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text
    
    def execute(self, buffer):
        buffer.lines.insert(self.line_num, self.text)
    
    def undo(self, buffer):
        if self.line_num < len(buffer.lines):
            del buffer.lines[self.line_num]

class DeleteLineCommand(EditCommand):
    #Tracks line deletion.
    def __init__(self, line_num, text):
        self.line_num = line_num
        self.text = text
    
    def execute(self, buffer):
        if self.line_num < len(buffer.lines):
            del buffer.lines[self.line_num]
    
    def undo(self, buffer):
        buffer.lines.insert(self.line_num, self.text)


        
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
        self.undo_stack = []  # Stack for undo commands
        self.redo_stack = []  # Stack for redo commands

    def push_undo_command(self, command):
        #Push a command to the undo stack and clear redo stack.
        self.undo_stack.append(command)
        if len(self.undo_stack) > 120:  # Limit history
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        """Undo the last action with user-friendly feedback."""
        if not self.undo_stack:
            self._show_status_message("Nothing to undo")
            return
    
        command_type = type(self.undo_stack[-1]).__name__
        action_map = {
            'LineEditCommand': 'edit',
            'InsertLineCommand': 'insertion',
            'DeleteLineCommand': 'deletion'
        }
        action = action_map.get(command_type, 'change')
        
        self._show_status_message(f"Undoing last {action}")
        command = self.undo_stack.pop()
        command.undo(self)
        self.redo_stack.append(command)
        self.dirty = True

    def redo(self):
        """Redo the last undone action with user-friendly feedback."""
        if not self.redo_stack:
            self._show_status_message("Nothing to redo")
            return
        
        command_type = type(self.redo_stack[-1]).__name__
        action_map = {
            'LineEditCommand': 'edit',
            'InsertLineCommand': 'insertion',
            'DeleteLineCommand': 'deletion'
        }
        action = action_map.get(command_type, 'change')
        
        self._show_status_message(f"Redoing last {action}")
        command = self.redo_stack.pop()
        command.execute(self)
        self.undo_stack.append(command)
        self.dirty = True
        
    def _show_status_message(self, message):
        """Helper method to display status messages consistently."""
        print(f"\n{message}", end='')
        time.sleep(0.355)  # Brief pause so user can read the message
        sys.stdout.flush()
        # Move cursor back up to overwrite the status message
        sys.stdout.write("\033[F")  # Move up one line
        sys.stdout.write("\033[K")  # Clear the line
        
        
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
        os.system('clear')
        print(f"Editing: {self.filename or 'New file'}")
        print("Commands: ↑/↓, PgUp/PgDn/End - Navigate, Enter - Edit,\n"
              "\t   Ctrl+B/F - Undo/Redo, S - Save, Q - Quit")
        print("-" * 80)
        
        # Clamp display range to valid lines
        start = self.display_start
        end = min(start + self.display_lines, len(self.lines))
    
        for i in range(start, end):  # Now guaranteed safe
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
                
        # Store original line for undo
        old_text = self.lines[self.current_line]
                
        # Set up readline with existing line content
        readline.set_startup_hook(lambda: readline.insert_text(old_text))        
        try:
            # Show prompt with line number and previous text
            prompt = f"{self.current_line+1:4d} [edit]: "
            new_text = input(prompt).rstrip('\n')
            
            if new_text != old_text:
                # Create and execute an undoable command (using class-based approach)
                cmd = LineEditCommand(self.current_line, old_text, new_text)
                self.push_undo_command(cmd)
                cmd.execute(self)
                self.dirty = True
        finally:
            # Clean up readline hook
            readline.set_startup_hook(None)

    def insert_line(self):
        # Create and execute an undoable command (using class-based approach)
        cmd = InsertLineCommand(self.current_line + 1, "")
        self.push_undo_command(cmd)
        cmd.execute(self)
        
        # Original logic
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.current_line = len(self.lines) - 1
        self.dirty = True
            
    def delete_line(self):
        if self.lines:
            # Create and execute an undoable command (using class-based approach)
            cmd = DeleteLineCommand(self.current_line, self.lines[self.current_line])
            self.push_undo_command(cmd)
            cmd.execute(self)
        
            # Original logic
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

            # First check for undo/redo shortcuts (Ctrl+B and Ctrl+F)
            if ch == '\x02':  # Ctrl+B for undo
                return 'undo'
            elif ch == '\x06':  # Ctrl+F for redo
                return 'redo'
            
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
                            elif ch2[1] == 'F':  # End key
                                return '\x1b[F'

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
                sys.stdout.write("Command [↑↓, PgUp/PgDn/End, E(dit), I(nsert), D(el), S(ave), Q(uit)]: ")
                sys.stdout.flush()
                
                cmd = self.get_key_input()
                if not cmd:  # Skip if no command received
                    continue

                if cmd == 'undo':   # Ctrl+B for undo
                    self.undo()
                    continue
                elif cmd == 'redo':   # Ctrl+F for redo
                    self.redo()
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
                        sys.stdout.write('\n')
                        new_start = min(
                            len(self.lines) - self.display_lines,  # Don't overshoot
                            self.display_start + self.display_lines  # Normal jump
                        )
                        self.display_start = max(0, new_start)  # Clamp to 0
                        self.current_line = min(
                            len(self.lines) - 1,
                            self.current_line + self.display_lines
                        )
                    continue
                
                # Handle Ctrl+D (EOF), End and Ctrl+C first before other commands
                if cmd in ('\x04', '\x1b[F', '\x03'):
                    if cmd == '\x04' or cmd == '\x1b[F': 
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
                    print("Invalid key. Please use: ↑, ↓, PgUp, PgDn, End, E, Enter, I, D, S, Q")
                    os.system('read -p "Press enter to continue..."')
                
            except EOFError:
                # Secondary handling of Ctrl+D if it wasn't caught as '\x04'
                if self.lines:
                    self.current_line = len(self.lines) - 1
                    self.display_start = max(0, len(self.lines) - self.display_lines)
                continue

            except KeyboardInterrupt:
                # Show a message and continue editing
                print()
                print("^C - Use 'Q' to quit or continue editing")
                os.system('read -p "Press enter to continue..."')
                continue
