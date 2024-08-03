import curses
import psutil
from ui import Menu, SelectBar, Button
from neural_network.utils import Information

class StartMenu(Menu):
    def __init__(self, screen, title, height, width, x, y):
        super().__init__(screen, title, height, width, x, y)
        self.interface = None
        self.is_interface_selected = False
        self.is_enabled = True
        self.information = Information()
        self.stdscr = screen
        self.draw()

    def main(self):
        curses.curs_set(0)
        curses.mousemask(1)
        curses.start_color()
        self.init_colors()

        while self.is_enabled:
            self.stdscr.clear()
            self.draw_menu()
            self.stdscr.refresh()
            event = self.stdscr.getch()
            self.handle_event(event)

        self.screen.clear()
        self.screen.refresh()

    def init_colors(self):
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)

    def draw_menu(self):
        self.draw()
        if self.is_interface_selected:
            self.window.addstr(3, 3, "Interface : " + self.interface, curses.color_pair(4))
        else:
            self.window.addstr(3, 3, "Interface : Undefined", curses.color_pair(5))
        buttons = [
            Button(self.window, "Live-Detection", 71, 2, 2if self.is_interface_selected else 6, action=self.on_live_detection),
            Button(self.window, "Post-Mortem Detection", 91, 2, 2, action=self.on_post_mortem),
            Button(self.window, "Select Interface", 49, 2, 3 if self.is_interface_selected else 3,
                   action=self.select_interface)
            ]

        self.draw_buttons(buttons)

        text = "Developed by SupMateo on GitHub : https://github.com/SupMateo/MeanShark | Version {version}, {release_date}".format(
            version=self.information.info['version'],
            release_date=self.information.info['release_date']
        )
        self.draw_footer(text)

    def handle_event(self, event):
        if event == ord('q'):
            self.is_enabled = False
        elif event == curses.KEY_MOUSE:
            _, mouse_x, mouse_y, _, _ = curses.getmouse()
            buttons = [
                Button(self.window, "Live-Detection", 71, 2, 2, action=self.on_live_detection),
                Button(self.window, "Post-Mortem Detection", 91, 2, 2, action=self.on_post_mortem),
                Button(self.window, "Select Interface", 49, 2, 4 if self.is_interface_selected else 3, action=self.select_interface)
            ]
            self.handle_mouse_event(mouse_x, mouse_y, buttons)

    def on_live_detection(self):
        if self.is_interface_selected:
            self.is_enabled = False

    def on_post_mortem(self):
        # Implement post-mortem detection logic here
        pass

    def select_interface(self):
        interfaces = psutil.net_if_addrs()
        interface_names = list(interfaces.keys())
        selection_win = SelectBar(self.stdscr, 1, self.height, interface_names)
        selection_win.draw()
        self.is_interface_selected = False

        while not self.is_interface_selected:
            event = self.stdscr.getch()
            if event in (curses.KEY_UP, curses.KEY_DOWN):
                selection_win.handle_event(event)
            elif event == ord('\n'):
                self.interface = selection_win.get_value()
                self.is_interface_selected = True
                break
            elif event == ord('q'):
                exit(0)

    def get_interface(self):
        return self.interface
