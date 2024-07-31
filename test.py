import torch
import numpy as np
from extracting import DataExtractor
import utils
from processing import Processor
from dataset_maker import DatasetMaker

utils.welcome()

#test_extract = DataExtractor("dataicmp.pcapng")

#a = test_extract.extract_data()
#processor = Processor(a)
#processed_capture = processor.output
#processed_cap_array = processed_capture.to_array()
#np_array = np.array(processed_cap_array)
#tensor = torch.tensor(processed_cap_array,dtype=torch.float)

dataset_maker = DatasetMaker("Datasets/malicious","Datasets/normal")
dataset_maker.build_raw_dataset()


print(torch.cuda.is_available())