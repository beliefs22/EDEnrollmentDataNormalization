import createtables
import datapull_sql
from collections import OrderedDict
import sqlite3
import os
import csv
from datapull_functions import *


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
        one with coordinator readable data, and one with machien readable data
    """

    coordinator_readable_data = coordinator = OrderedDefaultDict()
    redcap_label = OrderedDefaultDict()
    redcap_raw = OrderedDefaultDict()
    subject_id_for_file = subject_id.replace("'","").lower()
    coordinator_readable_data['Study ID'] = subject_id_for_file
    redcap_label['ec_id'] = subject_id_for_file
    # redcap_label['redcap_data_access_group'] = 'jhhs'
    redcap_label['edenrollchart_enrolledined'] = 'yes'

    redcap_raw['ec_id'] = subject_id_for_file
    # redcap_raw['redcap_data_access_group'] = 'jhhs'
    redcap_raw['edenrollchart_enrolledined'] = '1'
    
    #Get Discharge time for time checking
    dc_info = ADT(*datapull_sql.discharge_date_time(subject_id, conn))
    #Get Dispo Status for checking
    dispo = dc_info.dispo
    dc_time = "{} {}".format(dc_info.date, dc_info.time)
    coordinator, redcap_label, redcap_raw = get_arrival_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_discharge_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_dispo_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_vitals_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_oxygen_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_lab_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_flutesting_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time)
    coordinator, redcap_label, redcap_raw = get_othervir_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time)
    coordinator, redcap_label, redcap_raw = get_antiviral_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time)
    coordinator, redcap_label, redcap_raw = get_dc_antiviral_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time, dispo)
    coordinator, redcap_label, redcap_raw = get_antibiotic_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time)
    coordinator, redcap_label, redcap_raw = get_dc_abx_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time, dispo)
    coordinator, redcap_label, redcap_raw = get_imaging_info(coordinator, redcap_label, redcap_raw, subject_id, conn)
    coordinator, redcap_label, redcap_raw = get_diagnosis_info(coordinator, redcap_label, redcap_raw, subject_id, conn)

    return coordinator, redcap_label, redcap_raw


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
    #Create Tables that contain data
    createtables.create_tables(conn)
    sql = """SELECT STUDYID, DataPullComplete FROM STUDY_IDS_TO_PULL"""
    cur.execute(sql)
    subject_ids = cur.fetchall()
    sep = os.sep
    # Get ED Enrollment Headers
    ed_enrollment_header_file = open(r"{}{}ed_enrollment_headers.csv".format(patient_data_path, sep), 'r')
    ed_header_reader = csv.DictReader(ed_enrollment_header_file)
    ed_enrollment_headers = ed_header_reader.fieldnames
    labeled_data_for_redcap = list()
    raw_data_for_redcap = list()
    
    for subject_id in subject_ids:
        data_pull_status = subject_id[1]
        if data_pull_status == "No":
            subject_id = "'{}'".format(subject_id[0])
            subject_id_for_file = subject_id.replace("'","").lower()
            with open(patient_data_path + sep + "{}_data.txt".format(subject_id_for_file),'w') as outfile1:
                # Write Files for Coordinators to Read
                print("Writing coordinator Data File for Subject {}".format(subject_id_for_file))
                coordinator_readable_data, redcap_label_data, redcap_raw_data = edvisit(subject_id, conn)
                for key,value in coordinator_readable_data.items():
                    outfile1.write("{}: {}\n".format(key, value))
                # Data to import into redcap
                labeled_data_for_redcap.append(redcap_label_data)
                raw_data_for_redcap.append(redcap_raw_data)
    print("Finished writing all coordinator files")
    print("Starting write to redcap data file")
    with open(patient_data_path + sep + "redcap_label_data.csv", 'w') as outfile2:
        redcap_file = csv.DictWriter(
            outfile2, fieldnames=ed_enrollment_headers, restval='',
            lineterminator='\n')
        redcap_file.writeheader()
        for row in labeled_data_for_redcap:
            redcap_file.writerow(row)
    print("Finished writing Labeled  REDCap data file")

    with open(patient_data_path + sep + "redcap_raw_data.csv", 'w') as outfile2:
        redcap_file = csv.DictWriter(
            outfile2, fieldnames=ed_enrollment_headers, restval='',
            lineterminator='\n')
        redcap_file.writeheader()
        for row in raw_data_for_redcap:
            redcap_file.writerow(row)
    print("Finished writing Raw  REDCap data file")
    print("All Done!")

            

if __name__ =="__main__":
    main()
