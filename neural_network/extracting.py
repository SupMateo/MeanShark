import os
import logging
from datetime import datetime
from scapy.all import *
from scapy.layers.l2 import Ether

import random

# Set up paths for dataset storage
dirname = os.getcwd()
data_path = os.path.join(dirname, 'Dataset')


class Statistics:
    """
    Class to calculate various statistics from a list of captured packets.
    """
    def __init__(self, capture_list):
        self.capture_list = capture_list
        self.bitrate_normalized = None
        self.ip_amount_normalized = None
        self.port_amount_normalized = None
        self.total_time_normalized = None

    @property
    def ip_amount(self):
        # Calculate the unique number of IPs
        return self.calculate_ip_amount()

    @property
    def port_amount(self):
        # Calculate the unique number of ports
        return self.calculate_port_amount()

    @property
    def bitrate(self):
        # Calculate the bitrate of the captured data
        return self.calculate_bitrate()

    @property
    def total_time(self):
        # Calculate the total time of the capture
        return self.calculate_total_time()

    def calculate_ip_amount(self):
        """Calculate the number of unique IP addresses."""
        ip_list = []
        for data_packet in self.capture_list:
            if data_packet.ip_src is not None and data_packet.ip_dst is not None:
                if data_packet.ip_src not in ip_list:
                    ip_list.append(data_packet.ip_src)
                if data_packet.ip_dst not in ip_list:
                    ip_list.append(data_packet.ip_dst)
        ip_amount = len(ip_list)
        assert not math.isnan(ip_amount), "ip_amount est NaN"
        return ip_amount

    def calculate_port_amount(self):
        """Calculate the number of unique ports."""
        port_list = []
        for data_packet in self.capture_list:
            if data_packet.port_src is not None and data_packet.port_dst is not None:
                if data_packet.port_src not in port_list:
                    port_list.append(data_packet.port_src)
                if data_packet.port_dst not in port_list:
                    port_list.append(data_packet.port_dst)
        port_amount = len(port_list)
        assert not math.isnan(port_amount), "port_amount est NaN"
        return port_amount

    def calculate_bitrate(self):
        """Calculate the bitrate based on packet sizes and capture duration."""
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
        if total_time <= 0:
            total_time = -total_time
        return total_size / total_time if total_time != 0 else 0

    def calculate_total_time(self):
        """Calculate the total time of packet capture sample."""
        first_time = self.capture_list[0].time
        last_time = self.capture_list[-1].time
        times = [first_time, last_time]
        time_objs = []
        for timers in times:
            time_objs.append(datetime.strptime(str(timers), "%H:%M:%S:%f"))
        times.clear()
        for time_obj in time_objs:
            times.append(time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6)
        total_time = times[-1] - times[0]
        return total_time


class DataCapture:
    """
    Class to manage a list of captured packets.
    """
    def __init__(self, list_of_data_packet=None):
        self.is_processed = False
        if list_of_data_packet is None:
            self.capture_list = []
        else:
            self.capture_list = list_of_data_packet

        self.stats = Statistics(self.capture_list)
        self.size = len(self.capture_list)
        self.ip_mapping = {}

    def __iter__(self):
        return iter(self.capture_list)

    def __len__(self):
        return len(self.capture_list)

    def __repr__(self):
        return f"{self.capture_list}"

    def __str__(self):
        return str("DataCapture<"+str(self.capture_list)+">")

    def add_packet(self, data_packet):
        """Add a DataPacket object to the capture list."""
        try:
            if isinstance(data_packet, DataPacket):
                self.capture_list.append(data_packet)
                self.size = len(self.capture_list)
            else:
                raise TypeError
        except TypeError:
            logging.error(f'Object of type {type(data_packet).__name__} is not of type DataPacket')

    def get_packet(self, index):
        """Retrieve a packet at a specific index."""
        return self.capture_list[index]

    def show(self, index=None):
        """Show the details of packets or statistics."""
        if index is None:
            for data_packet in self.capture_list:
                print("\033[94mPACKET N°"+str(self.capture_list.index(data_packet))+" :")
                data_packet.show()
            self.show_stats()

        else:
            print("\033[94mPACKET N°" + str(index) + " :")
            self.capture_list[index].show()

    def print_field(self, field_name, field_value):
        """Print field with color formatting for presence or absence of data."""
        present_color = '\033[94m'
        none_color = '\033[91m'
        reset_color = '\033[0m'
        if field_value is not None:
            print(f"{present_color}{field_name} : {reset_color}{field_value}")
        else:
            print(f"{none_color}{field_name} : X")

    def show_stats(self):
        """Display statistics for the captured data."""
        fields = [
            ("BITRATE (Bps)", self.stats.bitrate),
            ("AMOUNT OF IP", self.stats.ip_amount),
            ("AMOUNT OF PORT", self.stats.port_amount),
            ("TOTAL TIME", self.stats.total_time)
        ]
        print("\033[94mSTATISTICS : ")
        print("\033[94m---------------------------------------------------")
        for field_name, field_value in fields:
            self.print_field(field_name, field_value)
        print("\033[94m---------------------------------------------------\033[0m")
        print()

    def randomize_ips(self):
        """Anonymize the IP addresses by randomizing the last three octets."""
        def generate_anonymized_ip(ip):
            ip_parts = ip.split('.')
            first_octet = ip_parts[0]
            return f"{first_octet}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

        for packet in self.capture_list:
            if packet.ip_src:
                if packet.ip_src not in self.ip_mapping:
                    self.ip_mapping[packet.ip_src] = generate_anonymized_ip(packet.ip_src)
                packet.ip_src = self.ip_mapping[packet.ip_src]

            if packet.ip_dst:
                if packet.ip_dst not in self.ip_mapping:
                    self.ip_mapping[packet.ip_dst] = generate_anonymized_ip(packet.ip_dst)
                packet.ip_dst = self.ip_mapping[packet.ip_dst]


class DataPacket:
    """
    Class representing a network data packet with its various attributes.
    """
    def __init__(self, type=None, protocol=None, length=None, data=None, ip_src=None, ip_dst=None, p_src=None,
                 p_dst=None, ack=None, flags=None, timestamp=None):
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
        return "DataPacket< type : " + str(self.type) + " | " + str(self.length) + " bytes >"

    def print_field(self, field_name, field_value):
        """Print a specific field of the packet."""
        present_color = '\033[94m'
        none_color = '\033[91m'
        reset_color = '\033[0m'
        if field_value is not None:
            print(f"{present_color}{field_name} : {reset_color}{field_value}")
        else:
            print(f"{none_color}{field_name} : X")

    def show(self):
        """Display details of the packet."""
        present_color = '\033[94m'
        reset_color = '\033[0m'
        fields = [
            ("TYPE", self.type),
            ("TIME (h:m:s:f)", self.time),
            ("LENGTH", self.length),
            ("PROTOCOL", self.protocol),
            ("ACK", self.ack),
            ("FLAGS", self.flags),
            ("IP SOURCE", self.ip_src),
            ("IP DESTINATION", self.ip_dst),
            ("PORT SRC", self.port_src),
            ("PORT DST", self.port_dst),
            ("DATA", self.data)
        ]
        print(present_color + "---------------------------------------------------")
        for field_name, field_value in fields:
            self.print_field(field_name, field_value)
        print(present_color + "---------------------------------------------------" + reset_color)
        print("")


class DataExtractor:
    """
    Class to extract data packets from a PCAP file and create DataPacket objects.
    """
    def __init__(self, raw_capture=None):
        if raw_capture is not None:
            try:
                cap_path = os.path.join(data_path, raw_capture)
                logging.info("capture found at " + cap_path + ". This may take a while to load it...")
            except:
                try:
                    cap_path = raw_capture
                    logging.info("capture found at " + cap_path+". This may take a while to load it...")
                except:
                    logging.error("capture could not be found")
                    exit(1)
            if raw_capture.split('.')[-1] in ['pcap', 'pcapng']:
                try:
                    self.raw_capture = rdpcap(cap_path)
                    logging.info(f"{cap_path} loaded successfully !")
                except Exception as e:
                    logging.error("capture could not be loaded")
                    exit(1)
            else:
                logging.error('Capture must be pcap or pcapng file.')
                exit(1)
        else:
            logging.warning("no file loaded, this extractor is for production")

    @staticmethod
    def make_packet_obj(simple_packet, nbr):
        """Create a DataPacket object from a raw packet."""
        if Ether in simple_packet:
            type = simple_packet[Ether].type
        else:
            type = None
        length = len(simple_packet)
        data = None
        ip_src = None
        ip_dst = None
        protocol = None
        p_src = None
        p_dst = None
        ack = None
        flags = None
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
        return DataPacket(type=type, length=length, data=data, ip_src=ip_src, ip_dst=ip_dst, protocol=protocol,
                          p_src=p_src, p_dst=p_dst, ack=ack, flags=flags, timestamp=timestamp)

    def extract_data(self, split_capture=None):
        """Extract data from a raw capture (PCAP or a split PCAP) and return a DataCapture object."""
        data_capture = DataCapture()
        if split_capture is None:
            for packet in self.raw_capture:
                data_capture.add_packet(self.make_packet_obj(packet, data_capture.size))
        else:
            for packet in split_capture:
                data_capture.add_packet(self.make_packet_obj(packet, data_capture.size))
        return data_capture

    def split_raw_capture(self, packet_by_capture, max_nbr_of_samples=None):
        """Split the raw capture into smaller sets of packets."""
        logging.info("Split capture in samples of " + str(packet_by_capture) + " packets...")
        split_cap = []
        packets = []
        total_packets = len(self.raw_capture)

        max_samples_to_process = min(total_packets // packet_by_capture,
                                     max_nbr_of_samples) if max_nbr_of_samples else total_packets // packet_by_capture

        for i, packet in enumerate(self.raw_capture):
            packets.append(packet)
            if len(packets) >= packet_by_capture:
                split_cap.append(packets)
                packets = []

                progress = len(split_cap) / max_samples_to_process * 100
                bar = "█" * (int(progress) // 2)
                print(
                    f"\rSamples extracted: {bar.ljust(50)} {int(progress)}% [{len(split_cap)}/{max_samples_to_process}]",
                    end='')

                if max_nbr_of_samples is not None and len(split_cap) >= max_nbr_of_samples:
                    break

        if len(packets) > 0:
            split_cap.append(packets)

        print("")
        logging.info(f"Capture split successfully into {len(split_cap)} part(s) with {packet_by_capture} packets each!")
        return split_cap
