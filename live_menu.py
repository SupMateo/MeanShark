import time
import curses
from threading import Thread

from ui import Menu, Button, SelectBar, Toolbar, ToolbarItem, PacketFrame, PacketObject

class LiveMenu(Menu):
    def __init__(self, screen, title, height, width, x, y):
        super().__init__(screen, title, height, width, x, y)
        self.interface = None
        self.is_interface_selected = False
        self.is_enabled = True
        self.stdscr = screen
        self.height = height
        self.draw()
        self.event = None

    '''
    def draw_separation(self):
        for y in range(self.height - 4):
            self.window.addstr(y + 3, 110, "|")
    '''

    def thread_packet_frame(self):
        while self.is_enabled:
            self.event = self.stdscr.getch()
            self.handle_event(self.event)



    def main(self):
        curses.curs_set(0)
        curses.mousemask(1)
        curses.start_color()
        self.define_objects()
        self.init_colors()
        self.define_objects()
        self.draw_menu()
        self.packet_menu.draw()



        thread = Thread(target=self.thread_packet_frame, daemon=True)
        thread.start()
        loop = 0



        while self.is_enabled:
            if loop < 50 :
                self.packet_frame.refresh_packets_display()
                self.packet_menu.window.erase()
                self.packet_menu.draw()
                self.packet_frame.draw()
                self.packet_menu.window.refresh()
                time.sleep(0.000001)
                loop += 1
            else :
                self.screen.clear()
                self.packet_frame.refresh_packets_display()
                self.packet_menu.draw()
                self.packet_frame.draw()
                self.draw_menu()
                self.screen.refresh()
                loop = 0


        self.screen.clear()
        self.screen.refresh()

    def define_objects(self):
        self.toolbar = Toolbar(self.window, items=[])
        self.add_normal_object(self.toolbar)
        self.file_item = ToolbarItem(self.toolbar, " File ")
        self.edit_item = ToolbarItem(self.toolbar, " Edit ")
        self.tools_item = ToolbarItem(self.toolbar, " Tools ")
        self.osint_item = ToolbarItem(self.toolbar, " OSINT ")
        self.about_item = ToolbarItem(self.toolbar, " About ")

        if not self.is_clickable_obj_selected():
            self.select_object(self.file_item)

        self.file_item.next_right = self.edit_item
        self.edit_item.next_right = self.tools_item
        self.tools_item.next_right = self.osint_item
        self.osint_item.next_right = self.about_item
        self.about_item.next_left = self.osint_item
        self.osint_item.next_left = self.tools_item
        self.tools_item.next_left = self.edit_item
        self.edit_item.next_left = self.file_item

        self.clickable_objects.extend([self.file_item, self.edit_item, self.tools_item, self.osint_item, self.about_item])
        self.packet_menu = Menu(screen=self.screen, title=" Packets ", height=46, width=100,x=105,y=3)

        self.packet_frame = PacketFrame(self.height - 5, 90, self.packet_menu)


    def init_colors(self):
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)

    def draw_menu(self):
        self.window = self.screen.derwin(self.height, self.width, self.y, self.x)
        self.window.box()
        self.center_title()
        self.draw_objects()
        self.window.refresh()

    def handle_event(self, event):
        if event == ord('q'):
            self.is_enabled = False
        elif event == curses.KEY_MOUSE:
            _, mouse_x, mouse_y, _, _ = curses.getmouse()
            self.handle_mouse_event(mouse_x, mouse_y)
        else:
            self.handle_keyboard_event(event)
