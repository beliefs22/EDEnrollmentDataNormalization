import geteddata
from collections import OrderedDict
import sqlite3
import os
import csv
from edhelpers import *
import comparedata


class OrderedDefaultDict(OrderedDict):

    def __init__(self, *a, **kw):
        default_factory = kw.pop('default_factory', self.__class__)
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __missing__(self, key):
        self[key] = value = self.default_factory()
        return value


def edvisit(subject_id, conn):
    """Gets available ED visit data from CEIRS Tables

    Args:
        subject_id (str): id of subject
        conn (:obj:) `database connection): connetion to the database that
            contains the data

    Returns:
        :obj: `OrderedDefaultDict`
        returns two ordered default dictionaires with data for writing to file
        one with human readable data, and one with machien readable data
    """

    human_readable_data = human = OrderedDefaultDict()
    machine_data = machine = OrderedDefaultDict()
    subject_id_for_file = subject_id.replace("'","").lower()
    human_readable_data['Study ID'] = subject_id_for_file
    machine_data['id'] = subject_id_for_file
    machine_data['redcap_data_access_group'] = 'jhhs'
    #Get Discharge time for time checking
    dc_info = ADT(*geteddata.discharge_date_time(subject_id, conn))
    #Get Dispo Status for checking
    dispo = dc_info.dispo
    dc_time = "{} {}".format(dc_info.date, dc_info.time)
    human, machine = get_arrival_info(human, machine, subject_id, conn)
    human, machine = get_discharge_info(human, machine, subject_id, conn)
    human, machine = get_dispo_info(human, machine, subject_id, conn)
    human, machine = get_vitals_info(human, machine, subject_id, conn)
    human, machine = get_oxygen_info(human, machine, subject_id, conn)
    human, machine = get_lab_info(human, machine, subject_id, conn)
    human, machine = get_flutesting_info(human, machine, subject_id, conn, dc_time)
    human, machine = get_othervir_info(human, machine, subject_id, conn, dc_time)
    human, machine = get_micro_info(human, machine, subject_id, conn, dc_time)
    human, machine = get_antiviral_info(human, machine, subject_id, conn, dc_time)
    human, machine = get_dc_antiviral_info(human, machine, subject_id, conn, dc_time, dispo)
    human, machine = get_antibiotic_info(human, machine, subject_id, conn, dc_time)
    human, machine = get_dc_abx_info(human, machine, subject_id, conn, dc_time, dispo)
    human, machine = get_imaging_info(human, machine, subject_id, conn)
    human, machine = get_diagnosis_info(human, machine, subject_id, conn)

    return human, machine


def main():
    #Get File Path for Database and Patient data
    #Get Base File Path
    os.chdir("..")
    base_path = os.getcwd()
    sep = os.sep
    patient_data_path = base_path + sep + "Patient_Data"
    conn = sqlite3.connect(r"{}{}CEIRS.db".format(base_path,sep))
    # Get subject IDs
    cur = conn.cursor()
    sql = """SELECT DISTINCT STUDYID FROM Demographics"""
    cur.execute(sql)
    subject_ids = cur.fetchall()
    sep = os.sep
    # Get ED Enrollment Headers
    ed_enrollment_header_file = open(r"{}{}ed_enrollment_headers.csv".format(patient_data_path, sep), 'r')
    ed_header_reader = csv.DictReader(ed_enrollment_header_file)
    ed_enrollment_headers = ed_header_reader.fieldnames
    data_for_redcap = list()
    
    for subject_id in subject_ids:
        subject_id = "'{}'".format(subject_id[0])
        subject_id_for_file = subject_id.replace("'","").lower()
        with open(patient_data_path + sep + "{}_data.txt".format(subject_id_for_file),'w') as outfile1:
            # Write Files for Coordinators to Read
            print("Writing Human Data File for Subject {}".format(subject_id_for_file))
            human_readable_data, machine_data = edvisit(subject_id, conn)
            for key,value in human_readable_data.items():
                outfile1.write("{}: {}\n".format(key, value))
            # Data to import into redcap
            data_for_redcap.append(machine_data)
    print("Finished writing all human files")
    print("Starting write to redcap data file")
    with open(patient_data_path + sep + "redcap_data.csv", 'w') as outfile2:
        redcap_file = csv.DictWriter(
            outfile2, fieldnames=ed_enrollment_headers, restval='',
            lineterminator='\n')
        redcap_file.writeheader()
        for row in data_for_redcap:
            redcap_file.writerow(row)
    print("Finished writing all data files")
    # create comparison file to compare manual data to auto data
##    print("Writing Comparison File")
##    comparedata.compare()
##    print("Finished writing compare file")
    print("All Done!")

            

if __name__ =="__main__":
    main()
