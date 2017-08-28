import geteddata as ed
from edvisitclasses import ADT, Vitals, Lab, Medication, Medication2, Imaging
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
    machine['edenrollchart_arrivaldate'] = arrival_info.date
    machine['edenrollchart_arrivaltime'] = arrival_info.time

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
    discharge_info = ADT(*ed.discharge_date_time(subject_id, conn))
    human['Discharge Date'] = discharge_info.date
    human['Discharge Time'] = discharge_info.time
    machine['edenrollchart_departtime'] = discharge_info.date
    machine['edenrollchart_temperature'] = discharge_info.time

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
    if dispo_info.dispo == "Discharge":
        machine['edenrollchart_dispo'] = dispo_info.dispo
        return human, machine
    if dispo_info.dispo == "Hospitalized Observation":
        machine['edenrollchart_dispo'] = 'Admit'
        machine['edenrollchart_observation'] = 'Yes'
        return human, machine
    if dispo_info.dispo == 'Eloped':
        machine['edenrollchart_dispo'] = dispo_info.dispo
        return human, machine
    if dispo_info.dispo == 'Admit':
        machine['edenrollchart_dispo'] = dispo_info.dispo
        return human, machine

    machine['edenrollchart_dispo'] = 'Other'
    machine['edenrollchart_dispo_specify'] = dispo_info.dispo    

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
    # Function to find minimums
    min_lab = lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
    
    # Temp
    temp = ed.vitals(subject_id, conn, "'Temp'")
    if temp:
        temp = min(temp, key=min_lab)[2]
        human['temp'] = temp
        machine['edenrollchart_temperature'] = temp
    else:
        human['temp'] = 'Temperature not recorded'
        machine['edenrollchart_temperature'] = '999'
    # Resp
    resp = ed.vitals(subject_id, conn, "'Resp'")
    if resp:
        resp = min(resp, key=min_lab)[2]
        human['resp'] = resp
        machine['edenrollchart_respiratoryrate'] = resp
    else:
        human['resp'] = 'Respirations not recorded'
        machine['edenrollchart_respiratoryrate'] = '999'
    # Blood Pressure
    bp = ed.vitals(subject_id, conn, "'BP'")
    if bp:
        bp = min(bp, key=min_lab)[2]
        human['bp'] = bp
        machine['edenrollchart_systolicbloodpressure'] = bp
    else:
        human['bp'] = 'Blood Pressure not recorded'
        machine['edenrollchart_systolicbloodpressure'] = '999'
    # Pulse
    pulse = ed.vitals(subject_id, conn, "'Pulse'")
    if pulse:
        pulse = min(pulse, key=min_lab)[2]
        human['pulse'] = pulse
        machine['edenrollchart_pulse'] = pulse
    else:
        human['pulse'] = 'Pulse not recorded'
        machine['edenrollchart_pulse'] = '999'
    # O2 SAT
    oxygen_sat = ed.vitals(subject_id, conn, "'SpO2'")
    if oxygen_sat:
        oxygen_sat = min(oxygen_sat, key=min_lab)[2]
        human['Oxgyen Saturation'] = oxygen_sat
        machine['edenrollchart_o2sat'] = oxygen_sat
    else:
        human['Oxgyen Saturation'] = 'O2 Sat not recorded'
        machine['edenrollchart_o2sat'] = '999'

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
    # Find relevant O2 devices
    oxygen_info = ed.vitals(subject_id, conn, "'O2 Device'")

    # Find all oxygen values
    if oxygen_info:
        # Find all oxygen values
        for vital_sign in oxygen_info:
            oxygen = Vitals(*vital_sign)
            if oxygen.value in ('Nasal cannula', 'Non-rebreather mask', 'High flow nasal cannula', 'Simple Facemask',
                                'Trach mask', 'Venturi mask'):
                human['Oxygen Supplmentation in ED'] = "{} Recorded At {}, ".format(oxygen.value, oxygen.date_time)
                machine['edenrollchart_o2supplementanytime'] = 'Yes'
                machine['edenrollchart_o2supplementanytime_route'] = oxygen.value
    else:
        human['Oxygen Supplementation in ED'] = 'Not Oxygen Supplementation was given while in ED'
        machine['edenrollchart_o2supplementanytime'] = 'No'
        machine['edenrollchart_o2supplementinitial'] = 'No'
        machine['edenrollchart_o2supplementleaving'] = 'No'

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
    
    # Function to find minimums
    min_lab = lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
    # PH
    ph = ed.lab(subject_id, conn, "'PH SPECIMEN'")
    if ph:
        ph = min(ph, key=min_lab)[0]
        human['ph'] = ph
        machine['edenrollchart_ph'] = ph
    else:
        human['ph'] = ' Not Done'
        machine['edenrollchart_ph'] = '999'
    # BUN
    bun_compnames = """LabComponentName = 'BLOOD UREA NITROGEN'
                    OR LabComponentName = 'UREA NITROGEN'"""
    bun = ed.lab2(subject_id, conn, bun_compnames)
    if bun:
        bun = min(bun, key=min_lab)[0]
        human['bun'] = bun
        machine['edenrollchart_bun'] = bun
    else:
        human['bun'] = ' Not Done'
        machine['edenrollchart_bun'] = '999'
    # Sodium
    sodium = ed.lab(subject_id, conn, "'SODIUM'")
    if sodium:
        sodium = min(sodium, key=min_lab)[0]
        human['sodium'] = sodium
        machine['edenrollchart_sodium'] = sodium
    else:
        human['sodium'] = ' Not Done'
        machine['edenrollchart_sodium'] = '999'
    # Glucose
    glucose = ed.lab(subject_id, conn, "'GLUCOSE'")
    if glucose:
        glucose = min(glucose, key=min_lab)[0]
        human['glucose'] = glucose
        machine['edenrollchart_glucose'] = glucose
    else:
        human['glucose'] = ' Not Done'
        machine['edenrollchart_glucose'] = '999'
    # Hematocrit
    hematocrit = ed.lab(subject_id, conn, "'HEMATOCRIT'")
    if hematocrit:
        hematocrit = min(hematocrit, key=min_lab)[0]
        human['hematocrit'] = hematocrit
        machine['edenrollchart_hematocrit'] = hematocrit
    else:
        human['hematocrit'] = ' Not Done'
        machine['edenrollchart_hematocrit'] = '999'

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
    # Influenza Testing
    influenza_count = 0
    influenza_compnames = """LabComponentName = 'INFLUENZA A NAT'
                  OR LabComponentName = 'INFLUENZA B NAT'
                  OR LabComponentName = 'INFLUENZA A PCR'
                  OR LabComponentName = 'INFLUENZA B PCR'"""
    influneza_tests = ed.lab2(subject_id, conn, influenza_compnames)
    influenza_testing = defaultdict(str)
    if influneza_tests:
        #Find first test for patien
        machine['edenrollchart_flutest'] = 'Yes'
        unique_influenza_test = defaultdict(dict)
        
        for test_result in influneza_tests:
            influenza_lab = Lab(*test_result)
            if influenza_lab.check_time(dc_time) is True:
                influenza_count += 1
                if influenza_count > 5:
                    break
                result = influenza_lab.value
                test_name = influenza_lab.labname
                result_type = influenza_lab.componentname
                result_time = influenza_lab.date_time
                if result in ('No RNA Detected', 'No DNA Detected'):
                    result = 'negative'
                if result in ('DNA Detected', 'RNA Detected'):
                    result = "{} {}".format(result_type, result)
                result_id = "{}|{}".format(test_name, result_time)
                # Negative Results
                if result == 'negative':
                    if not influenza_testing.get(result_id):
                        influenza_testing[result_id] = result
                        continue
                    if influenza_testing[result_id] != 'negative':
                        continue
                # Positive Results
                if result:
                    if influenza_testing.get(result_id) == 'negative':
                        influenza_testing[result_id] = result
                        continue
                    else:
                        influenza_testing[result_id] += "{}".format(result)
                        continue

        # Write Influenza Results to file
        influenza_count = 0
        for influenza_result_name, influenza_result in influenza_testing.items():
            test_name, order_time = influenza_result_name.split("|")
            test_date, test_time = order_time.split(" ")
            influenza_count += 1
            testing_type = 'pcr'
            if influenza_result == 'negative':
                test_result = 'negative'
            else:
                test_result = 'positive'
                machine['edenrollchart_flutest{}_typing'.format(influenza_count)] = 'Yes'
                machine['edenrollchart_flutest{}_typing_specify'.format(influenza_count)] = influenza_result.split(" ")[1]

            human[influenza_result_name] = influenza_result
            machine['edenrollchart_flutest{}_name'.format(influenza_count)] = test_name
            machine['edenrollchart_flutest{}_type'.format(influenza_count)] = testing_type
            machine['edenrollchart_flutest{}_result'.format(influenza_count)] = test_result
            machine['edenrollchart_flutest{}_resultdate'.format(influenza_count)] = test_date
            machine['edenrollchart_flutest{}_resulttime'.format(influenza_count)] = test_time

            # Record Number of Influenza Test Done
        machine['edenrollchart_numberflutests'] = influenza_count
    else:
        human['Influenza Testing'] = 'No Influenza Testing Done'
        machine['edenrollchart_flutest'] = 'No'

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
    # Other Virus Testing
    othervirus_compnames = """LabComponentName = 'PARAINFLUENZAE 3 NAT'
                  OR LabComponentName = 'ADENOVIRUS NAT'
                  OR LabComponentName = 'RHINOVIRUS NAT'
                  OR LabComponentName = 'PARAINFLUENZAE 2 NAT'
                  OR LabComponentName = 'METAPNEUMO NAT'
                  OR LabComponentName = 'RSV NAT'
                  OR LabComponentName = 'ADENOVIRUS PCR'
                  OR LabComponentName = 'RHINOVIRUS PCR'
                  OR LabComponentName = 'PARAINFLUENZAE 2 PCR'
                  OR LabComponentName = 'METAPNEUMOVIRUS PCR'
                  OR LabComponentName = 'RSV PCR'"""
    other_virus_tests = ed.lab2(subject_id, conn, othervirus_compnames)
    if other_virus_tests:
        machine['edenrollchart_otherrespviruses'] = 'Yes'
    
        othervirus_testing = defaultdict(str)
        for test_result in other_virus_tests:
            othervirus_lab = Lab(*test_result)
            if othervirus_lab.check_time(dc_time) is True:
                result = othervirus_lab.value
                result_time = othervirus_lab.date_time
                result_type = othervirus_lab.componentname
                if result in ('No RNA Detected', 'No DNA Detected'):
                    result = 'negative'
                if result in ('DNA Detected', 'RNA Detected'):
                    result = result_type + " {}".format(result)
                result_id = "{}|{}".format(result_type, result_time)
                # Negative Results
                if result == 'negative':
                    if not othervirus_testing.get(result_id):
                        othervirus_testing[result_id] = result
                        continue
                    if othervirus_testing[result_id] != 'negative':
                        continue
                # Positive Results
                if result:
                    if othervirus_testing.get(result_id) == 'negative':
                        othervirus_testing[result_id] = result
                        continue
                    else:
                        othervirus_testing[result_id] += " {}".format(result)
                        continue

        # Write Other Virus Tested Results to file
        for othervirus_result_name, othervirus_result in othervirus_testing.items():
            human[othervirus_result_name] = othervirus_result
            test_name, order_time = othervirus_result_name.split("|")
            machine_link = {'RSV NAT': 'edenrollchart_rsv',
                            'RHINOVIRUS NAT': 'edenrollchart_rhinovirus',
                            'ADENOVIRUS NAT': 'edenrollchart_adenovirus',
                            'PARAINFLUENZAE 3 NAT': 'edenrollchart_parainfluenza',
                            'PARAINFLUENZAE 2 NAT': 'edenrollchart_parainfluenza',
                            'METAPNEUMO NAT': 'edenrollchart_metapneumovirus',
                            'RSV PCR': 'edenrollchart_rsv',
                            'RHINOVIRUS PCR': 'edenrollchart_rhinovirus',
                            'ADENOVIRUS PCR': 'edenrollchart_adenovirus',
                            'PARAINFLUENZAE 3 PCR': 'edenrollchart_parainfluenza',
                            'PARAINFLUENZAE 2 PCR': 'edenrollchart_parainfluenza',
                            'METAPNEUMOVIRUS PCR': 'edenrollchart_metapneumovirus'
                            }
            machine[machine_link[test_name]] = othervirus_result
    else:
        human['Other Virus Tested'] = 'Not tested for Other Viruses'
        machine['edenrollchart_otherrespviruses'] = 'No'

    return human, machine


def get_micro_info(human, machine, subject_id, conn, dc_time):
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
    # Microbiology
    micro_test_num = 0
    searchtext = "'%CULT%'"
    micro_tests = ed.lab3(subject_id, conn, searchtext)
    if micro_tests:
        for micro_test in micro_tests:
            micro_lab = Lab(*micro_test)
            if micro_lab.check_time(dc_time) is True:
                result = micro_lab.value
                result_time = micro_lab.date_time
                test_name = micro_lab.labname
                result_id = "{}|{}".format(test_name, result_time)
                if result and result != "No growth" and result.find("Negative") == -1 and result.find("No "):
                    micro_test_num += 1
                    if micro_test_num > 5:
                        break
                    human['Culture # {} with a non-negative result {}'.format(micro_test_num, result_id)] = result

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
    # ED Antivirals
    ed_antiviral_count = 0
    ed_antivirals = ed.medication2(
        subject_id, conn, "'ANTIVIRALS'")
    if ed_antivirals:

        for antiviral in ed_antivirals:
            antiviral_lab = Medication2(*antiviral)
            if antiviral_lab.check_time(dc_time) is True:
                ed_antiviral_count += 1
                if ed_antiviral_count > 2:
                    break
                machine['edenrollchart_antiviral'] = 'Yes'
                # Record number of Antivrals
                machine['edenrollchart_numberantivirals'] = ed_antiviral_count
                med_name = antiviral_lab.name.split(" ")[0]
                order_date_time = antiviral_lab.date_time
                order_date, order_time = order_date_time.split(" ")
                med_route = antiviral_lab.route
                human["ED Antiviral #{}".format(
                    ed_antiviral_count)] = "{} {}".format(
                    med_name, med_route)
                machine['edenrollchart_antiviral{}_name'.format(
                    ed_antiviral_count)] = med_name
                machine['edenrollchart_antiviral{}_route'.format(
                    ed_antiviral_count)] = med_route
                machine['edenrollchart_antiviral{}_date'.format(
                    ed_antiviral_count)] = order_date
                machine['edenrollchart_antiviral{}_time'.format(
                    ed_antiviral_count)] = order_time
    else:
        human['ED Antivirals'] = 'No antivirals given in the ED'
        machine['edenrollchart_antiviral'] = 'No'

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
        machine['edenrollchart_antiviraldischarge'] = 'NA subject not discharged'
        return human, machine

    # Discharge Antivirals
    discharge_antiviral_count = 0
    discharge_antivirals = ed.medication(
        subject_id, conn, "'ANTIVIRALS'", "'Outpatient'")
    if discharge_antivirals:
        machine['edenrollchart_antiviraldischarge'] = 'Yes'
        for antiviral in discharge_antivirals:
            dc_antiviral_lab = Medication(*antiviral)
            if dc_antiviral_lab.check_time(dc_time) is True:
                discharge_antiviral_count += 1
                if discharge_antiviral_count > 2:
                    break
                med_name = dc_antiviral_lab.name.split(" ")[0]
                med_route = dc_antiviral_lab.route
                human[
                    "Discharge Antiviral #{}".format(
                        discharge_antiviral_count)] = "{} {}".format(
                    med_name, med_route)
                machine['edenrollchart_antiviraldischarge{}'.format(
                    discharge_antiviral_count)] = med_name
        # Record number of Dishcarged Antivirals
        machine['edenrollchart_numberantiviralsdischarge'] = discharge_antiviral_count
    else:
        human['Discharged Antiviral'] = 'No antivirals given at Discharge'
        machine['edenrollchart_antiviraldischarge'] = 'No'

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
    # ED Antibiotics
    ed_antibiotics_count = 0
    ed_antibiotics = ed.medication2(
        subject_id, conn, "'ANTIBIOTICS'")
    if ed_antibiotics:

        for antibiotic in ed_antibiotics:
            abx_med = Medication2(*antibiotic)
            if abx_med.check_time(dc_time) is True:
                # Record number of ED Antibiotics
                ed_antibiotics_count += 1
                if ed_antibiotics_count > 5:
                    break
                machine['edenrollchart_antibiotic'] = 'Yes'
                machine['edenrollchart_numberantibiotics'] = ed_antibiotics_count
                med_name = abx_med.name.split(" ")[0]
                order_date_time = abx_med.date_time
                order_date, order_time = order_date_time.split(" ")
                med_route = abx_med.route
                human["ED Antibiotics #{}".format(
                        ed_antibiotics_count)] = "{} {} {} {}".format(
                        med_name, med_route, order_date, order_time)
                machine['edenrollchart_antibiotic{}_name'.format(
                        ed_antibiotics_count)] = med_name
                machine['edenrollchart_antibiotic{}_date'.format(
                        ed_antibiotics_count)] = order_date
                machine['edenrollchart_antibiotic{}_time'.format(
                        ed_antibiotics_count)] = order_time
                machine['edenrollchart_antibiotic{}_route'.format(
                        ed_antibiotics_count)] = med_route


    else:
        human['ED Antibiotics' ] = 'No antibiotics given in the ED'
        machine['edenrollchart_antibiotic'] = 'No'

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
        machine['edenrollchart_antibioticdischarge'] = 'NA subject not discharged'
        return human, machine
    # Discharge Antibiotics
    discharge_antibiotics_count = 0
    discharge_antibiotics = ed.medication(
        subject_id, conn, "'ANTIBIOTICS'", "'Outpatient'")
    if discharge_antibiotics:
        machine['edenrollchart_antibioticdischarge'] = 'Yes'
        for antibiotic in discharge_antibiotics:
            dc_abx_med = Medication(*antibiotic)
            if dc_abx_med.check_time(dc_time) is True:
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
                machine['edenrollchart_antibioticdischarge{}_name'.format(
                        discharge_antibiotics_count)] = med_name
        # Record number of Discharge Abx
        machine['edenrollchart_numberantibioticsdischarge'] = discharge_antibiotics_count
    else:
        human['Discharge Antibiotics'] = 'No antibiotics given at discharge'
        machine['edenrollchart_antibioticdischarge'] = 'No'

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
    # Chest Imaging
    chest_xray_ct = ed.chest_imaging(subject_id, conn)
    if chest_xray_ct:
        chest_xray_ct = [Imaging(*item) for item in chest_xray_ct]
        human["Chest Imaging"] = chest_xray_ct[0].name
        machine['edenrollchart_chestimaging'] = 'Yes'
    else:
        human['Chest Imagine'] = 'No chest imaging ordered in the ED'
        machine['edenrollchart_chestimaging'] = 'No'

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

    #Initial all values to be no
    machine['edenrollchart_dxinfluenza'] = 'No'
    machine['edenrollchart_dxviralsyndrome'] = 'No'
    machine['edenrollchart_dxpneumonia'] = 'No'
    machine['edenrollchart_dxmyocardialinfarction'] = 'No'
    machine['edenrollchart_dxstroke'] = 'No'

    # Final Diagnoses
    diagnosis_count = 0
    diagnoses = ed.final_diagnoses(subject_id, conn)
    human['Diagnoses'] = diagnoses
    for diagnosis in diagnoses:
        diagnosis_count += 1
        # Record Diagnosis Number
        machine['edenrollchart_numberdx'] = diagnosis_count
        if diagnosis_count > 3:
            machine['edenrollchart_numberdx'] = 'More than three'
            break
        machine['edenrollchart_dx{}'.format(diagnosis_count)] = diagnosis[0]
        if diagnosis[0].lower().find('influenza') != -1:
            machine['edenrollchart_dxinfluenza'] = 'Yes'
        if diagnosis[0].lower().find('viral syndrome') != -1 or diagnosis[0].lower().find('viral infection') != -1:
            machine['edenrollchart_dxviralsyndrome'] = 'Yes'
        if diagnosis[0].lower().find('pneumonia') != -1:
            machine['edenrollchart_dxpneumonia'] = 'Yes'
        if diagnosis[0].lower().find('myocardial infarction') != -1:
            machine['edenrollchart_dxmyocardialinfarction'] = 'Yes'
        if diagnosis[0].lower().find('stroke') != -1:
            machine['edenrollchart_dxstroke'] = 'Yes'

    return human, machine