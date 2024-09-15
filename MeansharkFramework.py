import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from ui import customMenu
import scapy.all as scapy
import torch
import threading
from neural_network.model import MeanSharkNet
import psutil
import shodan
import json
import os
from neural_network.processing import Processor
from neural_network.extracting import DataExtractor
from neural_network.utils import Information

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("1080x720")
root.title("MeanShark")


class ModelManager:
    """
    Manages the MeanSharkNet model: loading the model, making predictions.
    """
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = MeanSharkNet(self.input_size, self.hidden_size, self.output_size,10).to(self.device)
        self.model.load_state_dict(torch.load(os.path.join(os.getcwd(), "neural_network/model.pt"), weights_only=True))
        self.model.eval()

    def predict(self, sample, x_stats):
        """Predicts the class of a sample using the loaded model."""
        with torch.no_grad():
            sample_tensor = sample.clone().detach().requires_grad_(True)
            x_stats_tensor = x_stats.clone().detach().requires_grad_(True)
            prediction = self.model(sample_tensor, x_stats_tensor)
            return prediction.argmax().item()


class PacketManager:
    """
    Handles packet processing and maintains the list of packets and samples.
    """
    def __init__(self, model_manager, listbox, framework):
        self.framework = framework
        self.packet_list = []
        self.current_sample = []
        self.sample_index = 0
        self.model_manager = model_manager
        self.listbox = listbox
        self.lock = threading.Lock()
        self.network_health = 1.0
        self.is_enabled = True
        self.nbr_of_malicious_sample = 0

    def process_current_sample(self):
        """
        Processes the current sample to extract features and make predictions.
        Updates the listbox and network health display.
        """
        if len(self.current_sample) >= 200:
            extractor = DataExtractor()
            features = extractor.extract_data(self.current_sample)
            processor = Processor(features)

            x_features = processor.output.to_array()
            x_stats = [processor.output.bitrate_normalized, processor.output.ip_amount_normalized,
                       processor.output.port_amount_normalized, processor.output.total_time_normalized]

            sample_tensor = torch.tensor(x_features, dtype=torch.float32).unsqueeze(0).to(self.model_manager.device)
            x_stats_tensor = torch.tensor(x_stats, dtype=torch.float32).unsqueeze(0).to(self.model_manager.device)

            result = self.model_manager.predict(sample_tensor, x_stats_tensor)

            self.listbox.insert(self.sample_index, f"Sample {self.sample_index + 1}")

            if result == 1:
                self.listbox.itemconfig(self.sample_index, {'bg': '#825428', 'fg': 'white'})
                self.nbr_of_malicious_sample += 1
            else:
                self.listbox.itemconfig(self.sample_index, {'bg': '#252526', 'fg': 'white'})

            self.network_health = 1 - (self.nbr_of_malicious_sample / (self.sample_index + 1))
            self.framework.network_health.set(self.network_health)
            self.framework.health_percentage.configure(text=str(round(self.framework.network_health.get() * 100,1)) + "%")

            self.current_sample = []
            self.sample_index += 1

    def reset(self):
        """Resets the packet list and current sample index."""
        self.packet_list.clear()
        self.current_sample.clear()
        self.sample_index = 0

    def packet_thread(self, packet):
        """thread that handles the incoming packets and append them to the list and processes them."""
        with self.lock:
            if self.is_enabled:
                self.packet_list.append(packet)
                self.current_sample.append(packet)
                self.process_current_sample()



class MeanSharkFramework:
    """
    The main application framework for managing the GUI, packet capture, and interactions.
    """
    def __init__(self, root):
        self.information = Information()
        self.API_KEY = os.getenv('SHODAN_API_KEY')
        print(self.API_KEY)
        if self.API_KEY is None:
            raise ValueError("the environment variable SHODAN_API_KEY is not set.")

        self.shodan_api = shodan.Shodan(self.API_KEY)
        self.root = root
        self.model_manager = ModelManager(input_size=46, hidden_size=70, output_size=2)
        self.side_frame = ctk.CTkFrame(self.root)
        self.upper_side_frame = ctk.CTkFrame(self.side_frame)
        self.packet_manager = PacketManager(self.model_manager, self.create_listbox(),self)
        self.last_sample_selected = None
        self.sample_selected = None
        self.last_packet_selected = None
        self.packet_selected = None
        self.interfaces = []
        for a in psutil.net_if_addrs():
            self.interfaces.append(a)
        self.interface_selected = self.interfaces[0]
        self.start_packet_capture()


    def save_capture(self):
        """Saves the current packet capture to a file."""
        file_destination = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".pcap",
                                                 filetypes=[("PCAPNG files", "*.pcapng"),("PCAP files", "*.pcap"),
                                                            ("All files", "*.*")], title="Save Capture as pcap")
        if file_destination:
            scapy.wrpcap(file_destination, self.packet_manager.packet_list)
            print(f"Packets saved to {file_destination}")
        else:
            print("No file selected. The capture was not saved.")

    def save_sample(self):
        """Saves the selected sample of packets to a file."""
        if self.sample_selected is None:
            print("No sample selected. Please select a sample first.")
            return

        file_destination = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension=".pcap",
                                                        filetypes=[("PCAPNG files", "*.pcapng"),
                                                                   ("PCAP files", "*.pcap"),
                                                                   ("All files", "*.*")], title="Save Capture as pcap")
        if file_destination:
            start_index = self.sample_selected * 200
            end_index = start_index + 200
            scapy.wrpcap(file_destination, self.packet_manager.packet_list[start_index:end_index])
            print(f"Sample saved to {file_destination}")
        else:
            print("No file selected. The capture was not saved.")

    def on_listbox_click(self, event):
        """Handles click events on the sample listbox to display selected sample's packets."""
        selection = self.listbox.curselection()
        if selection:
            self.sample_selected = selection[0]
            print(type(self.sample_selected))
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
        """Handles click events on the packet listbox to display details of the selected packet."""
        selection = self.packet_list.curselection()
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

    def on_launch_switch(self,event):
        """Toggles live capture on or off based on the switch state."""
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
        """Starts the main GUI event loop."""
        self.root.after(100, lambda: self.terminal_input.focus())
        self.root.mainloop()

    def post_mortem_analyze(self,event):
        """Post-Mortem analysis of a PCAP file"""
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a PCAP file",
                                               filetypes=[("PCAPNG files", "*.pcapng"), ("PCAP files", "*.pcap"),
                                                          ("All files", "*.*")])

        if file_path:
            print(f"Loading file: {file_path}")
            packets = scapy.rdpcap(file_path)
            self.packet_manager.reset()
            self.listbox.delete(0, tk.END)
            self.packet_list.delete(0, tk.END)
            self.packet_selected = None
            self.last_packet_selected = None
            self.sample_selected = None
            self.last_sample_selected = None
            self.packet_manager.is_enabled = True
            self.info.configure(state=tk.NORMAL)
            self.info.delete(1.0, tk.END)
            self.info.configure(state=tk.DISABLED)
            self.launch_switch.deselect()
            self.interface_selector.configure(state=tk.NORMAL)

            for packet in packets:
                self.packet_manager.packet_thread(packet)

            print("Post-Mortem analysis complete.")
        else:
            print("No file selected. Post-mortem analysis aborted.")

    def execute_command(self,event):
        """Executes terminal commands entered by the user."""
        command = self.terminal_input.get().strip()
        command_parser = command.split(" ")
        self.terminal_input.delete(0, tk.END)

        self.append_output(f"> {command}\n")

        if command_parser[0] == "help":
            output = """
            Available commands: 
                help
                clear
                info
                shodan arg1 arg2
                    arg1 = command (info, host, scan)
                    arg2 = query
                exit
            """
        elif command_parser[0] == "clear":
            self.terminal_output.configure(state=tk.NORMAL)
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.configure(state=tk.DISABLED)
            return
        elif command_parser[0] == "shodan":
            if len(command_parser) < 2:
                output = "Invalid shodan command"
            else:
                shodan_command = command_parser[1]
                if shodan_command == "info":
                    output = json.dumps(self.shodan_api.info(),indent=4)
                elif shodan_command == "host":
                    try:
                        shodan_results = self.shodan_api.host(command_parser[2])
                        shodan_results = json.dumps(shodan_results, indent=4)
                        output = "Shodan results: \n" + str(shodan_results)
                    except Exception as e:
                        output = "Shodan error: " + str(e)
                elif shodan_command == "scan":
                    try:
                        shodan_results = self.shodan_api.scan(command_parser[2])
                        shodan_results = json.dumps(shodan_results, indent=4)
                        output = "Shodan results: \n" + str(shodan_results)
                    except Exception as e:
                        output = "Shodan error: " + str(e)
        elif command_parser[0] == "info":
            output = ("MeanShark Framework - version : " + self.information.info['version'] + " released on " +
                      self.information.info['release_date'] + " - Developped by SupMateo : "
                                                              "https://github.com/SupMateo/MeanShark")
        elif command_parser[0] == "exit":
            self.root.quit()
            return
        else:
            output = f"Command not recognized: {command}"
        self.append_output(f"{output}\n")

    def show_about(self):
        """Displays an 'About' window with information."""
        about = ctk.CTkToplevel()
        about.title("About")
        about.geometry("600x100")
        about.wm_attributes("-topmost", True)

        label_info = ctk.CTkLabel(about, text="MeanShark Framework \n version : " + self.information.info['version'] + " \n released on " +
                      self.information.info['release_date'] + " \n Developped by SupMateo : "
                                                              "https://github.com/SupMateo/MeanShark" + "\n License : GPL 2.0")
        label_info.pack(pady=20)

    def define_elements(self):
        """Defines and initializes GUI elements and layout."""
        self.menu = customMenu.Menu(root)
        file_menu = self.menu.menu_bar(text=" File ", tearoff=0, relief="flat")
        file_menu.add_command(label="Save capture", command=self.save_capture)
        file_menu.add_command(label="Save sample", command=self.save_sample)
        file_menu.add_separator()
        file_menu.add_command(label="Post-Mortem Analysis", command=self.post_mortem_analyze)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        about_menu = self.menu.menu_bar(text="About", tearoff=0, relief="flat")
        about_menu.add_command(label="Show About", command=self.show_about)
        self.root.config(menu=self.menu)

        self.header_frame = ctk.CTkFrame(self.root)
        self.header_frame.pack(side=ctk.TOP, fill="both", padx=10, pady=10)

        self.interface_selector = ctk.CTkOptionMenu(master=self.header_frame, values=self.interfaces,
                                                    dropdown_font=("Roboto", 14), font=("Roboto", 14),
                                                    state=tk.DISABLED)
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

        self.launch_switch = ctk.CTkSwitch(master=self.header_frame, text="Live capture", font=("Roboto", 16),
                                           command=self.on_launch_switch)

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

        self.terminal_output = ctk.CTkTextbox(master=self.side_frame,font=("Consolas", 14))
        self.terminal_output.pack(fill="both", padx=10, pady=5, expand=True)
        self.terminal_output.configure(state=tk.DISABLED)

        self.terminal_input = ctk.CTkEntry(master=self.side_frame,font=("Consolas", 14))
        self.terminal_input.pack(fill="x", padx=10, pady=5)
        self.terminal_input.bind("<Return>", self.execute_command)
        self.append_output("█▀▄▀█ ▄███▄     ██    ▄      ▄▄▄▄▄    ▄  █ ██   █▄▄▄▄ █  █▀\n")
        self.append_output("█ █ █ █▀   ▀   █ █     █    █     ▀▄ █   █ █ █  █  ▄▀ █▄█\n")
        self.append_output("█ ▀ █ ██▄▄    █▄▄█ ██   █ ▄  ▀▀▀▀▄   ██▀▀█ █▄▄█ █▀▀▌  █▀▄\n")
        self.append_output("█   █ █▄   ▄▀ █  █ █ █  █  ▀▄▄▄▄▀    █   █ █  █ █  █  █  █\n")
        self.append_output(" █     ▀███▀  █    █  █ █  ▄▄           █     █   █     █\n")
        self.append_output("  ▀            █   █   ██  █ ▀▄        ▀     █   ▀     ▀\n")
        self.append_output("                ▀          █   ▀▄           ▀\n")
        self.append_output("▄▄▄▄▄▄▄▀▀▀▄▄▄▄▄▄▄▄▄▀▀▄▄▄▀▀ █     ▀▄ ▀▀▄▄▄▄▀▀▄▄▄▄▄▄▄▀▀▀▄▄▄▄▄\n")
        self.append_output("                     ▄    ▄         ▄    ▄\n")
        self.append_output("                     ▀      ▀▀  ▀▀▀      ▀ \n")
        self.append_output("                        ▀   ▄▄▄  ▄    ▀ \n")
        self.append_output("\n")
        self.append_output("                          Framework                        \n")
        self.append_output("\n")
        self.append_output("    Developped by SupMateo on GitHub\n")
        self.append_output("    https://github.com/SupMateo/MeanShark\n")
        self.append_output("    Version {version}, {release_date}\n".format(version=self.information.info['version'],release_date=self.information.info['release_date']))
        self.append_output("▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄")
        self.append_output("\n")
        self.append_output("\n")
        self.append_output("MeanShark Framework Terminal (type 'help' for available commands)\n")
        self.terminal_input.focus()

    def append_output(self, text):
        """Appends the output to the terminal."""
        self.terminal_output.configure(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.configure(state=tk.DISABLED)
        self.terminal_output.see(tk.END)

    def create_listbox(self):
        """Creates and configures the sample listbox."""
        self.listbox = tk.Listbox(self.upper_side_frame, bg="#252526", relief="flat", selectmode=tk.SINGLE)
        self.listbox.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_click)

        return self.listbox

    def create_packet_listbox(self):
        """Creates and configures the packet listbox."""
        self.packet_list = tk.Listbox(self.packets_frame, bg="#252526", relief="flat", selectmode=tk.SINGLE)
        self.packet_list.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        print("packet list initialized")
        self.packet_list.bind("<ButtonRelease-1>", self.on_packet_listbox_click)

        return self.packet_list

    def start_packet_capture(self):
        """Starts packet capture in a separate thread."""
        self.thread_sniff = threading.Thread(target=scapy.sniff,
                                        kwargs={"prn": self.packet_manager.packet_thread, "iface": str(self.interface_selected)},
                                        daemon=True)
        self.thread_sniff.start()


if __name__ == "__main__":
    app = MeanSharkFramework(root)
    app.define_elements()
    app.start()
