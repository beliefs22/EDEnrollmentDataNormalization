import sqlite3
import csv
import os


def create_tables(conn):
    """Create database tables for each text file provided by Matt

    Args:
       conn (:obj: `database connection`): connection to the database to
           save the tables
    """
    cur = conn.cursor()
    #Get Text Files Matt Stored
    sep = os.sep
    datafilespath = os.getcwd() + sep + 'Linking_Log_For_Matt' + sep + 'Matt_Place_Text_Files_Here'
    current_files = os.listdir(datafilespath)
    current_files = [filename
                     for filename in current_files
                     if filename.endswith('.txt')
                     ]

    for filename in current_files:
        with open(datafilespath + sep + filename, 'r') as text_file:
            csvreader = csv.reader(text_file, delimiter='\t')
            table_fields = ",".join(next(csvreader))
            table_data = [row
                          for row in csvreader
                          ]
            # Create Table Statement
            table_title = filename.replace(".txt", "")
            drop_table_sql = """DROP TABLE IF EXISTS {}""".format(table_title)
            create_table_sql = """CREATE TABLE {} ({})""".format(
                table_title, table_fields)
            print("Creating table {}".format(table_title))
            cur.execute(drop_table_sql)
            cur.execute(create_table_sql)

            # Insert Values Statement
            for table_row in table_data:
                transform = "'{}'"
                data_as_text = ",".join([transform.format(item.replace("'", "").replace(",", ""))for item in table_row])
                insert_sql = """INSERT INTO {} VALUES ({})""".format(
                    table_title, data_as_text)
                cur.execute(insert_sql)
            # Commit the changes
            conn.commit()
            print("Done Creating table {}".format(table_title))

    #Create MedAdminName Table from Medication Table and MedicationAdmin tables
    medication_sql = 'SELECT DISTINCT MEDICATION_ID, MedIndexName, MedRoute, THERACLASS FROM Medication'
    cur.execute(medication_sql)
    medication_info = dict()
    medications = cur.fetchall()
    for medication in medications:
        med_id = medication[0]
        med_name = medication[1]
        med_route = medication[2]
        med_class = medication[3]
        if med_route!= "":
            medication_info[med_id] = {'name': med_name,
                                       'route': med_route,
                                       'class': med_class
                                       }

    medication_admin_sql = 'SELECT * FROM MEDADMINS'
    cur.execute(medication_admin_sql)
    medication_admins = cur.fetchall()
    medication_admins_with_name_and_route = list()
    for medication_admin in medication_admins:
        try:
            med_id = medication_admin[2]
            action_taken = medication_admin[4]
            med_dose = medication_admin[7]
            med_route = medication_info[med_id]['route']
            med_name = medication_info[med_id]['name']
            med_class = medication_info[med_id]['class']
            if med_name.lower().find('ampicillin-sulbactam') != -1 or med_name.lower().find('azithromycin') != -1:
                med_class = 'ANTIBIOTICS'
                med_route = 'IV'
            if med_name.lower().find('peramivir') != -1:
                med_class = 'ANTIVIRALS'
                med_route = 'IV'
        except KeyError:
            #Skip meds that don't have route information
            print(medication_admin)
            continue
        #add name, route , and class fields to medication_admin fields
        if action_taken not in ("Canceled Entry", "Missed", "Refused") and med_dose not in ("", "0"):
            medication_admin = list(medication_admin) + [med_name] + [med_route] + [med_class]
            medication_admins_with_name_and_route.append(medication_admin)

    medication_admin_name_table_fields = "studyid, order_med_id, medication_id, TimeActionTaken, ActionTaken, " \
                                   "MAR_ORIG_DUE_TM, SCHEDULED_TIME, Dose, AdminSite, INFUSION_RATE, InfusionRateUnit, " \
                                   "DurationToInfuse, Duration_Infuse_Unit, medindexname, medroute, theraclass"


    table_title = 'MedAdminName'
    drop_table_sql = """DROP TABLE IF EXISTS {}""".format(table_title)
    create_table_sql = """CREATE TABLE {} ({})""".format(
        table_title, medication_admin_name_table_fields)
    print("Creating table {}".format(table_title))
    cur.execute(drop_table_sql)
    cur.execute(create_table_sql)

    # Insert Values Statement
    for table_row in medication_admins_with_name_and_route:
        transform = "'{}'"
        data_as_text = ",".join([transform.format(item.replace("'", "").replace(",", "")) for item in table_row])
        insert_sql = """INSERT INTO {} VALUES ({})""".format(
            table_title, data_as_text)
        cur.execute(insert_sql)
    # Commit the changes
    conn.commit()
    print("Done Creating table {}".format(table_title))

    # Create Study IDs for Data Pull Table
    visit_log_path = os.getcwd() + sep + 'Linking_Log_For_Matt'
    with open(visit_log_path + sep + 'Prospective_Linking_Log.csv', 'r') as id_log:
        csvreader = csv.reader(id_log, delimiter=',')
        table_fields = ",".join(next(csvreader))
        table_data = [row
                      for row in csvreader
                      ]
        # Create Table Statement
        table_title = 'STUDY_IDS_TO_PULL'
        drop_table_sql = """DROP TABLE IF EXISTS {}""".format(table_title)
        create_table_sql = """CREATE TABLE {} ({})""".format(
            table_title, table_fields)
        print("Creating table {}".format(table_title))
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)

        # Insert Values Statement
        for table_row in table_data:
            transform = "'{}'"
            data_as_text = ",".join([transform.format(item.replace("'", "").replace(",", "")) for item in table_row])
            insert_sql = """INSERT INTO {} VALUES ({})""".format(
                table_title, data_as_text)
            cur.execute(insert_sql)
        # Commit the changes
        conn.commit()
        print("Done Creating table {}".format(table_title))
    print("Done Creating table {}".format(table_title))

def main():
    conn = sqlite3.connect(r'\\win.ad.jhu.edu\cloud\sddesktop$\CEIRS\CEIRS.db')
    create_tables(conn)

if __name__ == "__main__":
    main()
