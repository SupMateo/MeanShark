import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

class MeanSharkNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(MeanSharkNet, self).__init__()

        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc1 = nn.Linear(hidden_size+3, hidden_size)
        self.relu1 = nn.ReLU()
        self.bn1 = nn.BatchNorm1d(hidden_size)
        self.relu2 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x_packets, x_stats):
        lstm_out, (hn, cn) = self.lstm(x_packets)
        lstm_out = hn[-1]

        combined = torch.cat((lstm_out, x_stats), dim=1)

        out = self.fc1(combined)
        out = self.relu1(out)
        out = self.bn1(out)
        out = self.relu2(out)
        out = self.fc2(out)
        return out
