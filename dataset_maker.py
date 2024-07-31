import os
import utils
import logging
from extracting import DataExtractor
from processing import Processor


class MeanSharkDataset():
    def __init__(self):
        self.training_data = None
        self.validation_data = None
        self.testing_data = None


class DatasetMaker:
    def __init__(self, path_malicious, path_normal):
        try:
            self.path_malicious = path_malicious
            self.path_normal = path_normal
        except:
            try:
                self.path_malicious = os.path.join(os.getcwd(), path_malicious)
                self.path_normal = os.path.join(os.getcwd(), path_normal)
            except:
                logging.error('Paths does not exist')
                exit(1)
        self.dataset = MeanSharkDataset()

    @property
    def output(self):
        return self.make()

    def make(self):
        pass

    def build_raw_dataset(self):
        raw_dataset = []
        raw_stats = []
        raw_labels = []
        malicious_capture = os.listdir(self.path_malicious)
        normal_capture = os.listdir(self.path_normal)
        for capture in malicious_capture:
            logging.info(f'Adding {capture} (MALICIOUS) data to our raw dataset...\n')
            extractor = DataExtractor(os.path.join(self.path_malicious, capture))
            samples = extractor.split_raw_capture(200, max=200)

            for sample in samples:
                data_sample = extractor.extract_data(split_capture=sample)
                processor = Processor(data_sample)
                processed_sample = processor.output
                stats = processed_sample.stats
                sample_array = processed_sample.to_array()
                raw_dataset.append(sample_array)
                sample_stats = []
                sample_stats.append(stats.bitrate)
                sample_stats.append(stats.ip_amount)
                sample_stats.append(stats.port_amount)
                raw_stats.append(sample_stats)
                raw_labels.append(1)
                print("\rsamples processed : " + "█"*int(
                    (len(raw_labels) / len(samples)) * 100) + " " +
                      f"{int(((len(raw_labels) + 1) / len(samples)) * 100)}%", end='')
            print("")

        for capture in normal_capture:
            logging.info(f'Adding {capture} (NORMAL) data to our raw dataset...\n')
            extractor = DataExtractor(os.path.join(self.path_normal, capture))
            samples = extractor.split_raw_capture(200, max=200)

            for sample in samples:
                data_sample = extractor.extract_data(split_capture=sample)
                processor = Processor(data_sample)
                processed_sample = processor.output
                stats = processed_sample.stats
                sample_array = processed_sample.to_array()
                raw_dataset.append(sample_array)
                raw_stats.append(stats.bitrate)
                raw_stats.append(stats.ip_amount)
                raw_stats.append(stats.port_amount)
                raw_labels.append(0)
                print(f"\r{len(raw_dataset) + 1}" + " samples processed : " + "█"*int(
                    (len(raw_dataset) / len(samples)) * 100) + " " +
                      f"{int(((len(raw_dataset) + 1) / len(samples)) * 100)}%", end='')

            print("")

        logging.info("Raw data build successfully")
        return raw_dataset, raw_stats, raw_labels


    def list_capture_files(self):
        print("malicious :")
        print(os.listdir(self.path_malicious))
        malicious_list = os.listdir(self.path_malicious)
        print("normal :")
        print(os.listdir(self.path_normal))
        normal_list = os.listdir(self.path_normal)
        return malicious_list, normal_list