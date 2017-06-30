import geteddata as ed
from edvisitclasses import ADT, Vitals, Lab, Medication, Imaging
from collections import defaultdict
from datetime import datetime

def get_arrival_info(human, machine, subject_id, conn):
    """Stores subjects arrival info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
        data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
        
    arrival_info = ADT(*ed.arrival_date_time(subject_id, conn))
    human['Arrival Date'] = arrival_info.date
    human['Arrival Time'] = arrival_info.time
    machine['as_edenroll_arrived'] = arrival_info.date
    machine['as_edenroll_arrivet'] = arrival_info.time

    return human, machine


def get_discharge_info(human, machine, subject_id, conn):
    """Stores subjects discharge info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
        data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    discharge_info = ADT(*ed.arrival_date_time(subject_id, conn))
    human['Discharge Date'] = discharge_info.date
    human['Discharge Time'] = discharge_info.time
    machine['as_edenroll_departd'] = discharge_info.date
    machine['as_edenroll_departt'] = discharge_info.time

    return human, machine
    

def get_dispo_info(human, machine, subject_id, conn):
    """Stores subjects disposition info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
        data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    dispo_info = ADT(*ed.arrival_date_time(subject_id, conn))
    human['Disposition'] = dispo_info.dispo
    machine['as_edenroll_dispo'] = dispo_info.dispo

    return human, machine

def get_vitals_info(human, machine, subject_id, conn):
    """Stores subjects vitals info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
        data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Function to find minimums
    min_lab = lambda x : datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
    
    #Temp
    temp = ed.vitals(subject_id, conn, "'Temp'")
    if temp:
        temp = min(temp, key=min_lab)[2]
        human['temp'] = temp
        machine['as_edenroll_temp'] = temp
    #Resp
    resp = ed.vitals(subject_id, conn, "'Resp'")
    if resp:
        resp = min(resp, key=min_lab)[2]
        human['resp'] = resp
        machine['as_edenroll_rr'] = resp
    #Blood Pressure
    bp = ed.vitals(subject_id, conn, "'BP'")
    if bp:
        bp = min(bp, key=min_lab)[2]
        human['bp'] = bp
        machine['as_edenroll_sbp'] = bp
    #Pulse
    pulse = ed.vitals(subject_id, conn, "'Pulse'")
    if pulse:
        pulse = min(pulse, key=min_lab)[2]
        human['pulse'] = pulse
        machine['as_edenroll_pulse'] = pulse
    #O2 SAT
    oxygen_sat = ed.vitals(subject_id, conn, "'SpO2'")
    if oxygen_sat:
        oxygen_sat = min(oxygen_sat, key=min_lab)[2]
        human['Oxgyen Saturation'] = oxygen_sat
        machine['as_edenroll_o2s'] = oxygen_sat


    return human, machine


def get_oxygen_info(human, machine, subject_id, conn):
    """Stores subjects oxygen info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
        data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Find relevant O2 devices
    oxygen_info = ed.vitals(subject_id, conn, "'O2 Device'")

   #Find all oxygen values     
    if oxygen_info:
        human['Oxygen Supplmentation'] = str()
        #Function to find minimums
        min_vital = lambda x : datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')

        #Find first Oxygen value
        min_oxygen = Vitals(*min(oxygen_info, key=min_vital))
        if min_oxygen.value in ('Nasal cannula','Non-rebreather mask',
                                'High flow nasal cannula','Simple Facemask',
                                'Trach mask', 'Venturi mask'):
            human['Oxygen sup on arrival'] = "{} Recorded at {}".format(
                min_oxygen.value, min_oxygen.date_time)
            machine['as_edenroll_o2sup'] = 'Yes'
            machine['as_edenroll_o2sup_r'] = min_oxygen.value
        #Find all oxygen values
        for vital_sign in oxygen_info:
            oxygen = Vitals(*vital_sign)
            if oxygen.value in ('Nasal cannula','Non-rebreather mask',
                                'High flow nasal cannula','Simple Facemask',
                                'Trach mask', 'Venturi mask'):
                human[
                    'Oxygen Supplmentation in ED'
                    ] = "{} Recorded At {}, ".format(oxygen.value,
                                                      oxygen.date_time)
                machine['as_edenroll_suppoxy_ed'] = 'Yes'
                machine['as_edenroll_suppoxy_ed'] = oxygen.value
            

    return human, machine

def get_lab_info(human, machine, subject_id, conn):
    """Stores subjects arrival info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
        data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    
    #Function to find minimums
    min_lab = lambda x : datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
    #PH
    ph = ed.lab(subject_id, conn, "'PH SPECIMEN'")
    if ph:
        ph = min(ph, key=min_lab)[0]
        human['ph'] = ph
        machine['as_edenroll_ph'] = ph
    #BUN
    bun_compnames = """LabComponentName = 'BLOOD UREA NITROGEN'
                    OR LabComponentName = 'UREA NITROGEN'"""
    bun = ed.lab2(subject_id, conn, bun_compnames)
    if bun:
        bun = min(bun, key=min_lab)[0]
        human['bun'] = bun
        machine['as_edenroll_bun'] = bun
    #Sodium
    sodium = ed.lab(subject_id, conn, "'SODIUM'")
    if sodium:
        sodium = min(sodium, key=min_lab)[0]
        human['sodium'] = sodium
        machine['as_edenroll_sodium'] = sodium
    #Glucose
    glucose = ed.lab(subject_id, conn, "'GLUCOSE'")
    if glucose:
        glucose = min(glucose, key=min_lab)[0]
        human['glucose'] = glucose
        machine['as_edenroll_glucose'] = glucose
    #Hematocrit
    hematocrit = ed.lab(subject_id, conn, "'HEMATOCRIT'")
    if hematocrit:
        hematocrit = min(hematocrit, key=min_lab)[0]
        human['hematocrit'] = hematocrit
        machine['as_edenroll_hemocr'] = hematocrit

    return human, machine

def get_flutesting_info(human, machine, subject_id, conn, dc_time):
    """Stores subjects flu testing info in dictionaies to use for file writing
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Influenza Testing
    influenza_count = 0
    influenza_compnames = """LabComponentName = 'INFLUENZA A NAT'
                  OR LabComponentName = 'INFLUENZA B NAT'"""
    influneza_tests = ed.lab2(subject_id, conn, influenza_compnames)
    influenza_testing = defaultdict(str)
    if influneza_tests:
        machine['as_edenroll_flutesting'] = 'Yes'
    for test_result in influneza_tests:
        influenza_lab = Lab(*test_result)
        if influenza_lab.check_time(dc_time) == True:
            influenza_count += 1
            if influenza_count > 5:
                break
            result = influenza_lab.value
            test_name = influenza_lab.labname
            result_type = influenza_lab.componentname
            result_time = influenza_lab.date_time
            if result == 'No RNA Detected':
                result = 'negative'
            if result == 'DNA Detected':
                result = "{} {}".format(result_type, result)
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
        
        human[influenza_result_name] = influenza_result
        machine['as_edenroll_flut{}_name'.format(influenza_count)] = test_name
        machine['as_edenroll_flut{}_testtype'.format(influenza_count)] = testing_type
        machine['as_edenroll_flut{}_res'.format(influenza_count)] = test_result
        machine['as_edenroll_flut{}_resd'.format(influenza_count)] = test_date
        machine['as_edenroll_flut{}_rest'.format(influenza_count)] = test_time                     

    #Record Number of Influenza Test Done
    machine['as_edenroll_flutests'] = influenza_count

    return human, machine
    

def get_othervir_info(human, machine, subject_id, conn, dc_time):
    """Stores subjects other virus info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Other Virus Testing
    othervirus_compnames = """LabComponentName = 'PARAINFLUENZAE 3 NAT'
                  OR LabComponentName = 'ADENOVIRUS NAT'
                  OR LabComponentName = 'RHINOVIRUS NAT'
                  OR LabComponentName = 'PARAINFLUENZAE 2 NAT'
                  OR LabComponentName = 'METAPNEUMO NAT'
                  OR LabComponentName = 'RSV NAT'"""
    other_virus_tests = ed.lab2(subject_id, conn, othervirus_compnames)
    if other_virus_tests:
        machine['as_edenroll_othervir'] = 'Yes'
    
    othervirus_testing = defaultdict(str)
    for test_result in other_virus_tests:
        othervirus_lab = Lab(*test_result)
        if othervirus_lab.check_time(dc_time) == True:
            result = othervirus_lab.value
            result_time = othervirus_lab.date_time
            result_type = othervirus_lab.componentname
            test_name = othervirus_lab.labname
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
        human[othervirus_result_name] = othervirus_result
        test_name, order_time = othervirus_result_name.split("|")
        machine_link = {'RSV NAT' : 'as_edenroll_othervir_rsv',
                        'RHINOVIRUS NAT' : 'as_edenroll_othervir_rhino',
                        'ADENOVIRUS NAT' : 'as_edenroll_othervir_adeno',
                        'PARAINFLUENZAE 3 NAT' : 'as_edenroll_othervir_para',
                        'PARAINFLUENZAE 2 NAT' : 'as_edenroll_othervir_para',
                        'METAPNEUMO NAT' : 'as_edenroll_othervir_meta'
                        }
        machine[machine_link[test_name]] = othervirus_result

    return human, machine

def get_micro_info(human, machine, subject_id, conn,dc_time):
    """Stores subjects microbiology info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Microbiology
    micro_test_num = 0
    searchtext = "'%CULT%'"
    micro_tests = ed.lab3(subject_id, conn, searchtext)
    if micro_tests:
        machine['as_edenroll_cul'] = 'Yes'
    for micro_test in micro_tests:
        micro_lab = Lab(*micro_test)
        if micro_lab.check_time(dc_time) == True:
            micro_test_num += 1
            if micro_test_num > 5:
                break
            result = micro_lab.value
            result_time = micro_lab.date_time
            result_type = micro_lab.componentname
            test_name = micro_lab.labname
            result_id = "{}|{}".format(test_name, result_time)
            if result and result != "No growth":
                human[result_id] = result
                machine['as_edenroll_culname{}'.format(micro_test_num)] = test_name
                machine['as_edenroll_culdate{}'.format(micro_test_num)] = result_time
                machine['as_edenroll_culorg{}'.format(micro_test_num)] = result
                machine['as_edenroll_cultype{}'.format(micro_test_num)] = test_name.split(" ")[-1]
    #Record Number of Micro Test done
    machine['as_edenroll_culnum'] = micro_test_num

    return human, machine

def get_antiviral_info(human, machine, subject_id, conn, dc_time):
    """Stores subjects antiviral info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #ED Antivirals
    ed_antiviral_count = 0
    ed_antivirals = ed.medication(
        subject_id, conn, "'ANTIVIRALS'", "'Inpatient'")
    if ed_antivirals:
        machine['as_edenroll_fluav'] = 'Yes'
    for antiviral in ed_antivirals:
        antiviral_lab = Medication(*antiviral)
        if antiviral_lab.check_time(dc_time) == True:
            ed_antiviral_count += 1
            if ed_antiviral_count > 2:
                break
            med_name = antiviral_lab.name.split(" ")[0]
            order_date_time = antiviral_lab.date_time
            order_date, order_time = order_date_time.split(" ")
            med_route = antiviral_lab.route
            human["ED Antiviral #{}".format(
                ed_antiviral_count)] = "{} {}".format(
                med_name, med_route)
            machine['as_edenroll_fluav{}_name'.format(
                ed_antiviral_count)] = med_name
            machine['as_edenroll_fluav{}route'.format(
                ed_antiviral_count)] = med_route
            machine['as_edenroll_fluav{}date'.format(
                ed_antiviral_count)] = order_date
            machine['as_edenroll_fluav{}time'.format(
                ed_antiviral_count)] = order_time
    #Record number of Antivrals
    machine['as_edenroll_fluavnum'] = ed_antiviral_count

    return human, machine

def get_dc_antiviral_info(human, machine, subject_id, conn, dc_time, dispo):
    """Stores subjects discharge antiviral info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time
		dispo (str): subjects final disposition

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    if dispo != "Discharge":
        machine['as_edenroll_fluavdisc'] = 'NA subject not discharged'
        return human, machine

    #Discharge Antivirals
    discharge_antiviral_count = 0
    discharge_antivirals = ed.medication(
        subject_id, conn, "'ANTIVIRALS'", "'Outpatient'")
    if discharge_antivirals:
        machine['as_edenroll_fluavdisc'] = 'Yes'
    for antiviral in discharge_antivirals:
        dc_antiviral_lab = Medication(*antiviral)
        if dc_antiviral_lab.check_time(dc_time) == True:
            discharge_antiviral_count += 1
            if discharge_antiviral_count > 2:
                break
            med_name = dc_antiviral_lab.name.split(" ")[0]
            order_date_time = dc_antiviral_lab.date_time
            order_date, order_time = order_date_time.split(" ")
            med_route = dc_antiviral_lab.route
            human[
                "Discharge Antiviral #{}".format(
                    discharge_antiviral_count)] = "{} {}".format(
                med_name, med_route)
            machine['as_edenroll_fluavdisc{}'.format(
                discharge_antiviral_count)] = med_name
    #Record number of Dishcarged Antivirals
    machine['as_edenroll_fluavdiscct'] = discharge_antiviral_count

    return human, machine

def get_antibiotic_info(human, machine, subject_id, conn, dc_time):
    """Stores subjects antibiotic info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #ED Antibiotics
    ed_antibiotics_count = 0
    ed_antibiotics = ed.medication(
        subject_id, conn, "'ANTIBIOTICS'", "'Inpatient'")
    if ed_antibiotics:
        machine['as_edenroll_ab_ed'] = 'Yes'
    for antibiotic in ed_antibiotics:
        abx_med = Medication(*antibiotic)
        if abx_med.check_time(dc_time) == True:            
            ed_antibiotics_count += 1
            if ed_antibiotics_count > 5:
                break
            med_name = abx_med.name.split(" ")[0]
            order_date_time = abx_med.date_time
            order_date, order_time = order_date_time.split(" ")
            med_route = abx_med.route
            human["ED Antibiotics #{}".format(
                    ed_antibiotics_count)] = "{} {} {} {}".format(
                    med_name, med_route, order_date, order_time)
            machine['as_edenroll_ab_ed{}_name'.format(
                    ed_antibiotics_count)] = med_name
            machine['as_edenroll_ab_ed{}date'.format(
                    ed_antibiotics_count)] = order_date
            machine['as_edenroll_ab_ed{}time'.format(
                    ed_antibiotics_count)] = order_time
            machine['as_edenroll_ab_ed{}route'.format(
                    ed_antibiotics_count)] = med_route
    #Record number of ED Antibiotics
    machine['as_edenroll_ab_ed_num'] = ed_antibiotics_count

    return human, machine

def get_dc_abx_info(human, machine, subject_id, conn, dc_time, dispo):
    """Stores subjects discharge antibiotic info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time
		dispo (str): subjects final disposition

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    if dispo != "Discharge":
        machine['as_edenroll_dabx'] = 'NA subject not discharging'
        return human, machine
    #Discharge Antibiotics
    discharge_antibiotics_count = 0
    discharge_antibiotics = ed.medication(
        subject_id, conn, "'ANTIBIOTICS'", "'Outpatient'")
    if discharge_antibiotics:
        machine['as_edenroll_dabx'] = 'Yes'
    for antibiotic in discharge_antibiotics:
        dc_abx_med = Medication(*antibiotic)
        if dc_abx_med.check_time(dc_time) == True:
            discharge_antibiotics_count += 1
            if discharge_antibiotics_count > 2:
                break
            med_name = dc_abx_med.name.split(" ")[0]
            time_ordered = dc_abx_med.date_time
            med_route = dc_abx_med.route
            human[
                "Discharge Antibiotics #{}".format(
                    discharge_antibiotics_count)] = "{} {} {}".format(
                med_name, med_route, time_ordered)
            machine[
                'as_edenroll_dabx{}name'.format(
                    discharge_antibiotics_count)] = med_name
    #Record number of Discharge Abx
    machine['as_edenroll_abxquant'] = discharge_antibiotics_count

    return human, machine

def get_imaging_info(human, machine, subject_id, conn):
    """Stores subjects imaging info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Chest Imaging
    chest_xray_ct = ed.chest_imaging(subject_id, conn)
    human["Chest Imaging"] = chest_xray_ct
    machine['as_edenroll_chest'] = 'Yes'

    return human, machine

def get_diagnosis_info(human, machine, subject_id, conn):
    """Stores subjects diagnosis info in dictionaies to use for file
    writing
    
    Args:
        human (:obj: `OrderedDefaultDict`): collection of human readable data
            to write to file
        machine (:obj: `OrderedDefaultDict`): collection of machine readable
            data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - human and machine that
        contain data to write to file
    """
    #Final Diagnoses
    diagnosis_count = 0
    diagnoses = ed.final_diagnoses(subject_id, conn)
    human['Diagnoses'] = diagnoses
    for diagnosis in diagnoses:
        diagnosis_count += 1
        #Record Diagnosis Number
        machine['as_edenroll_findxnum'] = diagnosis_count
        if diagnosis_count > 3:
            break
        machine['as_edenroll_findx{}'.format(diagnosis_count)] = \
                                                                    diagnosis[0]
    return human, machine    


    
    
