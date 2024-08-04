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
        self.output = None

    def main(self):
        curses.curs_set(0)
        curses.mousemask(1)
        curses.start_color()
        self.init_colors()
        self.define_objects()

        while self.is_enabled:

            self.stdscr.clear()
            self.draw_menu()
            self.draw_objects()
            self.stdscr.refresh()
            event = self.stdscr.getch()
            self.handle_event(event)

        self.screen.clear()
        self.screen.refresh()


    def define_objects(self):
        self.button_live_detection = Button(self.window, "Live-Detection", 115, 2, 2, action=self.on_live_detection)
        self.button_post_mortem = Button(self.window, "Post-Mortem Detection", 135, 2, 2, action=self.on_post_mortem)
        self.button_select_interface = Button(self.window, "Select Interface", 93, 2, 4 if self.is_interface_selected else 3,
                                         action=self.select_interface)

        self.button_live_detection.next_right = self.button_post_mortem
        self.button_live_detection.next_left = self.button_select_interface
        self.button_post_mortem.next_left = self.button_live_detection
        self.button_select_interface.next_right = self.button_live_detection

        self.add_button(self.button_live_detection)
        self.add_button(self.button_post_mortem)
        self.add_button(self.button_select_interface)
        if not self.is_clickable_obj_selected():
            self.select_object(self.button_live_detection)


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
            self.window.addstr(3, 3, 'Interface : {}'.format(self.interface), curses.color_pair(4))
            self.clickable_objects[self.clickable_objects.index(self.button_live_detection)].change_color(2)
        else:
            self.window.addstr(3, 3, 'Interface : Undefined',curses.color_pair(5))
            self.clickable_objects[self.clickable_objects.index(self.button_live_detection)].change_color(6)
        self.draw_objects()
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
            self.handle_mouse_event(mouse_x, mouse_y)
        else:
            self.handle_keyboard_event(event)

    def on_live_detection(self):
        if self.is_interface_selected:
            self.is_enabled = False
            self.output = 1

    def on_post_mortem(self):
        if self.is_interface_selected:
            self.is_enabled = False
            self.output = 0

    def select_interface(self):
        interfaces = psutil.net_if_addrs()
        interface_names = list(interfaces.keys())
        selection_win = SelectBar(self.stdscr, 1, self.height, interface_names)
        self.add_select_bar(selection_win)
        self.draw()
        self.is_interface_selected = False

        while not self.is_interface_selected:
            event = self.stdscr.getch()
            if event in (curses.KEY_UP, curses.KEY_DOWN):
                selection_win.handle_event(event)
            elif event == ord('\n'):
                self.interface = selection_win.get_value()
                self.is_interface_selected = True
                self.remove_obj(selection_win)
                break
            elif event == ord('q'):
                break



    def get_interface(self):
        return self.interface
