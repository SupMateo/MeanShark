import threading
import time
import curses
import os
import platform
import ctypes
from scapy.all import sniff, IP, IPv6, TCP, UDP, ICMP
from start_menu import StartMenu
from live_menu import LiveMenu, PacketObject



class Framework:
    def __init__(self):
        self.interface = None
        curses.wrapper(self.main)

    def packet_callback(self, packet):
        self.packets_nbr += 1
        packet_object = PacketObject(self.packets_nbr,packet.summary(),self.live_menu.packet_menu.window)
        self.live_menu.packet_frame.add_packet(packet_object)
        self.start_menu.window.refresh()


    def main(self, stdscr):
        stdscr.clear()
        curses.start_color()
        self.start_menu = StartMenu(stdscr, " MeanShark Framework ", 8, 117, 45, 0)
        self.start_menu.main()
        if self.start_menu.output == 1:
            self.live_menu = LiveMenu(stdscr, " MeanShark Framework | Live Detection ", 50, 206, 1, 0)
            self.start_sniffing()
            self.live_menu.main()
        else :
            exit(0)
        self.interface = self.start_menu.get_interface()
        print(self.interface)


    def start_sniffing(self):
        self.packets_nbr = 0
        sniff_thread = threading.Thread(target=sniff, kwargs={"prn": self.packet_callback, "iface": self.interface}, daemon=True)
        sniff_thread.start()

if __name__ == '__main__':
    framework = Framework()
