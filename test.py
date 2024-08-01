import torch
import numpy as np
from extracting import DataExtractor
import utils
from processing import Processor
from dataset_maker import DatasetMaker, MeanSharkDataset
import gc
from training import Trainer

utils.welcome()

#test_extract = DataExtractor("dataicmp.pcapng")

#a = test_extract.extract_data()
#processor = Processor(a)
#processed_capture = processor.output
#processed_cap_array = processed_capture.to_array()
#np_array = np.array(processed_cap_array)
#tensor = torch.tensor(processed_cap_array,dtype=torch.float)

#dataset_maker = DatasetMaker("malicious","normal")
#o = dataset_maker.make()
mean_shark_dataset = MeanSharkDataset()
#gc.collect()
#o.save_dataset_to_json()
#print(torch.cuda.is_available())
trainer = Trainer(mean_shark_dataset)
trainer.train()
trainer.test()
trainer.save_model()