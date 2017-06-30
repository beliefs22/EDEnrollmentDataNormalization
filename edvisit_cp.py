import geteddata
from collections import OrderedDict, defaultdict
import sqlite3
import os
from datetime import datetime
import csv
from edvisitclasses import ADT, Lab, Medication, Imaging


class OrderedDefaultDict(OrderedDict):

    def __init__(self, *a, **kw):
        default_factory = kw.pop('default_factory', self.__class__)
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __missing__(self, key):
        self[key] = value = self.default_factory()
        return value


def edvisit(subject_id, conn):
    """Gets available ED visit data from CEIRS Tables"""
    cur = conn.cursor()

    human_readable_data = OrderedDefaultDict()
    machine_data = OrderedDefaultDict()
    subject_id_for_file = subject_id.replace("'","")
    human_readable_data['Study ID'] = subject_id_for_file
    machine_data['id'] = subject_id_for_file
    machine_data['redcap_data_access_group'] = 'jhhs'
    #Arrival Date and Time
    arrival_info = ADT(*geteddata.arrival_date_time(subject_id, conn))
    human_readable_data['Arrival Date'] = arrival_info.date
    human_readable_data['Arrival Time'] = arrival_info.time
    machine_data['as_edenroll_arrived'] = arrival_info.date
    machine_data['as_edenroll_arrivet'] = arrival_info.time
    #Discharge Date and Time
    discharge_info = ADT(*geteddata.discharge_date_time(subject_id, conn))
    human_readable_data['Discharge Date'] = discharge_info.date
    human_readable_data['Discharge Time'] = discharge_info.time
    machine_data['as_edenroll_departd'] = discharge_info.date
    machine_data['as_edenroll_departt'] = discharge_info.time

    #Disposition
    human_readable_data['Disposition'] = discharge_info.dispo
    machine_data['as_edenroll_dispo'] = arrival_info.dispo

    #ED Arrival and Discharge Times for comparison
    ed_arrvial_date = datetime.strptime(arrival_info.date, '%Y-%m-%d')
    ed_arrival_time = datetime.strptime(arrival_info.time, '%H:%M:%S')
    ed_arrival_date_and_time = datetime.strptime("{} {}".format(
        arrival_info.date, arrival_info.time), '%Y-%m-%d %H:%M:%S')
    ed_discharge_date = datetime.strptime(discharge_info.date, '%Y-%m-%d')
    ed_discharge_time = datetime.strptime(discharge_info.time, '%H:%M:%S')
    ed_discharge_date_and_time = datetime.strptime("{} {}".format(
        discharge_info.date, discharge_info.time), '%Y-%m-%d %H:%M:%S')
    #Function to find minimums
    min_lab = lambda x : datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
    #PH
    ph = geteddata.lab(subject_id, conn, "'PH SPECIMEN'")
    if ph:
        ph = min(ph, key=min_lab)[0]
        human_readable_data['ph'] = ph
        machine_data['as_edenroll_ph'] = ph

    #BUN
    bun_compnames = """LabComponentName = 'BLOOD UREA NITROGEN'
                    OR LabComponentName = 'UREA NITROGEN'"""
    bun = geteddata.lab2(subject_id, conn, bun_compnames)
    if bun:
        bun = min(bun, key=min_lab)[0]
        human_readable_data['bun'] = bun
        machine_data['as_edenroll_bun'] = bun
    #Sodium
    sodium = geteddata.lab(subject_id, conn, "'SODIUM'")
    if sodium:
        sodium = min(sodium, key=min_lab)[0]
        human_readable_data['sodium'] = sodium
        machine_data['as_edenroll_sodium'] = sodium
    #Glucose
    glucose = geteddata.lab(subject_id, conn, "'GLUCOSE'")
    if glucose:
        glucose = min(glucose, key=min_lab)[0]
        human_readable_data['glucose'] = glucose
        machine_data['as_edenroll_glucose'] = glucose
    #Hematocrit
    hematocrit = geteddata.lab(subject_id, conn, "'HEMATOCRIT'")
    if hematocrit:
        hematocrit = min(hematocrit, key=min_lab)[0]
        human_readable_data['hematocrit'] = hematocrit
        machine_data['as_edenroll_hemocr'] = hematocrit

    #Influenza Testing
    influenza_compnames = """LabComponentName = 'INFLUENZA A NAT'
                  OR LabComponentName = 'INFLUENZA B NAT'"""
    influneza_tests = geteddata.lab2(subject_id, conn, influenza_compnames)
    influenza_testing = defaultdict(str)
    if influneza_tests:
        machine_data['as_edenroll_flutesting'] = 'Yes'
    for test_result in influneza_tests:
        result = test_result[0]
        result_time = test_result[1]
        result_type = test_result[2]
        test_name = test_result[3]
        influenza_result_date_time = datetime.strptime(
            result_time, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           influenza_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            if result == 'No RNA Detected':
                result = 'negative'
            if result == 'DNA Detected':
                result = result_type + " {}".format(result)
            result_id = "{}|{}".format(test_name, result_time)
            #Negative Results
            if result == 'negative':
                if not influenza_testing.get(result_id):
                    influenza_testing[result_id] = result
                    continue
                if influenza_testing[result_id] != 'negative':
                    continue
            #Positive Results
            if result:
                if influenza_testing.get(result_id) == 'negative':
                    influenza_testing[result_id] = result
                    continue
                else:
                    influenza_testing[result_id] += " {}".format(result)
                    continue

    #Write Influenza Results to file
    influenza_count = 0
    for influenza_result_name, influenza_result in \
        influenza_testing.items():
        test_name, order_time = influenza_result_name.split("|")
        test_date, test_time = order_time.split(" ")
        influenza_count += 1
        testing_type = 'pcr'
        if influenza_result == 'negative':
            test_result = 'negative'
        else:
            test_result = 'positive'
        
        human_readable_data[influenza_result_name] = influenza_result
        machine_data[
            'as_edenroll_flut{}_name'.format(influenza_count)] = test_name
        machine_data[
            'as_edenroll_flut{}_testtype'.format(
                influenza_count)] = testing_type
        machine_data[
            'as_edenroll_flut{}_res'.format(
                influenza_count)] = test_result
        machine_data[
            'as_edenroll_flut{}_resd'.format(influenza_count)] = test_date
        machine_data[
            'as_edenroll_flut{}_rest'.format(influenza_count)] = test_time                     

    #Record Number of Influenza Test Done
    machine_data['as_edenroll_flutests'] = influenza_count        

    #Other Virus Testing
    othervirus_compnames = """LabComponentName = 'PARAINFLUENZAE 3 NAT'
                  OR LabComponentName = 'ADENOVIRUS NAT'
                  OR LabComponentName = 'RHINOVIRUS NAT'
                  OR LabComponentName = 'PARAINFLUENZAE 2 NAT'
                  OR LabComponentName = 'METAPNEUMO NAT'
                  OR LabComponentName = 'RSV NAT'"""
    other_virus_tests = geteddata.lab2(subject_id, conn, othervirus_compnames)
    
    othervirus_testing = defaultdict(str)
    for test_result in other_virus_tests:
        result = test_result[0]
        result_time = test_result[1]
        result_type = test_result[2]
        test_name = test_result[3]
        other_vir_result_date_time = datetime.strptime(
            result_time, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           other_vir_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            if result == 'No RNA Detected':
                result = 'negative'
            if result == 'DNA Detected':
                result = result_type + " {}".format(result)
            result_id = "{}|{}".format(result_type, result_time)
            #Negative Results
            if result == 'negative':
                if not othervirus_testing.get(result_id):
                    othervirus_testing[result_id] = result
                    continue
                if othervirus_testing[result_id] != 'negative':
                    continue
            #Positive Results
            if result:
                if othervirus_testing.get(result_id) == 'negative':
                    othervirus_testing[result_id] = result
                    continue
                else:
                    othervirus_testing[result_id] += " {}".format(result)
                    continue

    #Write Other Virus Tested Results to file
    for othervirus_result_name, othervirus_result in \
        othervirus_testing.items():
        human_readable_data[othervirus_result_name] = othervirus_result
        test_name, order_time = othervirus_result_name.split("|")
        machine_link = {'RSV NAT' : 'as_edenroll_othervir_rsv',
                        'RHINOVIRUS NAT' : 'as_edenroll_othervir_rhino',
                        'ADENOVIRUS NAT' : 'as_edenroll_othervir_adeno',
                        'PARAINFLUENZAE 3 NAT' : 'as_edenroll_othervir_para',
                        'PARAINFLUENZAE 2 NAT' : 'as_edenroll_othervir_para',
                        'METAPNEUMO NAT' : 'as_edenroll_othervir_meta'
                        }
        machine_data[machine_link[test_name]] = othervirus_result
        

    #Microbiology
    micro_test_num = 0
    searchtext = "'%CULT%'"
    micro_tests = geteddata.lab3(subject_id, conn, searchtext)
    if micro_tests:
        machine_data['as_edenroll_cul'] = 'Yes'
    for micro_test in micro_tests:
        micro_test_num += 1
        if micro_test_num > 5:
            break
        result = micro_test[0]
        result_time = micro_test[1]
        result_type = micro_test[2]
        test_name = micro_test[3]
        result_id = "{}|{}".format(test_name, result_time)
        micro_result_date_time = datetime.strptime(
            result_time, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           micro_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            if result:
                human_readable_data[result_id] = result
                machine_data['as_edenroll_culname{}'.format(
                    micro_test_num)] = test_name
                machine_data['as_edenroll_culdate{}'.format(
                    micro_test_num)] = result_time
                machine_data['as_edenroll_culorg{}'.format(
                    micro_test_num)] = result
                machine_data['as_edenroll_cultype{}'.format(
                    micro_test_num)] = test_name.split(" ")[-1]
    #Record Number of Micro Test done
    machine_data['as_edenroll_culnum'] = micro_test_num

    #ED Antivirals
    ed_antiviral_count = 0
    ed_antivirals = geteddata.medication(
        subject_id, conn, "'ANTIVIRALS'", "'Inpatient'")
    if ed_antivirals:
        machine_data['as_edenroll_fluav'] = 'Yes'
    for antiviral in ed_antivirals:
        ed_antiviral_count += 1
        if ed_antiviral_count > 2:
            break
        med_name = antiviral[0].split(" ")[0]
        order_date_time = antiviral[1]
        order_date, order_time = order_date_time.split(" ")
        med_route = antiviral[2]
        antiviral_result_date_time = datetime.strptime(
            order_date_time, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           antiviral_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            human_readable_data["ED Antiviral #{}".format(ed_antiviral_count)] = "{} {}".format(
                med_name, med_route)
            machine_data['as_edenroll_fluav{}_name'.format(ed_antiviral_count)] = med_name
            machine_data['as_edenroll_fluav{}route'.format(ed_antiviral_count)] = med_route
            machine_data['as_edenroll_fluav{}date'.format(ed_antiviral_count)] = order_date
            machine_data['as_edenroll_fluav{}time'.format(ed_antiviral_count)] = order_time
    #Record number of Antivrals
    machine_data['as_edenroll_fluavnum'] = ed_antiviral_count
        

    #Discharge Antivirals
    discharge_antiviral_count = 0
    discharge_antivirals = geteddata.medication(
        subject_id, conn, "'ANTIVIRALS'", "'Outpatient'")
    if discharge_antivirals:
        machine_data['as_edenroll_fluavdisc'] = 'Yes'
    for antiviral in discharge_antivirals:
        discharge_antiviral_count += 1
        if discharge_antiviral_count > 2:
            break
        med_name = antiviral[0].split(" ")[0]
        order_date_time = antiviral[1]
        order_date, order_time = order_date_time.split(" ")
        med_route = antiviral[2]
        discharge_av_result_date_time = datetime.strptime(
            order_date_time, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           discharge_av_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            human_readable_data[
                "Discharge Antiviral #{}".format(discharge_antiviral_count)] = "{} {}".format(
                med_name, med_route)
            machine_data['as_edenroll_fluavdisc{}'.format(discharge_antiviral_count)] = med_name
    #Record number of Dishcarged Antivirals
    machine_data['as_edenroll_fluavdiscct'] = discharge_antiviral_count

    #ED Antibiotics
    ed_antibiotics_count = 0
    ed_antibiotics = geteddata.medication(
        subject_id, conn, "'ANTIBIOTICS'", "'Inpatient'")
    if ed_antibiotics:
        machine_data['as_edenroll_ab_ed'] = 'Yes'
    for antibiotic in ed_antibiotics:
        ed_antibiotics_count += 1
        if ed_antibiotics_count > 5:
            break
        med_name = antibiotic[0].split(" ")[0]
        order_date_time = antibiotic[1]
        order_date, order_time = order_date_time.split(" ")
        med_route = antibiotic[2]
        abx_result_date_time = datetime.strptime(
            order_date_time, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           abx_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            human_readable_data[
                "ED Antibiotics #{}".format(ed_antibiotics_count)] = "{} {} {} {}".format(
                    med_name, med_route, order_date, order_time)
            machine_data['as_edenroll_ab_ed{}_name'.format(ed_antibiotics_count)] = med_name
            machine_data['as_edenroll_ab_ed{}date'.format(ed_antibiotics_count)] = order_date
            machine_data['as_edenroll_ab_ed{}time'.format(ed_antibiotics_count)] = order_time
            machine_data['as_edenroll_ab_ed{}route'.format(ed_antibiotics_count)] = med_route
    #Record number of ED Antibiotics
    machine_data['as_edenroll_ab_ed_num'] = ed_antibiotics_count

    #Discharge Antibiotics
    discharge_antibiotics_count = 0
    discharge_antibiotics = geteddata.medication(
        subject_id, conn, "'ANTIBIOTICS'", "'Outpatient'")
    if discharge_antibiotics:
        machine_data['as_edenroll_dabx'] = 'Yes'
    for index, antibiotic in enumerate(discharge_antibiotics):
        discharge_antibiotics_count += 1
        if discharge_antibiotics_count > 2:
            break
        med_name = antibiotic[0].split(" ")[0]
        time_ordered = antibiotic[1]
        med_route = antibiotic[2]
        discharge_abx_result_date_time = datetime.strptime(
            time_ordered, '%Y-%m-%d %H:%M:%S')
        time_between_discharge_and_result = ed_discharge_date_and_time - \
                                           discharge_abx_result_date_time
        if abs(time_between_discharge_and_result.total_seconds()) <= 43200.00:
            human_readable_data["Discharge Antibiotics #{}".format(discharge_antibiotics_count)] = "{} {} {}".format(
                med_name, med_route, time_ordered)
            machine_data['as_edenroll_dabx{}name'.format(discharge_antibiotics_count)] = med_name
    #Record number of Discharge Abx
    machine_data['as_edenroll_abxquant'] = discharge_antibiotics_count
    #Chest Imaging
    chest_xray_ct = geteddata.chest_imaging(subject_id, conn)
    human_readable_data["Chest Imaging"] = chest_xray_ct
    machine_data['as_edenroll_chest'] = chest_xray_ct

    #Final Diagnoses
    diagnosis_count = 0
    diagnoses = geteddata.final_diagnoses(subject_id, conn)
    human_readable_data['Diagnoses'] = diagnoses
    for diagnosis in diagnoses:
        diagnosis_count += 1
        #Record Diagnosis Number
        machine_data['as_edenroll_findxnum'] = diagnosis_count
        if diagnosis_count > 3:
            break
        machine_data['as_edenroll_findx{}'.format(diagnosis_count)] = \
                                                                    diagnosis[0]
    return human_readable_data, machine_data
    

def main():
    conn = sqlite3.connect("CEIRS.db")
    #Get subject IDs
    cur = conn.cursor()
    sql = """SELECT DISTINCT STUDYID FROM DEMOGRAPHICS"""
    cur.execute(sql)
    subject_ids = cur.fetchall()
    patient_data_path = r'\\win.ad.jhu.edu\cloud\sddesktop$\CEIRS\Patient Data'
    sep = os.sep
    #Get ED Enrollment Headers
    ed_enrollment_header_file = open('ed_enrollment_headers.csv', 'r')
    ed_header_reader = csv.DictReader(ed_enrollment_header_file)
    ed_enrollment_headers = ed_header_reader.fieldnames
    data_for_redcap = list()
    
    for subject_id in subject_ids:
        subject_id = "'{}'".format(subject_id[0])
        subject_id_for_file = subject_id.replace("'","")
        with open(patient_data_path + sep + "{}_data.txt".format(
            subject_id_for_file),'w') as outfile1:
            #Write Files for Coordinators to Read
            human_readable_data, machine_data = edvisit(subject_id, conn)
            for key,value in human_readable_data.items():
                print("{}: {}".format(key, value), file=outfile1)
            #Data to import into redcap
            data_for_redcap.append(machine_data)
    with open(patient_data_path + sep + "redcap_data.csv", 'w') as outfile2:
        redcap_file = csv.DictWriter(
            outfile2, fieldnames=ed_enrollment_headers, restval='No Data',
            lineterminator='\n')
        redcap_file.writeheader()
        for row in data_for_redcap:
            redcap_file.writerow(row)

            

if __name__ =="__main__":
    main()
