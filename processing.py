from extracting import Statistics
import utils
import logging


class ProcessedPacket:

    def __init__(self, data_packet):
        self.type = self.process_type(data_packet.type)
        self.protocol = data_packet.protocol
        self.length = data_packet.length
        self.data = self.process_data(data_packet.data)
        self.ip_src = self.process_ip(data_packet.ip_src)
        self.ip_dst = self.process_ip(data_packet.ip_dst)
        self.port_src = self.process_port(data_packet.port_src)
        self.port_dst = self.process_port(data_packet.port_dst)
        self.ack = self.process_ack(data_packet.ack)
        self.flags = self.process_flags(data_packet.flags)
        #self.time = None
        self.vector = self.vectorize()

    def __repr__(self):
        return f'{self.vector}'

    def __str__(self):
        return f'ProcessedPacket<{self.vector}>'

    def process_data(self, data):
        target_length = 30
        if data is not None:
            try:
                int_list = [ord(char) for char in data.decode()]
            except :
                pass

            try:
                int_list = list(data)
            except:
                pass

            if int_list is None or len(int_list) == 0:
                logging.error("Data encoding failed")
                return -1

            else:
                if len(int_list) > target_length:
                    removed_values = int_list[target_length:]
                    removed_sum = sum(removed_values)

                    int_list = int_list[:target_length]

                    increment = removed_sum // target_length
                    remainder = removed_sum % target_length

                    for i in range(target_length):
                        int_list[i] += increment
                        if i < remainder:
                            int_list[i] += 1

                elif len(int_list) < target_length:
                    int_list.extend([-1] * (target_length - len(int_list)))
            return int_list

        else:
            int_list = []
            for i in range(target_length):
                int_list.append(-1)
            return int_list

    def process_ip(self, ip):
        processed_ip = -1
        if ip is not None:
            if ':' in ip:
                hex_string = ip.replace(':', '')
                processed_ip = int(int(hex_string, 16)/100000)
            else:
                decomposed_ip = ip.split('.')
                for i in range(len(decomposed_ip)):
                    processed_ip += processed_ip + int(decomposed_ip[i])*pow(256, abs(i-3))
        return int(processed_ip/50000)

    def process_port(self, port):
        if port is not None:
            return port
        else:
            return -1

    def process_type(self, type):
        if type is not None:
            return type
        else:
            return -1


    def process_ack(self, ack):
        if ack is not None:
            return ack
        else:
            return -1

    def process_flags(self, flags):
        processed_flags = [-1] * 8
        if flags is not None:
            if 'A' in flags:
                processed_flags[0] = 1
            if 'S' in flags:
                processed_flags[1] = 1
            if 'P' in flags:
                processed_flags[2] = 1
            if 'F' in flags:
                processed_flags[3] = 1
            if 'R' in flags:
                processed_flags[4] = 1
            if 'U' in flags:
                processed_flags[5] = 1
            if 'C' in flags:
                processed_flags[6] = 1
            if 'E' in flags:
                processed_flags[7] = 1
            return processed_flags
        else:
            return processed_flags

    def vectorize(self):
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

    def __init__(self, data_capture):
        self.data_capture = data_capture
        self.processed_packets = []
        for data_packets in self.data_capture:
            self.add_processed_packet(ProcessedPacket(data_packets))
        self.stats = data_capture.stats


    def __iter__(self):
        return iter(self.processed_packets)

    def __len__(self):
        return len(self.processed_packets)

    def __repr__(self):
        return f"{self.processed_packets}"

    def __str__(self):
        return str("ProcessedCapture<" + str(self.processed_packets) + ">")

    def add_processed_packet(self, processed_packet):
        try:
            if isinstance(processed_packet, ProcessedPacket):
                self.processed_packets.append(processed_packet.vector)
            else:
                raise TypeError
        except TypeError:
            logging.error(f'Object of type {type(processed_packet).__name__} is not of type ProcessedPacket')

    def to_array(self):
        return self.processed_packets

class Processor:
    def __init__(self, data_capture):
        self.data_capture = data_capture

    @property
    def output(self):
        return self.process()

    def process(self):
        processed_capture = ProcessedCapture(self.data_capture)
        for data_packet in self.data_capture:
            processed_packet = ProcessedPacket(data_packet)
            processed_capture.add_processed_packet(processed_packet)
        return processed_capture
