import torch
import numpy as np
from extracting import DataExtractor
import utils
from processing import Processor
from dataset_maker import DatasetMaker, MeanSharkDataset
import gc
from training import Trainer
import argparse

#a = test_extract.extract_data()
#processor = Processor(a)
#processed_capture = processor.output
#processed_cap_array = processed_capture.to_array()
#np_array = np.array(processed_cap_array)
#tensor = torch.tensor(processed_cap_array,dtype=torch.float)

#
#
#
#mean_shark_dataset = MeanSharkDataset()
#gc.collect()
#o.save_dataset_to_json()

#print(torch.cuda.is_available())


def make_dataset():
    dataset_maker = DatasetMaker("malicious","normal")
    o = dataset_maker.make()
    gc.collect()
    o.save_dataset_to_json()


def add_data_to_dataset():
    dataset_maker = DatasetMaker("malicious","normal")
    dataset_maker.add_data_to_dataset()


def train():
    mean_shark_dataset = MeanSharkDataset()
    trainer = Trainer(mean_shark_dataset)
    trainer.train()
    trainer.test()
    trainer.save_model()

utils.welcome()


parser = argparse.ArgumentParser(description='Exécute une fonction différente en fonction de l\'argument.')


parser.add_argument('-m','--make', action='store_true', help='Make a new dataset (json file) with data in Datasets folder.')
parser.add_argument('-a','--add', action='store_true', help='Add data from Datasets folder to the current dataset (json file).')
parser.add_argument('-t','--train', action='store_true', help='Train the model with the data encoded in the dataset (json file).')


args = parser.parse_args()

if args.make:
    make_dataset()
elif args.add:
    add_data_to_dataset()
elif args.train:
    train()
else:
    print("-m or --make : Make a new dataset (json file) with data in Datasets folder.")
    print("-a or --add : Add data from Datasets folder to the current dataset (json file).")
    print("-t or --train : Train the model with the data encoded in the dataset (json file).")




