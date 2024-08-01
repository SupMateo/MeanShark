import os
import utils
import json
import logging
from extracting import DataExtractor
from processing import Processor
import numpy as np
from sklearn.model_selection import train_test_split


class MeanSharkDataset:
    def __init__(self, features=None, stats=None, labels=None):
        if features is not None and stats is not None and labels is not None:
            self.features = np.array(features, dtype=np.float32)
            self.stats = np.array(stats, dtype=np.float32)
            self.labels = np.array(labels, dtype=np.int64)
        else:
            self.load_dataset_from_json()

        if self.features is None or self.stats is None or self.labels is None:
            raise ValueError("Features, stats, or labels are None after initialization or loading from JSON")

        combined_features = np.concatenate((self.features.reshape(self.features.shape[0], -1), self.stats), axis=1)
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            combined_features, self.labels, test_size=0.2, random_state=42
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=0.25, random_state=42
        )

        logging.info(f"Training set size: {X_train.shape[0]}")
        logging.info(f"Validation set size: {X_val.shape[0]}")
        logging.info(f"Test set size: {X_test.shape[0]}")

        self.training_set = X_train
        self.validation_set = X_val
        self.testing_set = X_test

    def load_dataset_from_json(self):
        try:
            with open("raw_dataset.json", 'r') as f:
                data_loaded = json.load(f)
        except FileNotFoundError:
            logging.error("raw_dataset.json not found. Try to make it")
            exit(1)

        self.features = np.array(data_loaded.get('dataset'), dtype=np.float32)
        self.stats = np.array(data_loaded.get('stats'), dtype=np.float32)
        self.labels = np.array(data_loaded.get('labels'), dtype=np.int64)

        if self.features is None or self.stats is None or self.labels is None:
            logging.error("Failed to load features, stats, or labels from JSON.")
            exit(1)

        logging.info("Raw dataset loaded successfully!")

    def save_dataset_to_json(self):
        data_to_save = {
            'dataset': self.features.tolist(),
            'stats': self.stats.tolist(),
            'labels': self.labels.tolist()
        }

        with open("raw_dataset.json", 'w') as f:
            json.dump(data_to_save, f, indent=4)

        logging.info("Raw data saved")


class DatasetMaker:
    def __init__(self, path_malicious, path_normal):
        if os.path.isdir(path_malicious) and os.path.isdir(path_normal):
            self.path_malicious = path_malicious
            self.path_normal = path_normal
        else:
            try:
                path_datasets = os.path.join(os.getcwd(), "Datasets")
                self.path_malicious = os.path.join(path_datasets, path_malicious)
                self.path_normal = os.path.join(path_datasets, path_normal)
            except:
                logging.error('Paths does not exist')
                exit(1)


    @property
    def output(self):
        return self.make()

    def make(self):
        features, stats, labels = self.build_raw_dataset()
        return MeanSharkDataset(features, stats, labels)

    def build_raw_dataset(self):
        raw_dataset = []
        raw_stats = []
        raw_labels = []
        malicious_capture = os.listdir(self.path_malicious)
        normal_capture = os.listdir(self.path_normal)
        capture_in_raw_dataset = 0
        nbr_of_samples = 400
        for capture in malicious_capture:
            if capture.split('.')[-1] in ['pcap', 'pcapng']:
                print()
                logging.info(f'Adding {capture} (MALICIOUS) data to the raw dataset...')
                extractor = DataExtractor(os.path.join(self.path_malicious, capture))
                samples = extractor.split_raw_capture(200, max=nbr_of_samples)

                for sample in samples:
                    data_sample = extractor.extract_data(split_capture=sample)
                    processor = Processor(data_sample)
                    processed_sample = processor.output
                    stats = processed_sample.stats
                    sample_array = processed_sample.to_array()
                    raw_dataset.append(sample_array)
                    sample_stats = [stats.bitrate_normalized, stats.ip_amount_normalized, stats.port_amount_normalized]
                    raw_stats.append(sample_stats)
                    raw_labels.append(1)
                    print("\rsamples processed : " + "█" * int(
                        ((len(raw_labels)-nbr_of_samples*capture_in_raw_dataset) / len(samples)) * 100) + " " +
                          f"{int(((len(raw_labels)) / len(samples)) * 100)}% [" +
                          f"{int(len(raw_labels)-nbr_of_samples*capture_in_raw_dataset)}/" +
                          f"{len(samples)}" + "]", end='')
                print("")
                capture_in_raw_dataset += 1
            else:
                logging.info(f'{capture} is not a pcap or pcapng file. This file is ignored')

        for capture in normal_capture:
            if capture.split('.')[-1] in ['pcap', 'pcapng']:
                print()
                logging.info(f'Adding {capture} (NORMAL) data to our raw dataset...')
                extractor = DataExtractor(os.path.join(self.path_normal, capture))
                samples = extractor.split_raw_capture(200, max=nbr_of_samples)

                for sample in samples:
                    data_sample = extractor.extract_data(split_capture=sample)
                    processor = Processor(data_sample)
                    processed_sample = processor.output
                    stats = processed_sample.stats
                    sample_array = processed_sample.to_array()
                    raw_dataset.append(sample_array)
                    sample_stats = [stats.bitrate_normalized, stats.ip_amount_normalized, stats.port_amount_normalized]
                    raw_stats.append(sample_stats)
                    raw_labels.append(0)
                    print("\rsamples processed : " + "█" * int(
                        ((len(raw_labels) - nbr_of_samples * capture_in_raw_dataset) / len(samples)) * 100) + " " +
                          f"{int(((len(raw_labels)) / len(samples)) * 100)}% [" +
                          f"{int(len(raw_labels) - nbr_of_samples * capture_in_raw_dataset)}/" +
                          f"{len(samples)}" + "]", end='')
                    print("")
                    capture_in_raw_dataset += 1
            else:
                logging.info(f'{capture} is not a pcap or pcapng file. This file is ignored')

        logging.info("Raw data build successfully")
        return raw_dataset, raw_stats, raw_labels
