import csv


def create_test_tables():
    medication_info = [['STUDY_ID', 'MEDICATION_ID', 'MedIndexName', 'MedRoute', 'THERACLASS'],
                       ['0001', '001', 'clindamycin', 'oral', 'antibiotic'],
                       ['0002', '002', 'tamiflu', 'oral', 'antiviral']
                       ]
    study_id_info = [['study_id', 'enrollment_date', 'mrn', 'data_pull_complete'],
                     ['0001', '01/01/2017', '00000001', 'no'],
                     ['0002', '02/02/2017', '00000002', 'no'],
                     ['0003', '03/03/2017', '00000003', 'no']
                     ]

    med_admin_info = [['study_id', 'med_id', 'action_taken', 'med_dose'],
                      ['0001', '001', 'given', '20mg'],
                      ['0002', '002', 'given', '200mg'],
                      ['0003', '001', 'given', '20mg'],
                      ['0003', '002', 'Missed', '20mg']
                      ]
    with open('EdMedication.txt', 'w') as fin:
        csv_writer = csv.writer(fin, delimiter='\t')
        for row in medication_info:
            csv_writer.writerow(row)

    with open('MEDADMINS.txt', 'w') as fin:
        csv_writer = csv.writer(fin, delimiter='\t')
        for row in med_admin_info:
            csv_writer.writerow(row)

    with open('study_ids_to_pull.csv', 'w') as fin:
        csv_writer = csv.writer(fin)
        for row in study_id_info:
            csv_writer.writerow(row)


def main():
    create_test_tables()


if __name__ == '__main__':
    main()
