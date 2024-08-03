import curses

def x_for_center_text(text, window):
    height, width = window.getmaxyx()
    text_height, text_width = 1, len(text)
    x = (width - text_width) // 2
    return x


class Menu:
    def __init__(self, screen, title, height, width, x, y):
        self.window = None
        self.screen = screen
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.title = title

    def draw(self):
        self.window = self.screen.subwin(self.height, self.width, self.y, self.x)
        self.window.box()
        self.center_title()
        self.window.refresh()

    def center_title(self):
        height, width = self.window.getmaxyx()
        text_height, text_width = 1, len(self.title)
        x = (width - text_width) // 2
        self.window.addstr(0, x, self.title, curses.color_pair(1))
        self.window.refresh()

    def draw_buttons(self, buttons):
        for button in buttons:
            button.draw()

    def draw_footer(self, text):
        x = x_for_center_text(text, self.window)
        self.window.addstr(6, 1 + x, text, curses.color_pair(1))

    def handle_mouse_event(self, mouse_x, mouse_y, buttons):
        for button in buttons:
            if button.is_pressed(mouse_x, mouse_y):
                button.action()


class SelectBar:
    def __init__(self, screen, x, y, choices):
        self.screen = screen
        self.x = x
        self.y = y
        self.choices = choices
        self.selected_index = 0

        self.height = len(choices) + 2
        self.width = max(len(choice) for choice in choices) + 4

        self.window = self.screen.subwin(self.height, self.width, self.y, self.x)
        self.window.box()

    def draw(self):
        self.window.clear()
        self.window.box()
        for idx, choice in enumerate(self.choices):
            if idx == self.selected_index:
                self.window.addstr(idx + 1, 2, choice, curses.A_REVERSE)
            else:
                self.window.addstr(idx + 1, 2, choice)
        self.window.refresh()

    def handle_event(self, event):
        if event == curses.KEY_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.choices)
        elif event == curses.KEY_UP:
            self.selected_index = (self.selected_index - 1) % len(self.choices)
        self.draw()

    def get_value(self):
        return self.choices[self.selected_index]

    def close(self):
        self.window.clear()


class Button:
    def __init__(self, screen, label, x, y, color, action=None):
        self.screen = screen
        self.label = label
        self.x = x
        self.y = y
        self.color = color
        self.height = 3
        self.width = len(label) + 4
        self.action = action  # Action to be performed on button press

    def draw(self):
        self.button_win = self.screen.subwin(self.height, self.width, self.y, self.x)
        self.button_win.box()
        self.button_win.addstr(1, 2, self.label, curses.color_pair(self.color))
        self.button_win.refresh()

    def is_pressed(self, x, y):
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            return True
        return False

    def change_color(self, color_pair):
        self.color = color_pair
        self.draw()

    def action(self):
        if self.action:
            self.action()
