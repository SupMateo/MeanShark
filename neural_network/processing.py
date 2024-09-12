import logging
import math


class ProcessedPacket:
    """
    Represents a processed network packet with attributes normalized and vectorized for analysis.
    """

    def __init__(self, data_packet):
        # Initialize packet attributes and process various fields (e.g., IPs, ports, flags, etc.)
        self.type = self.process_type(data_packet.type)
        self.protocol = self.process_protocol(data_packet.protocol)
        self.length = data_packet.length
        self.data = self.process_data(data_packet.data)
        self.ip_src = self.process_ip(data_packet.ip_src)
        self.ip_dst = self.process_ip(data_packet.ip_dst)
        self.port_src = self.process_port(data_packet.port_src)
        self.port_dst = self.process_port(data_packet.port_dst)
        self.ack = self.process_ack(data_packet.ack)
        self.flags = self.process_flags(data_packet.flags)
        # Vector representation of the packet for easy access.
        self.vector = self.vectorize()

    def __repr__(self):
        return f'{self.vector}'

    def __str__(self):
        return f'ProcessedPacket<{self.vector}>'

    def process_data(self, data):
        """Normalizes and processes packet data (payload) into a fixed-length vector."""
        target_length = 30
        if data is not None:
            try:
                int_list = [ord(char) for char in data.decode()]
            except:
                int_list = []

            # Converts raw data into integers and normalizes it to target length
            if not int_list:
                try:
                    int_list = list(data)
                except:
                    logging.error("Data conversion failed")
                    return [-1.0] * target_length

            # Normalizes data if too long or short, preserving sum if truncated
            if len(int_list) > target_length:
                removed_values = int_list[target_length:]
                removed_sum = sum(removed_values)
                int_list = int_list[:target_length]
                increment = removed_sum / target_length
                remainder = removed_sum % target_length
                for i in range(target_length):
                    int_list[i] += increment
                    if i < remainder:
                        int_list[i] += 1
            elif len(int_list) < target_length:
                int_list.extend([-1] * (target_length - len(int_list)))

            # Normalize values between 0 and 1
            min_value = min(int_list)
            max_value = max(int_list)
            if max_value > min_value:
                normalized_list = [(x - min_value) / (max_value - min_value) for x in int_list]
            else:
                normalized_list = [0.0] * target_length

            return normalized_list
        else:
            return [-1.0] * target_length

    def process_ip(self, ip):
        """Converts and normalizes an IP address"""
        processed_ip = -1
        if ip is not None:
            if ':' in ip:
                # Handles IPv6 addresses
                hex_string = ip.replace(':', '')
                try:
                    processed_ip = int(hex_string, 16) / (340282366920938463463374607431768211455 * 30)
                except ValueError:
                    processed_ip = 0.5
            else:
                # Handles IPv4 addresses
                decomposed_ip = ip.split('.')
                for i in range(len(decomposed_ip)):
                    processed_ip += float(processed_ip + int(decomposed_ip[i]) * pow(256, abs(i - 3)))
                processed_ip = processed_ip / (4294967295 * 30)
        return processed_ip

    def process_port(self, port):
        """Normalizes a port number to a value between 0 and 1."""
        if port is not None:
            return port / 65535
        else:
            return -1

    def process_type(self, type):
        """Normalizes the type field."""
        if type is not None:
            return type / 65535
        else:
            return -1

    def process_protocol(self, protocol):
        """Normalizes the protocol."""
        if protocol is not None:
            return protocol / 255
        else:
            return -1

    def process_ack(self, ack):
        """Normalizes the acknowledgment number"""
        if ack is not None:
            return ack / 4294967295
        else:
            return -1

    def process_flags(self, flags):
        """Encodes packet flags (TCP/UDP flags) into a binary vector."""
        processed_flags = [-1] * 8
        if flags is not None:
            if 'A' in flags: processed_flags[0] = 1
            if 'S' in flags: processed_flags[1] = 1
            if 'P' in flags: processed_flags[2] = 1
            if 'F' in flags: processed_flags[3] = 1
            if 'R' in flags: processed_flags[4] = 1
            if 'U' in flags: processed_flags[5] = 1
            if 'C' in flags: processed_flags[6] = 1
            if 'E' in flags: processed_flags[7] = 1
        return processed_flags

    def vectorize(self):
        """Combines all processed fields into a vector representation for analysis."""
        vector = []
        vector.append(self.ip_src)
        vector.append(self.ip_dst)
        vector.append(self.length)
        vector.append(self.port_src)
        vector.append(self.port_dst)
        vector.append(self.ack)
        vector.extend(self.flags)
        vector.append(self.type)
        vector.append(self.protocol)
        vector.extend(self.data)
        return vector


class ProcessedCapture:
    """
    Represents a collection of processed network packets for analysis.
    """

    def __init__(self, data_capture):
        # Initialize and process the captured packets.
        self.data_capture = data_capture
        self.processed_packets = []
        for data_packets in self.data_capture:
            self.add_processed_packet(ProcessedPacket(data_packets))

        # Normalized statistics of the capture.
        self.bitrate_normalized = data_capture.stats.bitrate / 100000000
        self.ip_amount_normalized = (data_capture.stats.ip_amount - 2) / (len(data_capture) * 2 - 2)
        self.port_amount_normalized = data_capture.stats.port_amount - 2 / (len(data_capture) * 2 - 2)
        self.total_time_normalized = data_capture.stats.total_time / 60

        # Validate that no NaN values are present in the normalized values.
        assert not math.isnan(self.bitrate_normalized), "bitrate_normalized is NaN"
        assert not math.isnan(self.ip_amount_normalized), "ip_amount_normalized is NaN"
        assert not math.isnan(self.port_amount_normalized), "port_amount_normalized is NaN"
        assert not math.isnan(self.total_time_normalized), "total_time_normalized is NaN"

    def __iter__(self):
        return iter(self.processed_packets)

    def __len__(self):
        return len(self.processed_packets)

    def __repr__(self):
        return f"{self.processed_packets}"

    def __str__(self):
        return str("ProcessedCapture<" + str(self.processed_packets) + ">")

    def add_processed_packet(self, processed_packet):
        """Adds a processed packet to the capture."""
        try:
            if isinstance(processed_packet, ProcessedPacket):
                self.processed_packets.append(processed_packet.vector)
            else:
                raise TypeError
        except TypeError:
            logging.error(f'Object of type {type(processed_packet).__name__} is not of type ProcessedPacket')

    def to_array(self):
        """Converts the processed packets into an array format."""
        return self.processed_packets


class Processor:
    """
    Orchestrates the processing of captured network packets.
    """
    def __init__(self, data_capture):
        """Initialize the processor with the raw data capture."""
        self.data_capture = data_capture

    @property
    def output(self):
        # Property that triggers the packet processing and returns the processed capture.
        return self.process()

    def process(self):
        """Processes the data capture into a ProcessedCapture."""
        processed_capture = ProcessedCapture(self.data_capture)
        for data_packet in self.data_capture:
            processed_packet = ProcessedPacket(data_packet)
            processed_capture.add_processed_packet(processed_packet)
        return processed_capture
