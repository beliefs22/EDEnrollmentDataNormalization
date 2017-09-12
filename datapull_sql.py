import sqlite3
import csv
import os


def arrival_date_time(subject_id, conn):
    """Gets arrival date and time from the demographics table
    Args:
        subject_id (str): the id of the subject whose data you are searching for
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        date (str): subjects arrival date
        time (str): subjects arrival time
        arrival (str): used in ADT object to indicate the object is for an
            arrrival
        dispo (str): subjects final disposition
    """
    cur = conn.cursor()
    sql = """SELECT ADT_ARRIVAL_TIME, EDDisposition FROM DEMOGRAPHICS
          WHERE STUDYID = {}""".format(subject_id)
    cur.execute(sql)
    data = cur.fetchall()
    if data:
        date, time = data[0][0].split(" ")
        dispo = data[0][1]
    return date, time, 'arrival', dispo


def discharge_date_time(subject_id, conn):
    """Gets discharge date and time from the demographics table
    Args:
        subject_id (str): the id of the subject whose data you are searching for
        conn (:obj: `database connection`): connection to the database that
            contains the patient data

    Returns:
        date (str): subjects discharge date
        time (str): subjects discharge time
        arrival (str): used in ADT object to indicate the object is for an
            discharge
        dispo (str): subjects final disposition
    """
    cur = conn.cursor()
    sql = """SELECT ED_DEPARTURE_TIME, EDDisposition FROM DEMOGRAPHICS
          WHERE STUDYID = {}""".format(subject_id)
    cur.execute(sql)
    data = cur.fetchall()
    if data[0][0]:
        date, time = data[0][0].split(" ")
        dispo = data[0][1]
        return date, time, 'discharge', dispo
    else:
        sql = """SELECT HOSP_ADMSN_TIME, EDDisposition FROM DEMOGRAPHICS
          WHERE STUDYID = {}""".format(subject_id)
        cur.execute(sql)
        data = cur.fetchall()
        if data[0][0]:
            date, time = data[0][0].split(" ")
            dispo = data[0][1]
            return date, time, 'discharge', dispo


def vitals(subject_id, conn, flowsheet_name):
    """Gets a vitals sign value from the Flowsheets table

    Args:
        subject_id (str): id of subject
        conn: (:obj: `database connectoin`): connection to the database that
            contains the patient data
        flowsheet_name (str): vital type you are searching for: BP, Temp, etc

    Returns:
        :obj: `list` of :obj: `tuple`:
           returns a list of tuples of any vitals values found. Each tuple will
           have the following information
           name (str): name of the vital sign - BP, Temp, etc
           date_and_time (str): date and time vital sign was recorded
           value (str): value of the vital sign
           
    """
    cur = conn.cursor()
    sql = """SELECT FlowsheetDisplayName, RECORDED_TIME, FlowsheetValue
            FROM Flowsheets
            WHERE STUDYID = {}
            AND FlowsheetDisplayName = {}""".format(subject_id, flowsheet_name)
    
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found lab value")
##            print(subject_id, item)
    return data


def lab(subject_id, conn, labcompname):
    """Gets a lab value from the Lab table
    Args:
        subject_id (str): id of the subject
        conn: (:obj: `database connectoin`): connection to the database that
            contains the patient data
        labcomname (str): the lab component you are searching for: Hematocrit

    Returns:
        :obj: `list` of :obj: `tuple`:
           returns a list of tuples of any lab values found. Each tuple will
           have the following information
           lab_result (str): result of the lab
           date_and_time (str): date and time lab was collected
           lab_name (str): name of the lab - Complete Blood Count
           component_name (str): component tested - Hematocrit
    """

    cur = conn.cursor()
    sql = """SELECT ORD_VALUE, SPECIMN_TAKEN_TIME, RESULT_TIME, PROC_NAME, LabComponentName FROM LAB
          WHERE STUDYID = {}
          AND LabComponentName = {}""".format(subject_id,labcompname)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found lab value")
##            print(subject_id, item)
    return data


def lab2(subject_id, conn, labcompnames):
    """Gets a lab value from the lab table. Used when searchig for multiple lab
    types.
    Args:
        subject_id (str): id of the subject
        conn: (:obj: `database connectoin`): connection to the database that
            contains the patient data
        labcomname (str): the lab components you are searching for: PH, BUN

    Returns:
        :obj: `list` of :obj: `tuple`:
           returns a list of tuples of any lab values found. Each tuple will
           have the following information
           lab_result (str): result of the lab
           date_and_time (str): date and time lab was collected
           lab_name (str): name of the lab - Complete Blood Count
           component_name (str): component tested - Hematocrit
    """
           
    cur = conn.cursor()
    sql = """SELECT ORD_VALUE, SPECIMN_TAKEN_TIME, RESULT_TIME, PROC_NAME, LabComponentName FROM LAB
          WHERE STUDYID = {}
          AND ({})""".format(subject_id, labcompnames)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found lab value")
##            print(subject_id, item)
    return data


def lab3(subject_id, conn, searchtext):
    """Gets a lab value from the labs table. Used when searching for labs by a
    search phrase. For example, labs with CULT in their name.
    Args:
        subject_id (str): id of the subject
        conn: (:obj: `database connectoin`): connection to the database that
            contains the patient data
        searchtext (str): the text to use to search for: CULT

    Returns:
        :obj: `list` of :obj: `tuple`:
           returns a list of tuples of any lab values found. Each tuple will
           have the following information
           lab_result (str): result of the lab
           date_and_time (str): date and time lab was collected
           lab_name (str): name of the lab - Complete Blood Count
           component_name (str): component tested - Hematocrit
    """
    cur = conn.cursor()
    sql = """SELECT ORD_VALUE, SPECIMN_TAKEN_TIME, RESULT_TIME, PROC_Name, LabComponentName FROM LAB
          WHERE STUDYID = {}
          AND PROC_NAME LIKE {}""".format(subject_id, searchtext)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found lab value")
##            print(subject_id, item)
    return data


def medication(subject_id, conn, theraclass, orderingmode):
    """Gets medication information from the medication table
    Args:
        subject_id (str): the id of the subject
        conn: (:obj: `database connection`): connection to the database that
            contains the data
        theraclass (str): the class of the medication - ANTIVAL, ATIBIOTIC, etc
        orderingmode (str): discharge medication or ordered while in hospital

    Returns:
        :obj: `list` of :obj: `tuple`:
           returns a list of tuples of any medications found. Each tuple will
           have the following information
           name (str): medication name
           date_and_time (str): date and time lab was collected
           route (str): medication admin route - oral ,IV, IM
           theraclass (str): the class of the medication - ANTIVAL, ATIBIOTIC
               , etc
           orderingmode (str): tells if discharge medication or ordered while in
               hospital
    """
    cur = conn.cursor()
    sql = """SELECT MedIndexName, TimeOrdered, MedRoute, THERACLASS,
          OrderingMode FROM Medication
          WHERE STUDYID = {} AND THERACLASS = {}
          AND OrderingMode = {}""".format(
              subject_id,theraclass, orderingmode)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found medication")
##            print(subject_id, item)
    return data

def medication2(subject_id, conn, theraclass):
    """Gets medication information for meds givven in hospital from the medication table
    Args:
        subject_id (str): the id of the subject
        conn: (:obj: `database connection`): connection to the database that
            contains the data
        theraclass (str): the class of the medication - ANTIVAL, ATIBIOTIC, etc

    Returns:
        :obj: `list` of :obj: `tuple`:
           returns a list of tuples of any medications found. Each tuple will
           have the following information
           name (str): medication name
           date_and_time (str): date and time lab was collected
           route (str): medication admin route - oral ,IV, IM
    """
    cur = conn.cursor()
    sql = """SELECT MedIndexName, TimeActionTaken, MedRoute
          FROM MedAdminName
          WHERE STUDYID = {} AND THERACLASS = {}""".format(
              subject_id, theraclass)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found medication")
##            print(subject_id, item)
    return data


def chest_imaging(subject_id, conn):
    """Gets imaging information from the procedures table
    Args:
        subject_id (str): the id of the subject whose data you are searching for
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
    Returns:
        :obj: `list` of :obj: `tuples`:
        returns alist of tuples of any imaging found with the follwing data
        name (str): name of the imaging
        date_time (str): time imaging was ordered
        status (str): if imaging was completed or cancelled
    """

    cur = conn.cursor()
    sql = r"""SELECT PROC_NAME, ORDER_TIME, OrderStatus FROM Procedures
          WHERE STUDYID = {} AND (PROC_NAME LIKE '%CT%'
          OR PROC_NAME LIKE'%XR%')
          AND OrderStatus = 'Completed'""".format(subject_id)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found chest imaging")
##            print(subject_id, item)
    return data


def final_diagnoses(subject_id, conn):
    """Gets diagnosis information from the Diagnosis table
    Args:
        subject_id (str): the id of the subject whose data you are searching for
        conn (:obj: `database connection`): connection to the database that
            contains the patient data
    Returns:
        :obj: `list` of :obj: `tuples`:
        returns alist of tuples of any diagnosis found with the follwing data
        name (str): name of the diagnosis
    """

    cur = conn.cursor()
    sql = """SELECT EpicInternalDiagnosisName FROM Diagnosis
          WHERE STUDYID = {}""".format(subject_id)
    cur.execute(sql)
    data = cur.fetchall()
##    if data:
##        for item in data:
##            print("found diagnoses")
##            print(subject_id, item)
    return data


def main():
    conn = sqlite3.connect(r"\\win.ad.jhu.edu\cloud\sddesktop$\CEIRS\CEIRS.db")
    #Get subject IDs
    cur = conn.cursor()
    sql = """SELECT DISTINCT STUDYID FROM DEMOGRAPHICS"""
    cur.execute(sql)
    subject_ids = cur.fetchall()
    for subject_id in subject_ids:
        subject_id = "'{}'".format(subject_id[0])
##        print(arrival_date_time(subject_id, conn))
##        print(discharge_date_time(subject_id, conn))
##        print(lab(subject_id, conn, "'PH SPECIMEN'"))
##        print(medication(subject_id, conn, "'ANTIBIOTICS'","'Inpatient'"))
##        print(chest_imaging(subject_id, conn))
##        print(final_diagnoses(subject_id, conn))
        print(vitals(subject_id, conn, "'O2 Device'"), "o2 device")
        

    conn.close()

if __name__ == "__main__":
    main()
