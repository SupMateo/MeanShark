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
        self.is_enabled = True

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

    def reset(self):
        self.packet_list.clear()
        self.current_sample.clear()
        self.sample_index = 0

    def packet_thread(self, packet):
        with self.lock:
            if self.is_enabled:
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
        self.last_sample_selected = None
        self.sample_selected = None
        self.last_packet_selected = None
        self.packet_selected = None
        self.interfaces = []
        for a in psutil.net_if_addrs():
            self.interfaces.append(a)
        self.interface_selected = self.interfaces[0]
        self.start_packet_capture()


    def on_listbox_click(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.sample_selected = selection[0]
            if self.sample_selected != self.last_sample_selected:
                self.packet_list.delete(0, tk.END)
                for i in range(200):
                    self.packet_list.insert(i, self.packet_manager.packet_list[200*self.sample_selected + i].summary())
                    self.packet_list.itemconfig(i, {'bg': '#252526', 'fg': 'white'})
                self.last_sample_selected = self.sample_selected
            else:
                pass
            print(f"Sample selected: {self.sample_selected}")

    def on_packet_listbox_click(self, event):
        selection = self.packet_list.curselection()
        print("clicked")
        if selection:
            self.packet_selected = selection[0]
            if self.packet_selected != self.last_packet_selected:
                packet_index = 200 * self.sample_selected + self.packet_selected
                if 0 <= packet_index < len(self.packet_manager.packet_list):
                    packet = self.packet_manager.packet_list[packet_index]
                    packet_info = packet.show(dump=True)
                    self.info.configure(state=tk.NORMAL)
                    self.info.delete(1.0, tk.END)
                    self.info.insert(tk.END, packet_info)
                    self.info.configure(state=tk.DISABLED)
            print(f"Packet selected: {self.packet_selected}")

    def on_launch_switch(self):
        state = self.launch_switch.get()
        if state == 1:
            print("Switch is On")
            self.listbox.delete(0, tk.END)
            self.packet_list.delete(0, tk.END)
            self.packet_manager.reset()
            self.packet_selected = None
            self.last_packet_selected = None
            self.sample_selected = None
            self.last_sample_selected = None
            self.packet_manager.is_enabled = True
            self.info.configure(state=tk.NORMAL)
            self.info.delete(1.0, tk.END)
            self.info.configure(state=tk.DISABLED)
            self.packet_manager.is_enabled = True
            self.interface_selector.configure(state=tk.DISABLED)
            self.interface_selected = str(self.interface_selector.get())
            self.start_packet_capture()
        else:
            print("Switch is Off")
            self.interface_selector.configure(state=tk.NORMAL)
            self.packet_manager.is_enabled = False



    def start(self):
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

        self.interface_selector = ctk.CTkOptionMenu(master=self.header_frame, values=self.interfaces,
                                                    dropdown_font=("Roboto", 14), font=("Roboto", 14), state=tk.DISABLED)
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
        self.launch_switch = ctk.CTkSwitch(master=self.header_frame, text="Live capture", font=("Roboto", 16),command=self.on_launch_switch)
        self.launch_switch.pack(side="right", padx=10, pady=10)
        self.launch_switch.select()

        self.packets_frame = ctk.CTkFrame(self.root)
        self.packet_list = self.create_packet_listbox()
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

        # Bind the listbox click event to the on_listbox_click method
        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_click)

        return self.listbox

    def create_packet_listbox(self):
        self.packet_list = tk.Listbox(self.packets_frame, bg="#252526", relief="flat", selectmode=tk.SINGLE)
        self.packet_list.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        # Bind the packet listbox click event to the on_packet_listbox_click method
        print("packet list initialized")
        self.packet_list.bind("<ButtonRelease-1>", self.on_packet_listbox_click)

        return self.packet_list

    def start_packet_capture(self):
        self.thread_sniff = threading.Thread(target=scapy.sniff,
                                        kwargs={"prn": self.packet_manager.packet_thread, "iface": str(self.interface_selected)},
                                        daemon=True)
        self.thread_sniff.start()


if __name__ == "__main__":
    app = MeanSharkFramework(root)
    app.define_elements()
    app.start()
