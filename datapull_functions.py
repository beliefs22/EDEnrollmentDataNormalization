import datapull_sql as ed
from datapullclasses import ADT, Vitals, Lab, Medication, Medication2, Imaging
from collections import defaultdict
from datetime import datetime


def get_arrival_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects arrival info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """

    arrival_info = ADT(*ed.arrival_date_time(subject_id, conn))
    coordinator['Arrival Date'] = arrival_info.date
    coordinator['Arrival Time'] = arrival_info.time
    redcap_label['edenrollchart_arrivaldate'] = arrival_info.date
    redcap_label['edenrollchart_arrivaltime'] = arrival_info.time[:5]
    redcap_raw['edenrollchart_arrivaldate'] = arrival_info.date
    redcap_raw['edenrollchart_arrivaltime'] = arrival_info.time[:5]

    return coordinator, redcap_label, redcap_raw


def get_discharge_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects discharge info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    discharge_info = ADT(*ed.discharge_date_time(subject_id, conn))
    coordinator['Discharge Date'] = discharge_info.date
    coordinator['Discharge Time'] = discharge_info.time
    redcap_label['edenrollchart_departtime'] = discharge_info.time[:5]
    redcap_label['edenrollchart_departdate'] = discharge_info.date
    redcap_raw['edenrollchart_departtime'] = discharge_info.time[:5]
    redcap_raw['edenrollchart_departdate'] = discharge_info.date

    return coordinator, redcap_label, redcap_raw


def get_dispo_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects disposition info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    dispo_info = ADT(*ed.arrival_date_time(subject_id, conn))
    coordinator['Disposition'] = dispo_info.dispo
    if dispo_info.dispo == "Discharge":
        redcap_label['edenrollchart_dispo'] = dispo_info.dispo
        redcap_raw['edenrollchart_dispo'] = '2'
        return coordinator, redcap_label, redcap_raw
    if dispo_info.dispo == "Hospitalized Observation":
        redcap_label['edenrollchart_dispo'] = 'Admit'
        redcap_raw['edenrollchart_dispo'] = '1'
        redcap_label['edenrollchart_observation'] = 'Yes'
        redcap_raw['edenrollchart_observation'] = '1'
        return coordinator, redcap_label, redcap_raw
    if dispo_info.dispo == 'Eloped':
        redcap_label['edenrollchart_dispo'] = dispo_info.dispo
        redcap_raw['edenrollchart_dispo'] = "3"
        return coordinator, redcap_label, redcap_raw
    if dispo_info.dispo == 'Admit':
        redcap_label['edenrollchart_dispo'] = dispo_info.dispo
        redcap_raw['edenrollchart_dispo'] = "1"
        return coordinator, redcap_label, redcap_raw

    redcap_label['edenrollchart_dispo'] = 'Other'
    redcap_label['edenrollchart_dispo_specify'] = dispo_info.dispo
    redcap_raw['edenrollchart_dispo'] = '4'
    redcap_raw['edenrollchart_dispo_specify'] = dispo_info.dispo

    return coordinator, redcap_label, redcap_raw


def get_vitals_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects vitals info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    # Function to find minimums
    min_lab = lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')

    # Temp
    temp = ed.vitals(subject_id, conn, "'Temp'")
    if temp:
        temp = min(temp, key=min_lab)[2]
        coordinator['temp'] = temp
        redcap_label['edenrollchart_temperature'] = temp
        redcap_raw['edenrollchart_temperature'] = temp
    else:
        coordinator['temp'] = 'Temperature not recorded'
        redcap_label['edenrollchart_temperature'] = 'Not Recorded'
        redcap_raw['edenrollchart_temperature'] = '999'


    # Resp
    resp = ed.vitals(subject_id, conn, "'Resp'")
    if resp:
        resp = min(resp, key=min_lab)[2]
        coordinator['resp'] = resp
        redcap_label['edenrollchart_respiratoryrate'] = resp
        redcap_raw['edenrollchart_respiratoryrate'] = resp
    else:
        coordinator['resp'] = 'Respirations not recorded'
        redcap_label['edenrollchart_respiratoryrate'] = 'Not Recorded'
        redcap_raw['edenrollchart_respiratoryrate'] = '999'
    # Blood Pressure
    bp = ed.vitals(subject_id, conn, "'BP'")
    if bp:
        bp = min(bp, key=min_lab)[2]
        bp = bp.split("/")[0]
        coordinator['bp'] = bp
        redcap_label['edenrollchart_systolicbloodpressure'] = bp
        redcap_raw['edenrollchart_systolicbloodpressure'] = bp
    else:
        coordinator['bp'] = 'Blood Pressure not recorded'
        redcap_label['edenrollchart_systolicbloodpressure'] = 'Not Recorded'
        redcap_raw['edenrollchart_systolicbloodpressure'] = '999'
    # Pulse
    pulse = ed.vitals(subject_id, conn, "'Pulse'")
    if pulse:
        pulse = min(pulse, key=min_lab)[2]
        coordinator['pulse'] = pulse
        redcap_label['edenrollchart_pulse'] = pulse
        redcap_raw['edenrollchart_pulse'] = pulse
    else:
        coordinator['pulse'] = 'Pulse not recorded'
        redcap_label['edenrollchart_pulse'] = 'Not Recorded'
        redcap_raw['edenrollchart_pulse'] = '999'
    # O2 SAT
    oxygen_sat = ed.vitals(subject_id, conn, "'SpO2'")
    if oxygen_sat:
        oxygen_sat = min(oxygen_sat, key=min_lab)[2]
        coordinator['Oxgyen Saturation'] = oxygen_sat
        redcap_label['edenrollchart_o2sat'] = oxygen_sat
        redcap_raw['edenrollchart_o2sat'] = oxygen_sat
    else:
        coordinator['Oxgyen Saturation'] = 'O2 Sat not recorded'
        redcap_label['edenrollchart_o2sat'] = 'Not Recorded'
        redcap_raw['edenrollchart_o2sat'] = '999'

    return coordinator, redcap_label, redcap_raw


def get_oxygen_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects oxygen info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    # Find relevant O2 devices
    oxygen_info = ed.vitals(subject_id, conn, "'O2 Device'")
    oxygen_type_codes = {'Nasal cannula' : "1",
                         'High flow nasal cannula' : '1',
                         'Non-rebreather mask' : '2',
                         'Simple Facemask' : '2',
                        'Trach mask' : '2',
                         'Venturi mask' : '2',
                         'BiPAP' : '3',
                         'CPAP' : '3'
                         }

    # Find all oxygen values
    if oxygen_info:
        # Find all oxygen values
        for vital_sign in oxygen_info:
            oxygen = Vitals(*vital_sign)
            if oxygen.value in ('Nasal cannula', 'Non-rebreather mask', 'High flow nasal cannula', 'Simple Facemask',
                                'Trach mask', 'Venturi mask'):
                coordinator['Oxygen Supplmentation in ED'] = "{} Recorded At {}, ".format(oxygen.value, oxygen.date_time)
                redcap_label['edenrollchart_o2supplementanytime'] = 'Yes'
                redcap_label['edenrollchart_o2supplementanytime_route'] = oxygen.value

                redcap_raw['edenrollchart_o2supplementanytime'] = '1'
                redcap_raw['edenrollchart_o2supplementanytime_route'] = oxygen_type_codes[oxygen.value]
    else:
        coordinator['Oxygen Supplementation in ED'] = 'Not Oxygen Supplementation was given while in ED'
        redcap_label['edenrollchart_o2supplementanytime'] = 'No'
        redcap_label['edenrollchart_o2supplementinitial'] = 'No'
        redcap_label['edenrollchart_o2supplementleaving'] = 'No'

        redcap_label['edenrollchart_o2supplementanytime'] = '0'
        redcap_label['edenrollchart_o2supplementinitial'] = '0'
        redcap_label['edenrollchart_o2supplementleaving'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_lab_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects arrival info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """

    # Function to find minimums
    min_lab = lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')
    # PH
    ph = ed.lab(subject_id, conn, "'PH SPECIMEN'")
    if ph and min(ph, key=min_lab)[0] != 'see below':
        ph = min(ph, key=min_lab)[0]
        coordinator['ph'] = ph
        redcap_label['edenrollchart_ph'] = ph
        redcap_raw['edenrollchart_ph'] = ph
    else:
        coordinator['ph'] = ' Not Done'
        redcap_label['edenrollchart_ph'] = 'Not Done'
        redcap_raw['edenrollchart_ph'] = '999'
    # BUN
    bun_compnames = """LabComponentName = 'BLOOD UREA NITROGEN'
                    OR LabComponentName = 'UREA NITROGEN'"""
    bun = ed.lab2(subject_id, conn, bun_compnames)
    if bun and min(bun, key=min_lab)[0] != 'see below':
        bun = min(bun, key=min_lab)[0]
        coordinator['bun'] = bun
        redcap_label['edenrollchart_bun'] = bun
        redcap_raw['edenrollchart_bun'] = bun
    else:
        coordinator['bun'] = ' Not Done'
        redcap_label['edenrollchart_bun'] = 'Not Done'
        redcap_raw['edenrollchart_bun'] = '999'
    # Sodium
    sodium = ed.lab(subject_id, conn, "'SODIUM'")
    if sodium and min(sodium, key=min_lab)[0] != 'see below':
        sodium = min(sodium, key=min_lab)[0]
        coordinator['sodium'] = sodium
        redcap_label['edenrollchart_sodium'] = sodium
        redcap_raw['edenrollchart_sodium'] = sodium
    else:
        coordinator['sodium'] = ' Not Done'
        redcap_label['edenrollchart_sodium'] = 'Not Done'
        redcap_raw['edenrollchart_sodium'] = '999'
    # Glucose
    glucose = ed.lab(subject_id, conn, "'GLUCOSE'")
    if glucose and min(glucose, key=min_lab)[0] != 'see below':
        glucose = min(glucose, key=min_lab)[0]
        coordinator['glucose'] = glucose
        redcap_label['edenrollchart_glucose'] = glucose
        redcap_raw['edenrollchart_glucose'] = glucose
    else:
        coordinator['glucose'] = ' Not Done'
        redcap_label['edenrollchart_glucose'] = 'Not Done'
        redcap_raw['edenrollchart_glucose'] = '999'
    # Hematocrit
    hematocrit = ed.lab(subject_id, conn, "'HEMATOCRIT'")
    if hematocrit and min(hematocrit, key=min_lab)[0] != 'see below':
        hematocrit = min(hematocrit, key=min_lab)[0]
        coordinator['hematocrit'] = hematocrit
        redcap_label['edenrollchart_hematocrit'] = hematocrit
        redcap_raw['edenrollchart_hematocrit'] = hematocrit
    else:
        coordinator['hematocrit'] = ' Not Done'
        redcap_label['edenrollchart_hematocrit'] = 'Not Done'
        redcap_raw['edenrollchart_hematocrit'] = '999'

    return coordinator, redcap_label, redcap_raw


def get_flutesting_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time):
    """Stores subjects flu testing info in dictionaies to use for file writing
    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
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


        for test_result in influneza_tests:
            influenza_lab = Lab(*test_result)
            if influenza_lab.check_time(dc_time) is True:
                influenza_count += 1
                if influenza_count < 5:
                    # Find first test for patient
                    redcap_label['edenrollchart_flutest'] = 'Yes'
                    redcap_raw['edenrollchart_flutest'] = '1'
                    # Record Number of Influenza Test Done
                    redcap_label['edenrollchart_numberflutests'] = influenza_count
                    redcap_raw['edenrollchart_numberflutests'] = influenza_count
                if influenza_count >= 5:
                    break
                result = influenza_lab.value
                test_name = influenza_lab.labname
                result_type = influenza_lab.componentname
                collect_time = influenza_lab.collect_date_time
                result_time = influenza_lab.result_date_time
                if result in ('No RNA Detected', 'No DNA Detected'):
                    result = 'negative'
                if result in ('DNA Detected', 'RNA Detected'):
                    result = "{} {}".format(result_type, result)
                result_id = "{}|{}|{}".format(test_name, collect_time, result_time)
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
            test_name, collect_info, result_info = influenza_result_name.split("|")
            collect_date, collect_time = collect_info.split(" ")
            result_date, result_time = result_info.split(" ")
            influenza_count += 1
            testing_type = 'pcr'
            if influenza_result == 'negative':
                test_result = 'negative'
                redcap_label['edenrollchart_flutest{}_result'.format(influenza_count)] = 'Negative'
                redcap_raw['edenrollchart_flutest{}_result'.format(influenza_count)] = '1'
            else:
                test_result = 'positive'
                redcap_label['edenrollchart_flutest{}_typing'.format(influenza_count)] = 'Yes'
                redcap_label['edenrollchart_flutest{}_typing_specify'.format(influenza_count)] = influenza_result.split(" ")[1]
                redcap_label['edenrollchart_flutest{}_result'.format(influenza_count)] = 'Positive'

                redcap_raw['edenrollchart_flutest{}_typing'.format(influenza_count)] = '1'
                redcap_raw['edenrollchart_flutest{}_typing_specify'.format(influenza_count)] = influenza_result.split(" ")[1]
                redcap_raw['edenrollchart_flutest{}_result'.format(influenza_count)] = '2'

            coordinator[influenza_result_name] = influenza_result
            redcap_label['edenrollchart_flutest{}_name'.format(influenza_count)] = test_name
            redcap_label['edenrollchart_flutest{}_type'.format(influenza_count)] = testing_type
            redcap_label['edenrollchart_flutest{}_collectiondate'.format(influenza_count)] = collect_date
            redcap_label['edenrollchart_flutest{}_collectiontime'.format(influenza_count)] = collect_time[:5]
            redcap_label['edenrollchart_flutest{}_resultdate'.format(influenza_count)] = result_date
            redcap_label['edenrollchart_flutest{}_resulttime'.format(influenza_count)] = result_time[:5]

            redcap_raw['edenrollchart_flutest{}_name'.format(influenza_count)] = test_name
            redcap_raw['edenrollchart_flutest{}_type'.format(influenza_count)] = '1'
            redcap_raw['edenrollchart_flutest{}_collectiondate'.format(influenza_count)] = collect_date
            redcap_raw['edenrollchart_flutest{}_collectiontime'.format(influenza_count)] = collect_time[:5]
            redcap_raw['edenrollchart_flutest{}_resultdate'.format(influenza_count)] = result_date
            redcap_raw['edenrollchart_flutest{}_resulttime'.format(influenza_count)] = result_time[:5]

    else:
        coordinator['Influenza Testing'] = 'No Influenza Testing Done'
        redcap_label['edenrollchart_flutest'] = 'No'
        redcap_raw['edenrollchart_flutest'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_othervir_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time):
    """Stores subjects other virus info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
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
        othervirus_testing = defaultdict(str)
        for test_result in other_virus_tests:
            othervirus_lab = Lab(*test_result)
            if othervirus_lab.check_time(dc_time) is True:
                redcap_label['edenrollchart_otherrespviruses'] = 'Yes'
                redcap_raw['edenrollchart_otherrespviruses'] = '1'
                result = othervirus_lab.value
                collect_time = othervirus_lab.collect_date_time
                result_type = othervirus_lab.componentname
                if result in ('No RNA Detected', 'No DNA Detected'):
                    result = 'negative'
                if result in ('DNA Detected', 'RNA Detected'):
                    result = result_type + " {}".format(result)
                result_id = "{}|{}".format(result_type, collect_time)
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
            coordinator[othervirus_result_name] = othervirus_result
            test_name, order_time = othervirus_result_name.split("|")
            redcap_label_link = {'RSV NAT': 'edenrollchart_rsv',
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
            if othervirus_result == 'negative':
                redcap_label[redcap_label_link[test_name]] = 'Negative'
                redcap_raw[redcap_label_link[test_name]] = '0'
            if othervirus_result == 'positive':
                redcap_label[redcap_label_link[test_name]] = 'Positive'
                redcap_raw[redcap_label_link[test_name]] = '1'
    else:
        coordinator['Other Virus Tested'] = 'Not tested for Other Viruses'
        redcap_label['edenrollchart_otherrespviruses'] = 'No'
        redcap_raw['edenrollchart_otherrespviruses'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_antiviral_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time):
    """Stores subjects antiviral info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    # ED Antivirals
    ed_antiviral_count = 0
    ed_antivirals = ed.medication2(
        subject_id, conn, "'ANTIVIRALS'")
    if ed_antivirals:
        med_route_codes = {'IV' : '3',
                           'Intravenous' : '3',
                           'Oral' : '1',
                           'PO' : '1',
                           'IM' : '2',
                           'Intramuscular' : '2'
                           }

        for antiviral in ed_antivirals:
            antiviral_lab = Medication2(*antiviral)
            med_route = antiviral_lab.route
            #Skip meds without proper routes and give after dishcarge from the ED
            if antiviral_lab.check_time(dc_time) is True and med_route_codes.get(med_route):
                ed_antiviral_count += 1
                if ed_antiviral_count < 3:
                    redcap_label['edenrollchart_antiviral'] = 'Yes'
                    redcap_raw['edenrollchart_antiviral'] = '1'
                    # Record number of Antivrals
                    redcap_label['edenrollchart_numberantivirals'] = ed_antiviral_count
                    redcap_raw['edenrollchart_numberantivirals'] = ed_antiviral_count
                if ed_antiviral_count >= 3:
                    break

                med_name = antiviral_lab.name.split(" ")[0]
                order_date_time = antiviral_lab.date_time
                order_date, order_time = order_date_time.split(" ")
                coordinator["ED Antiviral #{}".format(
                    ed_antiviral_count)] = "{} {}".format(med_name, med_route)
                redcap_label['edenrollchart_antiviral{}_name'.format(ed_antiviral_count)] = med_name
                redcap_label['edenrollchart_antiviral{}_route'.format(ed_antiviral_count)] = med_route
                redcap_label['edenrollchart_antiviral{}_date'.format(ed_antiviral_count)] = order_date
                redcap_label['edenrollchart_antiviral{}_time'.format(ed_antiviral_count)] = order_time[:5]

                redcap_raw['edenrollchart_antiviral{}_name'.format(ed_antiviral_count)] = med_name
                redcap_raw['edenrollchart_antiviral{}_route'.format(ed_antiviral_count)] = med_route_codes[med_route]
                redcap_raw['edenrollchart_antiviral{}_date'.format(ed_antiviral_count)] = order_date
                redcap_raw['edenrollchart_antiviral{}_time'.format(ed_antiviral_count)] = order_time[:5]
    else:
        coordinator['ED Antivirals'] = 'No antivirals given in the ED'
        redcap_label['edenrollchart_antiviral'] = 'No'
        redcap_raw['edenrollchart_antiviral'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_dc_antiviral_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time, dispo):
    """Stores subjects discharge antiviral info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time
        dispo (str): subjects final disposition

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    if dispo != "Discharge":
        redcap_label['edenrollchart_antiviraldischarge'] = 'NA subject not discharged'
        redcap_raw['edenrollchart_antiviraldischarge'] = '97'
        return coordinator, redcap_label, redcap_raw

    # Discharge Antivirals
    discharge_antiviral_count = 0
    discharge_antivirals = ed.medication(
        subject_id, conn, "'ANTIVIRALS'", "'Outpatient'")
    if discharge_antivirals:

        for antiviral in discharge_antivirals:
            dc_antiviral_lab = Medication(*antiviral)
            if dc_antiviral_lab.check_time(dc_time) is True:
                discharge_antiviral_count += 1
                if discharge_antiviral_count < 3:
                    redcap_label['edenrollchart_antiviraldischarge'] = 'Yes'
                    redcap_raw['edenrollchart_antiviraldischarge'] = '1'
                    # Record number of Dishcarged Antivirals
                    redcap_label['edenrollchart_numberantiviralsdischarge'] = discharge_antiviral_count
                    redcap_raw['edenrollchart_numberantiviralsdischarge'] = discharge_antiviral_count
                if discharge_antiviral_count >= 3:
                    break
                med_name = dc_antiviral_lab.name.split(" ")[0]
                med_route = dc_antiviral_lab.route
                coordinator["Discharge Antiviral #{}".format(discharge_antiviral_count)] = "{} {}".format(
                    med_name, med_route)
                redcap_label['edenrollchart_antiviraldischarge{}'.format(discharge_antiviral_count)] = med_name
                redcap_raw['edenrollchart_antiviraldischarge{}'.format(discharge_antiviral_count)] = med_name

    else:
        coordinator['Discharged Antiviral'] = 'No antivirals given at Discharge'
        redcap_label['edenrollchart_antiviraldischarge'] = 'No'
        redcap_raw['edenrollchart_antiviraldischarge'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_antibiotic_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time):
    """Stores subjects antibiotic info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    # ED Antibiotics
    ed_antibiotics_count = 0
    ed_antibiotics = ed.medication2(
        subject_id, conn, "'ANTIBIOTICS'")
    if ed_antibiotics:
        med_route_codes = {'IV' : '3',
                           'Intravenous' : '3',
                           'Oral' : '1',
                           'PO' : '1',
                           'IM' : '2',
                           'Intramuscular' : '2'
                           }

        for antibiotic in ed_antibiotics:
            abx_med = Medication2(*antibiotic)
            med_route = abx_med.route
            if abx_med.check_time(dc_time) is True and med_route_codes.get(med_route):
                # Record number of ED Antibiotics
                ed_antibiotics_count += 1
                if ed_antibiotics_count < 5:
                    redcap_label['edenrollchart_antibiotic'] = 'Yes'
                    redcap_label['edenrollchart_numberantibiotics'] = ed_antibiotics_count
                    redcap_raw['edenrollchart_antibiotic'] = '1'
                    redcap_raw['edenrollchart_numberantibiotics'] = ed_antibiotics_count
                if ed_antibiotics_count >= 5:
                    break

                med_name = abx_med.name.split(" ")[0]
                order_date_time = abx_med.date_time
                order_date, order_time = order_date_time.split(" ")
                coordinator["ED Antibiotics #{}".format( ed_antibiotics_count)] = "{} {} {} {}".format(
                    med_name, med_route, order_date, order_time)
                redcap_label['edenrollchart_antibiotic{}_name'.format(ed_antibiotics_count)] = med_name
                redcap_label['edenrollchart_antibiotic{}_date'.format(ed_antibiotics_count)] = order_date
                redcap_label['edenrollchart_antibiotic{}_time'.format(ed_antibiotics_count)] = order_time[:5]
                redcap_label['edenrollchart_antibiotic{}_route'.format(ed_antibiotics_count)] = med_route

                redcap_raw['edenrollchart_antibiotic{}_name'.format(ed_antibiotics_count)] = med_name
                redcap_raw['edenrollchart_antibiotic{}_date'.format(ed_antibiotics_count)] = order_date
                redcap_raw['edenrollchart_antibiotic{}_time'.format(ed_antibiotics_count)] = order_time[:5]
                redcap_raw['edenrollchart_antibiotic{}_route'.format(ed_antibiotics_count)] = med_route_codes[med_route]
    else:
        coordinator['ED Antibiotics' ] = 'No antibiotics given in the ED'
        redcap_label['edenrollchart_antibiotic'] = 'No'
        redcap_raw['edenrollchart_antibiotic'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_dc_abx_info(coordinator, redcap_label, redcap_raw, subject_id, conn, dc_time, dispo):
    """Stores subjects discharge antibiotic info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
        dc_time (str): subjects discharge time
        dispo (str): subjects final disposition

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """

    if dispo != "Discharge":
        redcap_label['edenrollchart_antibioticdischarge'] = 'NA subject not discharged'
        redcap_raw['edenrollchart_antibioticdischarge'] = '98'
        return coordinator, redcap_label, redcap_raw
    # Discharge Antibiotics
    discharge_antibiotics_count = 0
    discharge_antibiotics = ed.medication(
        subject_id, conn, "'ANTIBIOTICS'", "'Outpatient'")
    if discharge_antibiotics:

        for antibiotic in discharge_antibiotics:
            dc_abx_med = Medication(*antibiotic)
            if dc_abx_med.check_time(dc_time) is True:
                discharge_antibiotics_count += 1
                if discharge_antibiotics_count < 3:
                    redcap_label['edenrollchart_antibioticdischarge'] = 'Yes'
                    redcap_raw['edenrollchart_antibioticdischarge'] = '1'
                    # Record number of Discharge Abx
                    redcap_label['edenrollchart_numberantibioticsdischarge'] = discharge_antibiotics_count
                    redcap_raw['edenrollchart_numberantibioticsdischarge'] = discharge_antibiotics_count
                if discharge_antibiotics_count >= 3:
                    break
                med_name = dc_abx_med.name.split(" ")[0]
                time_ordered = dc_abx_med.date_time
                med_route = dc_abx_med.route
                coordinator["Discharge Antibiotics #{}".format(discharge_antibiotics_count)] = "{} {} {}".format(
                    med_name, med_route, time_ordered)
                redcap_label['edenrollchart_antibioticdischarge{}_name'.format(discharge_antibiotics_count)] = med_name
                redcap_raw['edenrollchart_antibioticdischarge{}_name'.format(discharge_antibiotics_count)] = med_name

    else:
        coordinator['Discharge Antibiotics'] = 'No antibiotics given at discharge'
        redcap_label['edenrollchart_antibioticdischarge'] = 'No'
        redcap_raw['edenrollchart_antibioticdischarge'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_imaging_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects imaging info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
            to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """
    # Chest Imaging
    chest_xray_ct = ed.chest_imaging(subject_id, conn)
    if chest_xray_ct:
        chest_xray_ct = [Imaging(*item) for item in chest_xray_ct]
        coordinator["Chest Imaging"] = chest_xray_ct[0].name
        redcap_label['edenrollchart_chestimaging'] = 'Yes'
        redcap_raw['edenrollchart_chestimaging'] = '1'
    else:
        coordinator['Chest Imagine'] = 'No chest imaging ordered in the ED'
        redcap_label['edenrollchart_chestimaging'] = 'No'
        redcap_raw['edenrollchart_chestimaging'] = '0'

    return coordinator, redcap_label, redcap_raw


def get_diagnosis_info(coordinator, redcap_label, redcap_raw, subject_id, conn):
    """Stores subjects diagnosis info in dictionaies to use for file
    writing

    Args:
        coordinator (:obj: `OrderedDefaultDict`): collection of coordinator readable data
        to write to file
        redcap_label (:obj: `OrderedDefaultDict`): collection of redcap_label readable
        data to write to file
        redcap_raw (:obj: `OrderedDefaultDict`): collection of redcap_raw machine readable data to write to file
        subject_id (str): id of subject
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        :obj: `OrderedDefaultDict`):
        returns two ordered default dictionaries - coordinator and redcap_label that
        contain data to write to file
    """

    #Initial all values to be no
    redcap_label['edenrollchart_dxinfluenza'] = 'No'
    redcap_label['edenrollchart_dxviralsyndrome'] = 'No'
    redcap_label['edenrollchart_dxpneumonia'] = 'No'
    redcap_label['edenrollchart_dxmyocardialinfarction'] = 'No'
    redcap_label['edenrollchart_dxstroke'] = 'No'

    redcap_raw['edenrollchart_dxinfluenza'] = '0'
    redcap_raw['edenrollchart_dxviralsyndrome'] = '0'
    redcap_raw['edenrollchart_dxpneumonia'] = '0'
    redcap_raw['edenrollchart_dxmyocardialinfarction'] = '0'
    redcap_raw['edenrollchart_dxstroke'] = '0'

    # Final Diagnoses
    diagnosis_count = 0
    diagnoses = ed.final_diagnoses(subject_id, conn)
    coordinator['Diagnoses'] = diagnoses
    for diagnosis in diagnoses:
        diagnosis_count += 1
        # Record Diagnosis Number
        redcap_label['edenrollchart_numberdx'] = diagnosis_count
        redcap_raw['edenrollchart_numberdx'] = diagnosis_count
        if diagnosis_count > 3:
            redcap_label['edenrollchart_numberdx'] = 'More than three'
            redcap_raw['edenrollchart_numberdx'] = '4'
            break
        redcap_label['edenrollchart_dx{}'.format(diagnosis_count)] = diagnosis[0]
        if diagnosis[0].lower().find('influenza') != -1:
            redcap_label['edenrollchart_dxinfluenza'] = 'Yes'
            redcap_raw['edenrollchart_dxinfluenza'] = '1'
        if diagnosis[0].lower().find('viral syndrome') != -1 or diagnosis[0].lower().find('viral infection') != -1:
            redcap_label['edenrollchart_dxviralsyndrome'] = 'Yes'
            redcap_raw['edenrollchart_dxviralsyndrome'] = '1'
        if diagnosis[0].lower().find('pneumonia') != -1:
            redcap_label['edenrollchart_dxpneumonia'] = 'Yes'
        if diagnosis[0].lower().find('myocardial infarction') != -1:
            redcap_label['edenrollchart_dxmyocardialinfarction'] = 'Yes'
            redcap_raw['edenrollchart_dxmyocardialinfarction'] = '1'
        if diagnosis[0].lower().find('stroke') != -1:
            redcap_label['edenrollchart_dxstroke'] = 'Yes'
            redcap_raw['edenrollchart_dxstroke'] = '1'

    return coordinator, redcap_label, redcap_raw
