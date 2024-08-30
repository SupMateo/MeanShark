import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset,random_split
from model import MeanSharkNet
import logging
import matplotlib.pyplot as plt
import torch.nn as nn
import utils


def init_weights(m):
    if isinstance(m, nn.Linear) or isinstance(m, nn.Conv2d):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.zeros_(m.bias)


class Trainer:
    def __init__(self, mean_shark_dataset):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logging.info('Using device: {}'.format(device))

        features = torch.tensor(mean_shark_dataset.features, dtype=torch.float32).to(device)
        stats = torch.tensor(mean_shark_dataset.stats, dtype=torch.float32).to(device)
        labels = torch.tensor(mean_shark_dataset.labels, dtype=torch.long).to(device)

        self.dataset = TensorDataset(features, stats, labels)
        self.train_size = int(0.7 * len(self.dataset))
        self.val_size = int(0.15 * len(self.dataset))
        self.test_size = len(self.dataset) - self.train_size - self.val_size
        self.train_dataset, self.val_dataset, self.test_dataset = random_split(self.dataset, [self.train_size, self.val_size, self.test_size])
        self.batch_size = 75
        self.input_size = mean_shark_dataset.features.shape[2]
        self.hidden_size = 70
        self.attention_head = 10
        self.output_size = len(np.unique(mean_shark_dataset.labels))
        self.model = MeanSharkNet(self.input_size, self.hidden_size,self.output_size,self.attention_head).to(device)
        self.criterion = torch.nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.00001)
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []

    def train(self, num_epochs=350):
        train_loader = DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=False)
        logging.info("Training start")
        #torch.autograd.set_detect_anomaly(True)

        for epoch in range(num_epochs):

            self.model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            for x_packets, x_stats, y in train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(x_packets, x_stats)
                loss = self.criterion(outputs, y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                for name, param in self.model.named_parameters():
                    if param.grad is not None:
                        if torch.isnan(param.grad).any():
                            print(f"NaN in gradients of {name}")
                        elif torch.isinf(param.grad).any():
                            print(f"Inf in gradients of {name}")
                self.optimizer.step()
                running_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += y.size(0)
                correct += (predicted == y).sum().item()

            self.train_losses.append(running_loss / len(train_loader))
            self.train_accuracies.append(correct / total)
            logging.info(f"Epoch {epoch + 1}, Loss: {running_loss / len(train_loader)}, Accuracy: {correct / total}")

            self.model.eval()
            val_loss = 0.0
            correct = 0
            total = 0
            with torch.no_grad():
                for x_packets, x_stats, y in val_loader:
                    outputs = self.model(x_packets, x_stats)
                    loss = self.criterion(outputs, y)
                    val_loss += loss.item()
                    _, predicted = torch.max(outputs, 1)
                    total += y.size(0)
                    correct += (predicted == y).sum().item()

            self.val_losses.append(val_loss / len(val_loader))
            self.val_accuracies.append(correct / total)
            logging.info(f"Validation Loss: {val_loss / len(val_loader)}, Accuracy: {correct / total}")

        logging.info("training finished")

        epochs = range(1, num_epochs + 1)
        plt.figure()
        plt.plot(epochs, self.train_losses, 'b', label='Training Loss')
        plt.plot(epochs, self.val_losses, 'r', label='Validation Loss')
        plt.title('Training and Validation Losses')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()

        plt.figure()
        plt.plot(epochs, self.train_accuracies, 'b', label='Training Accuracy')
        plt.plot(epochs, self.val_accuracies, 'r', label='Validation Accuracy')
        plt.title('Training and Validation Accuracies')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.show()

    def test(self):
        logging.info("Start testing the model")
        test_loader = DataLoader(self.test_dataset, batch_size=self.batch_size, shuffle=False)
        self.model.eval()
        test_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for x_packets, x_stats, y in test_loader:
                outputs = self.model(x_packets, x_stats)
                loss = self.criterion(outputs, y)
                test_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += y.size(0)
                correct += (predicted == y).sum().item()
                print(f"Test Loss: {test_loss / len(test_loader)}, Accuracy: {correct / total}")
        logging.info("testing the model finished")


    def save_model(self):
        self.model.eval()
        torch.save(self.model.state_dict(), 'model.pt')