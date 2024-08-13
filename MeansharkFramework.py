import customtkinter as ctk
import tkinter as tk
from ui import customMenu
import scapy.all as scapy
import torch
import threading
from neural_network.model import MeanSharkNet
import psutil
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
        self.model.load_state_dict(torch.load(os.path.join(os.getcwd(), "neural_network/model.pt"), weights_only=True))
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
        self.sample_index = 0
        self.model_manager = model_manager
        self.listbox = listbox
        self.lock = threading.Lock()

    def process_current_sample(self):
        if len(self.current_sample) >= 200:
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

            # Cannot use itemconfig with customtkinter; need alternative visual cue
            if result == 1:
                self.listbox.itemconfig(self.sample_index, {'bg': '#825428', 'fg': 'white'})  # Needs alternative
            else:
                self.listbox.itemconfig(self.sample_index, {'bg': '#252526', 'fg': 'white'})  # Needs alternative

            self.current_sample = []
            self.sample_index += 1

    def packet_thread(self, packet):
        with self.lock:
            self.packet_list.append(packet)
            self.current_sample.append(packet)
            self.process_current_sample()


class MeanSharkFramework:
    def __init__(self, root):
        self.root = root
        self.model_manager = ModelManager(input_size=46, hidden_size=70, output_size=2)
        self.side_frame = ctk.CTkFrame(self.root)
        self.upper_side_frame = ctk.CTkFrame(self.side_frame)
        self.packet_manager = PacketManager(self.model_manager, self.create_listbox())
        self.start_packet_capture()

    def thread_gui(self):
        last_sample_selected = None
        last_packet_selected = None
        while True:
            sample_selected, packet_selected = self.get_elements_selected()
            if last_sample_selected != sample_selected:
                self.draw_info_sample(sample_selected)
            if sample_selected is not None and packet_selected != last_packet_selected:
                self.draw_info_packet(sample_selected, packet_selected)
            last_sample_selected = sample_selected
            last_packet_selected = packet_selected

    def get_elements_selected(self):
        sample_selected = self.packet_manager.listbox.curselection()
        packet_selected = None
        if sample_selected:
            sample_selected = sample_selected[0]  # Prend le premier élément du tuple
            packet_selected = self.packet_list.curselection()
            if packet_selected:
                packet_selected = packet_selected[0]  # Prend le premier élément du tuple
        return sample_selected, packet_selected

    def draw_info_sample(self, sample_index):
        if sample_index is not None:
            self.packet_list.delete(0, tk.END)
            try:
                for i in range(200):
                    packet = self.packet_manager.packet_list[200 * sample_index + i]
                    self.packet_list.insert(i, packet.summary())
                    self.packet_list.itemconfig(i, {'bg': '#252526', 'fg': 'white'})
            except Exception as e:
                print(e)

    def draw_info_packet(self, sample_index, packet_index):
        if sample_index is None or packet_index is None:
            return
        try:
            if isinstance(packet_index, int):
                packet = self.packet_manager.packet_list[200 * sample_index + packet_index]
                self.info.configure(state="normal")
                self.info.delete(1.0, tk.END)
                self.info.insert(tk.END, packet.show(dump=True))
                self.info.configure(state="disabled")
            else:
                print(f"Invalid packet_index: {packet_index}, Type: {type(packet_index)}")
        except Exception as e:
            print(e)

    # Les autres fonctions de la classe restent inchangées...



    def start(self):
        self.GUI_thread = threading.Thread(target=self.thread_gui, daemon=True)
        self.GUI_thread.start()
        self.root.mainloop()

    def define_elements(self):
        self.menu = customMenu.Menu(root)
        file_menu = self.menu.menu_bar(text=" File ", tearoff=0, relief="flat")
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        tools_menu = self.menu.menu_bar(text=" Tools ", tearoff=0, relief="flat")
        tools_menu.add_command(label="New")
        tools_menu.add_command(label="Open")
        self.root.config(menu=self.menu)
        self.header_frame = ctk.CTkFrame(self.root)
        self.header_frame.pack(side=ctk.TOP, fill="both", padx=10, pady=10)
        self.interface = []
        for a in psutil.net_if_addrs():
            self.interface.append(a)
        self.interface_selector = ctk.CTkOptionMenu(master=self.header_frame, values=self.interface,
                                                    dropdown_font=("Roboto", 14), font=("Roboto", 14))
        self.interface_selector.pack(side="left", padx=10, pady=10)

        self.center_frame = ctk.CTkFrame(self.header_frame)
        self.center_frame.pack(side="left", expand=True)

        self.label_center_frame = ctk.CTkLabel(master=self.center_frame, text="Network health:", font=("Roboto", 16))
        self.label_center_frame.pack(side="left", padx=10, pady=10)

        self.network_health = ctk.CTkProgressBar(self.center_frame, width=self.root.winfo_screenwidth() / 3, height=20)
        self.network_health.pack(side="left", padx=10, pady=10, expand=True)

        self.health_percentage = ctk.CTkLabel(master=self.center_frame,
                                              text=str(self.network_health.get() * 100) + "%", font=("Roboto", 16))
        self.health_percentage.pack(side="left", padx=10, pady=10, expand=True)
        self.launch_switch = ctk.CTkSwitch(master=self.header_frame, text="Live capture", font=("Roboto", 16))
        self.launch_switch.pack(side="right", padx=10, pady=10)

        self.packets_frame = ctk.CTkFrame(self.root)
        self.packet_list = tk.Listbox(self.packets_frame, bg="#252526", relief="flat", selectmode=tk.SINGLE)
        self.packet_list.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.upper_side_frame, command=self.listbox.yview)
        self.scrollbar.pack(side="left", fill="y", padx=5, pady=5)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.packets_frame.pack(side="right", fill="both", padx=10, pady=10, expand=True)

        self.side_frame.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        self.upper_side_frame.pack(side="top", fill="both", padx=10, pady=10, expand=True)

        self.info = ctk.CTkTextbox(master=self.upper_side_frame)
        self.info.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        self.terminal = ctk.CTkTextbox(master=self.side_frame)
        self.terminal.pack(fill="both", padx=10, pady=10, expand=True)

    def create_listbox(self):
        self.listbox = tk.Listbox(self.upper_side_frame, bg="#252526", relief="flat", selectmode=tk.SINGLE)
        self.listbox.pack(side="left", fill="both", padx=10, pady=10, expand=True)
        return self.listbox

    def start_packet_capture(self):
        thread_sniff = threading.Thread(target=scapy.sniff,
                                        kwargs={"prn": self.packet_manager.packet_thread, "iface": 'Wi-Fi'},
                                        daemon=True)
        thread_sniff.start()


if __name__ == "__main__":
    app = MeanSharkFramework(root)
    app.define_elements()
    app.start()
