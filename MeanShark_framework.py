import threading
import time
import curses
from scapy.all import sniff
from start_menu import StartMenu

class Framework:
    def __init__(self):
        self.interface = None
        curses.wrapper(self.main)

    def paquet_callback(self, paquet):
        self.start_menu.window.addstr(3, 3, paquet.summary(), curses.color_pair(1))
        self.start_menu.window.refresh()
        print(paquet.summary())

    def main(self, stdscr):
        stdscr.clear()
        curses.start_color()
        self.start_menu = StartMenu(stdscr, " MeanShark Framework ", 8, 117, 1, 0)
        self.start_menu.main()
        self.interface = self.start_menu.get_interface()
        print(self.interface)
        self.start_sniffing()

    def start_sniffing(self):
        sniff_thread = threading.Thread(target=sniff, kwargs={"prn": self.paquet_callback, "iface": self.interface}, daemon=True)
        sniff_thread.start()
        time.sleep(5)

if __name__ == '__main__':
    framework = Framework()
