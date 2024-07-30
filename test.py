#import torch
from extracting import DataExtractor
import utils
import json

utils.welcome()

test_extract = DataExtractor("dataicmp.pcapng")


split = test_extract.split_raw_capture(50)
a = test_extract.extract_data()
print(a)
a.show()
#print(torch.cuda.is_available())