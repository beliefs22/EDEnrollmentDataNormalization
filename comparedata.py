import csv
from collections import OrderedDict
import os

class OrderedDefaultDict(OrderedDict):

    def __init__(self, *a, **kw):
        default_factory = kw.pop('default_factory', self.__class__)
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __missing__(self, key):
        self[key] = value = self.default_factory()
        return value

network_path = r'\\win.ad.jhu.edu\cloud\sddesktop$\CEIRS\Patient_Data' + os.sep
automated_data_file = network_path + 'redcap_data.csv'
manual_data_file_15 = network_path + 'manually_pulled_ed_enrollment.csv'
compare_filename = network_path + 'comparison.csv'


#Get data from files
with open(automated_data_file,'r') as automated_file, open(manual_data_file_15, 'r') as manual_15_file,\
        open(compare_filename, 'w') as compare_file:

    #Automated data
    automated_reader = csv.DictReader(automated_file)
    automated_data = OrderedDefaultDict()
    for row in automated_reader:
        automated_data[row['id']] = row


    #Manual data 15
    manual_15_reader = csv.DictReader(manual_15_file)
    manual_15_data = OrderedDefaultDict()
    for row in manual_15_reader:
        manual_15_data[row['id']] = row

    #Create Comparison file
    field_names = automated_reader.fieldnames
    compare_file_writer = csv.DictWriter(compare_file, fieldnames=field_names, restval='No Data', lineterminator='\n')
    compare_file_writer.writeheader()
    study_ids = set(list(automated_data.keys()) + list(manual_15_data.keys()))

    for study_id in study_ids:
        #write automated data found
        if automated_data.get(study_id) and manual_15_data.get(study_id):
            compare_file_writer.writerow(automated_data[study_id])
            compare_file_writer.writerow(manual_15_data[study_id])

