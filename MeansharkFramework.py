import customtkinter as ctk
import tkinter as tk
from ui import customMenu
import scapy.all as scapy
import torch
import threading
from neural_network.model import MeanSharkNet
import numpy as np
import os
from neural_network.processing import Processor
from neural_network.extracting import DataExtractor

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("1080x720")
root.title("MeanShark")


class ModelManager:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = MeanSharkNet(self.input_size, self.hidden_size, self.output_size).to(self.device)
        self.model.load_state_dict(torch.load(os.path.join(os.getcwd(),"neural_network/model.pt"), weights_only=True))
        self.model.eval()

    def predict(self, sample, x_stats):
        with torch.no_grad():
            sample_tensor = torch.tensor(sample, dtype=torch.float32)
            x_stats_tensor = torch.tensor(x_stats, dtype=torch.float32)
            prediction = self.model(sample_tensor, x_stats_tensor)
            return prediction.argmax().item()


class PacketManager:
    def __init__(self, model_manager, listbox):
        self.packet_list = []
        self.current_sample = []
        self.sample_index = 0  # Change initial sample_index to 0
        self.model_manager = model_manager
        self.listbox = listbox
        self.lock = threading.Lock()

    def process_current_sample(self):
        if len(self.current_sample) >= 200:
            print(self.current_sample)
            extractor = DataExtractor()
            features = extractor.extract_data(self.current_sample)
            processor = Processor(features)

            x_features = processor.output.to_array()
            x_stats = [processor.output.bitrate_normalized, processor.output.ip_amount_normalized,
                       processor.output.port_amount_normalized]

            sample_tensor = torch.tensor(x_features, dtype=torch.float32).unsqueeze(0).to(self.model_manager.device)
            x_stats_tensor = torch.tensor(x_stats, dtype=torch.float32).unsqueeze(0).to(self.model_manager.device)

            result = self.model_manager.predict(sample_tensor, x_stats_tensor)

            self.listbox.insert(self.sample_index, f"Sample {self.sample_index + 1}")

            if result == 1:
                self.listbox.itemconfig(self.sample_index, {'bg': '#825428', 'fg': 'white'})
            else:
                self.listbox.itemconfig(self.sample_index, {'bg': '#252526', 'fg': 'white'})

            self.current_sample = []
            self.sample_index += 1

    def packet_thread(self, packet):
        with self.lock:
            print(packet.summary())
            self.packet_list.append(packet)
            self.current_sample.append(packet)
            self.process_current_sample()

class MeanSharkFramework:
    def __init__(self, root):
        self.root = root
        self.model_manager = ModelManager(input_size=46, hidden_size=70, output_size=2)
        self.capture_frame = ctk.CTkFrame(self.root)
        self.packet_manager = PacketManager(self.model_manager, self.create_listbox())
        self.start_packet_capture()

    def nothing(self):
        print("ok")

    def start(self):
        self.root.mainloop()

    def define_elements(self):
        self.menu = customMenu.Menu(root)
        file_menu = self.menu.menu_bar(text=" File ", tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        tools_menu = self.menu.menu_bar(text=" Tools ", tearoff=0)
        tools_menu.add_command(label="New")
        tools_menu.add_command(label="Open")
        self.root.config(menu=self.menu)

        self.capture_frame.pack(side="right", fill="both", padx=10, pady=10, expand=True)
        self.capture_label = ctk.CTkLabel(master=self.capture_frame,text="Capture",font=("Roboto",19))
        self.capture_label.pack(side="top",padx=10, pady=10)

        self.side_frame = ctk.CTkFrame(self.root)
        self.side_frame.pack(side="left", fill="both", padx=10, pady=10, expand=True)

    def create_listbox(self):
        self.listbox = tk.Listbox(self.capture_frame, bg="#252526",relief="flat", selectmode=tk.SINGLE)
        self.listbox.pack(fill="both", padx=10, pady=10, expand=True)
        return self.listbox

    def start_packet_capture(self):
        thread_sniff = threading.Thread(target=scapy.sniff,kwargs={"prn":self.packet_manager.packet_thread, "iface":
            'Wi-Fi'},daemon=True)
        thread_sniff.start()


if __name__ == "__main__":
    app = MeanSharkFramework(root)
    app.define_elements()
    app.start()
