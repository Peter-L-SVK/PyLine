import os
import readline 

class TextBuffer:
    def __init__(self):
        self.lines = []
        self.filename = None
        self.dirty = False
        self.current_line = 0
        self.current_col = 0
        self.display_start = 0
        self.display_lines = 20
        self.edit_history = {}

    def load_file(self, filename):
        #Load file contents into buffer
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
        #Save buffer contents to file
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
        #Display visible portion of buffer with line numbers
        os.system('clear')
        print(f"Editing: {self.filename or 'New file'}")
        print("Commands: ↑/↓ - Navigate, Enter - Edit, S - Save, Q - Quit")
        print("-" * 80)
        
        end_line = min(self.display_start + self.display_lines, len(self.lines))
        for i in range(self.display_start, end_line):
            line_num = i + 1
            prefix = ">" if i == self.current_line else " "
            print(f"{prefix}{line_num:4d}: {self.lines[i]}")

    def navigate(self, direction):
        """Move cursor up/down"""
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
        #Edit the current line with previous text available
        if not self.lines:
            self.lines.append("")
            
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
        #Insert a new line after current position
        self.lines.insert(self.current_line + 1, "")
        self.current_line += 1
        self.dirty = True

    def delete_line(self):
        #Delete current line
        if self.lines:
            del self.lines[self.current_line]
            if self.current_line >= len(self.lines) and self.current_line > 0:
                self.current_line -= 1
            self.dirty = True

    def edit_interactive(self):
        #Main editing interface with enhanced line editing
        while True:
            self.display()
            try:
                cmd = input("Command [up, down, E(dit), I(nsert), D(el), S(ave), Q(uit)]: ").lower()
                
                if cmd in ('', 'e'):
                    self.edit_current_line()
                elif cmd == '↑' or cmd == 'up':
                    self.navigate('up')
                elif cmd == '↓' or cmd == 'down':
                    self.navigate('down')
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
                        input("Press Enter to continue...")
                elif cmd == 'q':
                    if self.dirty:
                        save = input("Save changes? (Y/N): ").lower()
                        if save == 'y':
                            self.save()
                    break
                
            except EOFError:
                if self.lines:  # Only if there are lines
                    self.current_line = len(self.lines) - 1
                    self.display_start = max(0, len(self.lines) - self.display_lines)
                continue
