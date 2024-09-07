# MeanShark

MeanShark is an advanced packet sniffing and network analysis tool with integrated machine learning capabilities and OSINT tool, designed to monitor network traffic and detect malicious activities. It features a graphical interface built with [customtkinter](https://github.com/TomSchimansky/CustomTkinter), packet capture and inspection using [Scapy](https://scapy.net/), and a neural network model implemented in PyTorch to classify network traffic.

## Features

- **Live Packet Capture**: Capture network packets in real-time using Scapy.
- **Neural Network for Malicious Traffic Detection**: Analyze traffic with a pre-trained neural network model built using PyTorch to identify malicious packets.
- **Packet Summary and Inspection**: View packet details and save packet captures for offline analysis.
- **Shodan Integration**: Use the [Shodan API](https://www.shodan.io/) to gather intelligence on hosts.
- **Graphical User Interface**: Built with customTkinter for a dark-themed user-friendly experience.
- **Network Health Monitoring**: Live updates on the health of your network based on the percentage of malicious packets detected.
  
## Installation

### Prerequisites

- Python 3.8+
- Wireshark or a similar PCAP reader
- A valid [Shodan API key](https://account.shodan.io/)
- CUDA (optional, for GPU support with PyTorch)

### Required Libraries

Install the required libraries with `pip`:

```bash
pip install -r requirements.txt
```

### Environment Variables
You need to set the environment variable for the Shodan API key:

- On Linux :
  
```bash
export SHODAN_API_KEY="your_shodan_api_key"
```

- On Windows you have to add it in the Environment variables menu

## Usage

### MeanShark Framework
Run the `MeanShark` application using Python:

```bash
python MeansharkFramework.py
```

### MeanShark Training Tool
With the `MeanShark Training Tool` you can add data to the dataset or recreate totally a new dataset. First, you have to classify your PCAP data in the directories `MeanShark/neural_network/Datasets/malicious` and `MeanShark/neural_network/Datasets/normal` (create the folders if they are not present).
Next, you can use the `MeanShark_training_tool` application with the correct arguments :
- -m : Recreate a new dataset.
- -a : Add the pcap files data from the Datasets directory to the dataset.
- -t : Train the model with the dataset.

#### Exemple

```bash
python MeanShark_training_tool.py -a
```

After the data has been added to the dataset, you should train the model with the new dataset :

```bash
python MeanShark_training_tool.py -t
```

## Neural Network Model
The `MeanSharkNet` is a neural network model designed to analyze network traffic data. It implements linear and non linear layers. An auto-attentive layer and an LSTM layer complete the model to make it more efficient and accurate. It takes extracted features from network packets and classifies them as malicious or benign. The model is pre-trained and can be customized.

## Author
Developed by SupMateo: [GitHub](https://github.com/SupMateo/)
