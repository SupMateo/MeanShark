import os
import logging
import time
from datetime import datetime

from scapy.all import *
from scapy.layers.l2 import Ether

dirname = os.getcwd()
data_path = os.path.join(dirname, 'Dataset')
logging.basicConfig(level=logging.DEBUG,
                    format='\033[33m[MEANSHARK | %(asctime)s | %(levelname)s] \033[0m %(message)s')

class Statistics:
    def __init__(self, capture_list):
        self.capture_list = capture_list

    @property
    def ip_amount(self):
        return self.calculate_ip_amount()

    @property
    def port_amount(self):
        return self.calculate_port_amount()

    @property
    def bitrate(self):
        return self.calculate_bitrate()

    def calculate_ip_amount(self):
        ip_list = []
        for data_packet in self.capture_list:
            if data_packet.ip_src is not None and data_packet.ip_dst is not None:
                if data_packet.ip_src not in ip_list:
                    ip_list.append(data_packet.ip_src)
                if data_packet.ip_dst not in ip_list:
                    ip_list.append(data_packet.ip_dst)
        return len(ip_list)

    def calculate_port_amount(self):
        port_list = []
        for data_packet in self.capture_list:
            if data_packet.port_src is not None and data_packet.port_dst is not None:
                if data_packet.ip_src not in port_list:
                    port_list.append(data_packet.port_src)
                if data_packet.ip_dst not in port_list:
                    port_list.append(data_packet.port_dst)
        return len(port_list)


    def calculate_bitrate(self):
        if not self.capture_list:
            return 0
        first_time = self.capture_list[0].time
        last_time = self.capture_list[-1].time
        times = [first_time, last_time]
        time_objs = []
        for timers in times:
            time_objs.append(datetime.strptime(str(timers), "%H:%M:%S:%f"))
        times.clear()
        for time_obj in time_objs:
            times.append(time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6)

        total_size = sum(data_packet.length for data_packet in self.capture_list)
        total_time = times[-1] - times[0]
        return total_size / total_time if total_time != 0 else 0

class DataCapture:
    def __init__(self, list_of_data_packet=None):
        if list_of_data_packet is None:
            self.capture_list = []
        else:
            self.capture_list = list_of_data_packet

        self.stats = Statistics(self.capture_list)
        self.size = len(self.capture_list)

    def __iter__(self):
        return iter(self.capture_list)

    def __repr__(self):
        return f"{self.capture_list}"

    def __str__(self):
        return str("DataCapture : < "+str(self.capture_list)+">")

    def add_packet(self, data_packet):
        try:
            if isinstance(data_packet, DataPacket):
                self.capture_list.append(data_packet)
                self.size = len(self.capture_list)
            else:
                raise TypeError
        except TypeError:
            logging.error(f'Object of type {type(data_packet).__name__} is not of type DataPacket')

    def get_packet(self,index):
        return self.capture_list[index]

    def show(self,index=None):
        if index is None:
            for data_packet in self.capture_list:
                print("\033[94mPACKET N°"+str(self.capture_list.index(data_packet))+" :")
                data_packet.show()
            self.show_stats()

        else:
            print("\033[94mPACKET N°" + str(index) + " :")
            self.capture_list[index].show()


    def print_field(self, field_name, field_value):
        present_color = '\033[94m'
        none_color = '\033[91m'
        reset_color = '\033[0m'
        if field_value is not None:
            print(f"{present_color}{field_name} : {reset_color}{field_value}")
        else:
            print(f"{none_color}{field_name} : X")

    def show_stats(self):
        fields = [
            ("BITRATE (Bps)", self.stats.bitrate),
            ("AMOUNT OF IP", self.stats.ip_amount),
            ("AMOUNT OF PORT", self.stats.port_amount),
        ]
        print("\033[94mSTATISTICS : ")
        print("\033[94m---------------------------------------------------")
        for field_name, field_value in fields:
            self.print_field(field_name, field_value)
        print("\033[94m---------------------------------------------------")
        print()

class DataPacket:
    def __init__(self, type=None, protocol=None, length=None, data=None, ip_src=None, ip_dst=None, p_src=None,
                 p_dst=None,ack=None, flags=None, timestamp=None):
        self.type = type
        self.protocol = protocol
        self.length = length
        self.data = data
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.port_src = p_src
        self.port_dst = p_dst
        self.ack = ack
        self.flags = flags
        self.time = timestamp

    def __repr__(self):
        return "DataPacket < type : " + str(self.type) + " | " + str(self.length) + " bytes >"

    def print_field(self, field_name, field_value):
        present_color = '\033[94m'
        none_color = '\033[91m'
        reset_color = '\033[0m'
        if field_value is not None:
            print(f"{present_color}{field_name} : {reset_color}{field_value}")
        else:
            print(f"{none_color}{field_name} : X")

    def show(self):
        present_color = '\033[94m'
        fields = [
            ("TYPE", self.type),
            ("TIME (h:m:s:f)", self.time),
            ("LENGTH", self.length),
            ("PROTOCOL", self.protocol),
            ("ACK", self.ack),
            ("FLAGS",self.flags),
            ("IP SOURCE", self.ip_src),
            ("IP DESTINATION", self.ip_dst),
            ("PORT SRC", self.port_src),
            ("PORT DST", self.port_dst),
            ("DATA", self.data)
        ]
        print(present_color + "---------------------------------------------------")
        for field_name, field_value in fields:
            self.print_field(field_name, field_value)
        print(present_color + "---------------------------------------------------")
        print("")


class DataExtractor:
    def __init__(self, raw_capture):
        cap_path = os.path.join(data_path, raw_capture)
        if raw_capture.split('.')[-1] in ['pcap', 'pcapng']:
            try:
                self.raw_capture = rdpcap(cap_path)
                logging.info(f"{cap_path} loaded successfully !")
            except Exception as e:
                logging.error(e)
        else:
            logging.error('Capture must be pcap or pcapng file.')
            exit(1)

    @staticmethod
    def make_packet_obj(simple_packet, nbr):
        packet_nbr = nbr + 1
        type = simple_packet[Ether].type
        length = len(simple_packet)
        data = None
        ip_src = None
        ip_dst = None
        protocol = None
        p_src = None
        p_dst = None
        ack = None
        flags=None
        timestamp = datetime.fromtimestamp(float(simple_packet.time)).strftime('%H:%M:%S:%f')

        if ARP in simple_packet:
            ip_src = simple_packet[ARP].psrc
            ip_dst = simple_packet[ARP].pdst
            protocol = 0

        if IP in simple_packet:
            ip_src = simple_packet[IP].src
            ip_dst = simple_packet[IP].dst
            protocol = simple_packet[IP].proto

        if IPv6 in simple_packet:
            ip_src = simple_packet[IPv6].src
            ip_dst = simple_packet[IPv6].dst
            protocol = simple_packet[IPv6].nh

        transport_layer = simple_packet.getlayer(TCP) or simple_packet.getlayer(UDP) or simple_packet.getlayer(SCTP)
        if transport_layer:
            p_src = transport_layer.sport
            p_dst = transport_layer.dport
            if transport_layer == simple_packet.getlayer(TCP):
                ack = transport_layer.ack
                flags = transport_layer.flags

        if simple_packet.haslayer('Raw'):
            data = simple_packet['Raw'].load
        time.sleep(0.1)
        print("\r" + str(packet_nbr) + " packet(s) processed...", end='')
        return DataPacket(type=type, length=length, data=data, ip_src=ip_src, ip_dst=ip_dst, protocol=protocol,
                          p_src=p_src, p_dst=p_dst,ack=ack,flags=flags,timestamp=timestamp)

    def extract_data(self, split_capture=None):
        data_capture = DataCapture()
        if split_capture is None:
            for packet in self.raw_capture:
                data_capture.add_packet(self.make_packet_obj(packet, data_capture.size))
        else:
            for packet in split_capture:
                data_capture.add_packet(self.make_packet_obj(packet, data_capture.size))
        print("\n")
        return data_capture

    def split_raw_capture(self, packet_by_capture):
        split_cap = []
        packets = []
        for packet in self.raw_capture:
            if len(packets) < packet_by_capture:
                packets.append(packet)
            if len(packets) >= packet_by_capture:
                split_cap.append(packets)
                packets = []
        if len(packets) > 0:  # Add the last packets if they don't make a full batch
            split_cap.append(packets)
        logging.info(f"Capture split successfully in {len(split_cap)} part(s) !")
        return split_cap
